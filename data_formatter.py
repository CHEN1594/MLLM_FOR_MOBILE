import json
import os

# 输入和输出路径
input_simvec_directory = "intermediate_data/raw_simvec_data"
output_simvec_directory = "intermediate_data/cleaned_simvec_data"

input_metadata_directory = "intermediate_data/raw_meta_data"
output_metadata_directory = "intermediate_data/cleaned_meta_data"

# 确保输出目录存在
os.makedirs(output_simvec_directory, exist_ok=True)
os.makedirs(output_metadata_directory, exist_ok=True)

# 支持的图表类型 (文件夹名称)
chart_types = ["bar", "scatter", "pie"]

# 规范化文本内容的函数
def normalize_text_content(text: str) -> str:
    """规范化文本内容"""
    return text.replace(' ', '_').replace('\u2212', '-').replace(',', '')

# 1. 处理 SimVec 文件
for chart_type in chart_types:
    input_chart_path = os.path.join(input_simvec_directory, chart_type)
    output_chart_path = os.path.join(output_simvec_directory, chart_type)

    # 确保输出子目录存在
    os.makedirs(output_chart_path, exist_ok=True)

    for filename in os.listdir(input_chart_path):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_chart_path, filename)
            output_path = os.path.join(output_chart_path, filename.replace(".txt", ".json"))

            data = {
                "rect": [],
                "text": [],
                "circle": [],
                "line": [],
                "area": []  # 新增 area 类型
            }

            with open(input_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    
                    if line.startswith("rect "):
                        _, color, position_str = line.split(" ", 2)
                        position = json.loads(position_str.replace('[', '[').replace(']', ']'))
                        if color == "None":
                            continue
                        data["rect"].append({
                            "color": color,
                            "position": position
                        })

                    elif line.startswith("text "):
                        _, content, position_str = line.split(" ", 2)
                        content = normalize_text_content(content)
                        position = json.loads(position_str.replace('[', '[').replace(']', ']'))
                        data["text"].append({
                            "content": content,
                            "position": position
                        })

                    elif line.startswith("circle "):
                        _, color, position_str = line.split(" ", 2)
                        position = json.loads(position_str.replace('[', '[').replace(']', ']'))
                        data["circle"].append({
                            "color": color,
                            "position": position
                        })

                    elif line.startswith("line "):
                        _, color, points_str = line.split(" ", 2)
                        points = [[int(p.split(',')[0]), int(p.split(',')[1])] for p in points_str.split(';')]
                        data["line"].append({
                            "color": color,
                            "points": points
                        })

                    elif line.startswith("area "):  # 新增的 area 类型处理
                        _, color, points_str = line.split(" ", 2)
                        points = [[int(p.split(',')[0]), int(p.split(',')[1])] for p in points_str.split(';')]
                        data["area"].append({
                            "color": color,
                            "points": points
                        })

            with open(output_path, "w", encoding="utf-8") as f_out:
                json.dump(data, f_out, indent=2)

            print(f"SimVec 转换完成: {output_path}")

# 2. 处理 Metadata 文件
for chart_type in chart_types:
    input_chart_path = os.path.join(input_metadata_directory, chart_type)
    output_chart_path = os.path.join(output_metadata_directory, chart_type)

    os.makedirs(output_chart_path, exist_ok=True)

    for filename in os.listdir(input_chart_path):
        if filename.endswith(".json"):
            input_path = os.path.join(input_chart_path, filename)
            output_path = os.path.join(output_chart_path, filename)

            with open(input_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # 处理 X 轴文本
            if (
                "xAxis" in metadata 
                and metadata["xAxis"] is not None 
                and "ticks" in metadata["xAxis"] 
                and metadata["xAxis"]["ticks"] is not None
            ):
                metadata["xAxis"]["ticks"] = [
                    normalize_text_content(tick) for tick in metadata["xAxis"]["ticks"]
                ]

            # 处理 Y 轴文本
            if (
                "yAxis" in metadata 
                and metadata["yAxis"] is not None 
                and "ticks" in metadata["yAxis"] 
                and metadata["yAxis"]["ticks"] is not None
            ):
                metadata["yAxis"]["ticks"] = [
                    normalize_text_content(tick) for tick in metadata["yAxis"]["ticks"]
                ]

            # 处理图例 (legend) 中的文本
            if "legend" in metadata and isinstance(metadata["legend"], dict) and "items" in metadata["legend"]:
                metadata["legend"]["items"] = [
                    normalize_text_content(item) for item in metadata["legend"]["items"]
                ]

            with open(output_path, "w", encoding="utf-8") as f_out:
                json.dump(metadata, f_out, indent=2)

            print(f"Metadata 处理完成: {output_path}")
