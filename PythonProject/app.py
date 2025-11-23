import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. 页面设置 (Page Config) ---
st.set_page_config(
    page_title="儒林外史 - 数字人文分析",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🗺️ 《儒林外史》空间叙事分析")
st.markdown("CHC5904 Assignment 2 - Option 2: Spatial Analysis of 'The Scholars'")

# --- 2. 定义文件路径 ---
# 请确保这个路径是正确的
excel_file = r"C:\Users\Yang\Desktop\semester1\CHC5904-周二下午\assignment2\rulinwaishi\分析结果.xlsx"

# --- 3. 定义地点的经纬度 ---
coordinates = {
    "南京": {"lat": 32.0603, "lon": 118.7969},
    "苏州": {"lat": 31.2989, "lon": 120.5853},
    "杭州": {"lat": 30.2741, "lon": 120.1551},
    "北京": {"lat": 39.9042, "lon": 116.4074},
    "扬州": {"lat": 32.3942, "lon": 119.4129},
    "济南": {"lat": 36.6512, "lon": 117.1201},
    "湖州": {"lat": 30.8943, "lon": 120.0868}
}


# --- 4. 加载数据函数 ---
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return None, None
    df_freq = pd.read_excel(file_path, sheet_name='频率统计')
    df_context = pd.read_excel(file_path, sheet_name='原文摘录')
    return df_freq, df_context


# --- 5. 主程序逻辑 ---
df_freq, df_context = load_data(excel_file)

if df_freq is None:
    st.error(f"错误：找不到文件 {excel_file}。请确认路径正确。")
else:
    # --- 数据预处理 ---
    total_counts = df_freq.groupby("地点")["出现次数"].sum().reset_index()
    total_counts["lat"] = total_counts["地点"].apply(lambda x: coordinates.get(x, {}).get("lat"))
    total_counts["lon"] = total_counts["地点"].apply(lambda x: coordinates.get(x, {}).get("lon"))

    # ==========================================
    # 🌟 新增功能：侧边栏筛选器 (Interactive Filter)
    # ==========================================
    st.sidebar.header("🔍 筛选控制台 (Filter)")

    # 获取所有城市列表
    all_cities = list(total_counts['地点'].unique())

    # 创建多选框，默认全选
    selected_cities = st.sidebar.multiselect(
        "请勾选要查看的城市：",
        options=all_cities,
        default=all_cities
    )

    # 根据用户的选择过滤数据
    if not selected_cities:
        st.warning("请至少选择一个城市。")
        filtered_data = total_counts
        filtered_context = df_context
    else:
        filtered_data = total_counts[total_counts['地点'].isin(selected_cities)]
        filtered_context = df_context[df_context['地点'].isin(selected_cities)]

    # ==========================================
    # 📊 第一部分：数据概览 (Data Overview)
    # ==========================================
    st.markdown("### 1. 数据统计概览")

    # 调整列宽比例，让布局更紧凑
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("**频率统计表**")
        # 使用 st.dataframe 并设置高度，使其与右侧图表尽量对齐
        st.dataframe(
            filtered_data[['地点', '出现次数']].sort_values(by='出现次数', ascending=False),
            use_container_width=True,
            hide_index=True,
            height=350  # 固定高度
        )

    with col2:
        st.markdown("**各地点出现频次对比**")
        # 改进配色：使用 'Reds' 单色渐变，更专业
        fig_bar = px.bar(
            filtered_data.sort_values(by='出现次数', ascending=True),  # 排序让图表更好看
            x='出现次数',
            y='地点',
            orientation='h',  # 改成横向柱状图，更容易对齐
            color='出现次数',
            color_continuous_scale='Reds',  # 🌟 修改配色：红色系
            text_auto=True
        )
        # 设置图表布局，去除多余边距
        fig_bar.update_layout(
            height=350,  # 与表格高度保持一致
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="",
            yaxis_title=""
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================
    # 🗺️ 第二部分：GIS 地图 (Map Visualization)
    # ==========================================
    st.markdown("---")
    st.markdown("### 2. GIS 空间热力图")
    st.caption("地图气泡大小与颜色深浅代表该地点在文本中出现的频率。")

    # 使用 Plotly Mapbox
    fig_map = px.scatter_mapbox(
        filtered_data,
        lat="lat",
        lon="lon",
        hover_name="地点",
        hover_data={"出现次数": True, "lat": False, "lon": False},
        size="出现次数",
        color="出现次数",
        # 🌟 修改配色：使用 'Reds' 或 'OrRd' (橙红)，看起来像热力图
        color_continuous_scale='Reds',
        size_max=40,
        zoom=4.5,
        center={"lat": 33.0, "lon": 118.0},
        mapbox_style="carto-positron",  # 🌟 修改底图风格：更简洁干净的底图
    )

    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=500)
    st.plotly_chart(fig_map, use_container_width=True)

    # ==========================================
    # 📄 第三部分：文本细读 (Close Reading)
    # ==========================================
    st.markdown("---")
    st.markdown("### 3. 文本细读辅助 (Context Explorer)")

    # 这里直接复用上面的筛选结果，不需要再次选择
    st.info(f"当前显示城市：{', '.join(selected_cities)}")

    for city in selected_cities:
        city_data = filtered_context[filtered_context["地点"] == city]
        if not city_data.empty:
            with st.expander(f"📖 查看【{city}】的相关原文 ({len(city_data)} 条)"):
                for idx, row in city_data.iterrows():
                    st.markdown(f"**[{row['文件名']}]**: ...{row['原文摘录']}...")