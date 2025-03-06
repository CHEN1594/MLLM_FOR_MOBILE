import json
import os
import re

# 输入路径
input_simvec_directory = "intermediate_data/raw_simvec"
metadata_directory = "intermediate_data/metadata"

# 输出路径
output_simvec_directory = "intermediate_data/cleaned_simvec"
output_metadata_directory = "output_json_file/metadata"

os.makedirs(output_simvec_directory, exist_ok=True)
os.makedirs(output_metadata_directory, exist_ok=True)

# 文本清理函数,用于匹配
def normalize_text_content(text: str) -> str:
    text = text.replace(" ", "_").replace("\u2212", "-").replace(",", "")
    text = re.sub(r"[^\w.-]", "", text)  
    return text.lower()  

# Step 1: 处理 SimVec 文件（从文本转换为 JSON）
for filename in os.listdir(input_simvec_directory):
    if not filename.endswith(".txt"):
        continue

    input_path = os.path.join(input_simvec_directory, filename)
    output_path = os.path.join(output_simvec_directory, filename.replace(".txt", ".json"))

    data = {"rect": [], "text": [], "circle": [], "line": [], "area": []}  # 初始化数据结构

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

        for line in lines:
            line = line.strip()

            if line.startswith("rect "):
                _, color, position_str = line.split(" ", 2)
                position = json.loads(position_str)
                if color != "None":
                    data["rect"].append({"color": color, "position": position})

            elif line.startswith("text "):
                _, content, position_str = line.split(" ", 2)
                normalized_content = normalize_text_content(content)
                position = json.loads(position_str)
                data["text"].append({"content": normalized_content, "position": position})

            elif line.startswith("circle "):
                _, color, position_str = line.split(" ", 2)
                position = json.loads(position_str)
                data["circle"].append({"color": color, "position": position})

            elif line.startswith("line "):
                _, color, points_str = line.split(" ", 2)
                points = []
                for p in points_str.split(';'):
                    coords = p.split(',')
                    if len(coords) < 2 or coords[0] == "NaN" or coords[1] == "NaN":
                        continue  # 过滤掉 NaN 值
                    try:
                        points.append([int(coords[0]), int(coords[1])])
                    except ValueError:
                        print(f"警告：无法解析点 {p}，已跳过")
                        continue

                if points:
                    data["line"].append({"color": color, "points": points})

            elif line.startswith("area "):
                _, color, points_str = line.split(" ", 2)
                points = []
                for p in points_str.split(';'):
                    coords = p.split(',')
                    if len(coords) < 2 or coords[0] == "NaN" or coords[1] == "NaN":
                        continue
                    try:
                        points.append([int(coords[0]), int(coords[1])])
                    except ValueError:
                        print(f"警告：无法解析点 {p}，已跳过")
                        continue

                if points:
                    data["area"].append({"color": color, "points": points})

    with open(output_path, "w", encoding="utf-8") as f_out:
        json.dump(data, f_out, indent=2)

    print(f"SimVec 转换完成: {output_path}")

# Step 2: 补全 Metadata 文件（填补 "wait" 字段）
for filename in os.listdir(metadata_directory):
    if not filename.endswith(".json"):
        continue

    metadata_path = os.path.join(metadata_directory, filename)
    simvec_path = os.path.join(output_simvec_directory, filename)

    if not os.path.exists(simvec_path):
        print(f"跳过 {filename}，因为找不到对应的 SimVec 文件")
        continue

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    with open(simvec_path, "r", encoding="utf-8") as f:
        simvec_data = json.load(f)

    # 补全 tick 
    for axis in ["x", "y"]:
        if axis in metadata and "tick" in metadata[axis] and metadata[axis]["tick"]:
            for tick in metadata[axis]["tick"]:
                normalized_tick_content = normalize_text_content(tick["content"])
                tick["position"] = {"x": "wait", "y": "wait"}  # 先填充默认值
                
                # 在 simvec_data["text"] 中寻找匹配的文本
                for text_item in simvec_data["text"]:
                    if normalized_tick_content == text_item["content"]:
                        tick["position"] = {
                            "x": text_item["position"][0],
                            "y": text_item["position"][1]
                        }
                        break

    # 补全 range
    for axis in ["x", "y"]:
        if axis in metadata and "range" in metadata[axis]:
            metadata[axis]["range"]["begin"] = "wait"
            metadata[axis]["range"]["end"] = "wait"

            tick_positions = [tick["position"]["x"] if axis == "x" else tick["position"]["y"] for tick in metadata[axis]["tick"]]
            tick_positions = [p for p in tick_positions if p != "wait"]  # 过滤掉未填充的
            if tick_positions:
                metadata[axis]["range"]["begin"] = min(tick_positions)
                metadata[axis]["range"]["end"] = max(tick_positions)

    # 补全 fixed_distance
    for axis in ["x", "y"]:
        if axis in metadata and "fixed_distance" in metadata[axis]:
            metadata[axis]["fixed_distance"] = "wait"
            tick_positions = sorted([tick["position"]["x"] if axis == "x" else tick["position"]["y"] for tick in metadata[axis]["tick"] if tick["position"]["x"] != "wait"])

            if len(tick_positions) > 1:
                distances = [tick_positions[i+1] - tick_positions[i] for i in range(len(tick_positions)-1)]
                if distances:
                    metadata[axis]["fixed_distance"] = sum(distances) / len(distances)  # 取平均

    # 保存
    output_metadata_path = os.path.join(output_metadata_directory, filename)
    with open(output_metadata_path, "w", encoding="utf-8") as f_out:
        json.dump(metadata, f_out, indent=2)

    print(f"Metadata 更新完成: {output_metadata_path}")
