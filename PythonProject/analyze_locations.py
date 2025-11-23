import os
import pandas as pd

# 1. 设置文件夹路径
folder_path = r"C:\Users\Yang\Desktop\semester1\CHC5904-周二下午\assignment2\rulinwaishi"

# 2. 定义地点及其“别名”
target_locations = {
    "南京": ["南京", "金陵", "秦淮"],
    "苏州": ["苏州", "姑苏", "吴门"],
    "杭州": ["杭州", "西湖", "武林", "钱塘"],
    "北京": ["北京", "京师", "京", "长安", "都门", "帝京"],
    "扬州": ["扬州", "维扬", "广陵"],
    "济南": ["济南", "山东", "大明湖", "历下"],
    "湖州": ["湖州", "吴兴"]
}

# 用来存放结果
summary_data = []
context_data = []

# 3. 开始分析
print("开始处理文件 (扩大上下文范围)...")

try:
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
except FileNotFoundError:
    print(f"错误：找不到路径 {folder_path}")
    files = []

# 准备容器
file_location_counts = []

for filename in files:
    file_path = os.path.join(folder_path, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"正在分析: {filename} ...")

        for std_loc, aliases in target_locations.items():
            total_count = 0
            for alias in aliases:
                # A. 统计次数
                count = content.count(alias)
                total_count += count

                # B. 提取上下文 (改进：提取前后 250 字，共 500 字)
                if count > 0:
                    start_index = 0
                    while True:
                        index = content.find(alias, start_index)
                        if index == -1:
                            break

                        # 这里改成了 250，保证句子完整
                        snippet_start = max(0, index - 250)
                        snippet_end = min(len(content), index + 350)
                        snippet = content[snippet_start:snippet_end].replace('\n', ' ')

                        context_data.append({
                            "文件名": filename,
                            "地点": std_loc,
                            "原文关键词": alias,
                            "原文摘录": f"...{snippet}..."
                        })
                        start_index = index + 1

            file_location_counts.append({
                "文件名": filename,
                "地点": std_loc,
                "出现次数": total_count
            })

    except Exception as e:
        print(f"读取错误 {filename}: {e}")

# 4. 导出结果
df_all = pd.DataFrame(file_location_counts)
df_context = pd.DataFrame(context_data)
df_summary = df_all.groupby("地点")["出现次数"].sum().reset_index()

output_path = os.path.join(folder_path, "分析结果.xlsx")

with pd.ExcelWriter(output_path) as writer:
    df_summary.to_excel(writer, sheet_name='频率统计', index=False)
    df_context.to_excel(writer, sheet_name='原文摘录', index=False)
    df_all.to_excel(writer, sheet_name='详细明细', index=False)

print("-" * 30)
print(f"成功！已重新生成: {output_path}")
print("现在的原文摘录应该非常长，足够您做 PPT 截图了。")