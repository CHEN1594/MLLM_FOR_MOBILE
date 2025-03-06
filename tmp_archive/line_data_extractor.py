import json
import math
import os

# 目录路径
meta_data_dir = 'intermediate_data/cleaned_meta_data/line'
simvec_data_dir = 'intermediate_data/cleaned_simvec_data/line'
output_dir = 'intermediate_data/extracted_data/line'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 颜色处理函数
def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色转换为 (R, G, B) 元组格式"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(rgb1: tuple, rgb2: tuple) -> float:
    """计算两个 RGB 颜色之间的欧氏距离"""
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)))

# 遍历 `metadata` 目录中的每一个 JSON 文件
for file_name in os.listdir(meta_data_dir):
    if not file_name.endswith('.json'):
        continue

    file_base_name = os.path.splitext(file_name)[0]

    # 文件路径
    meta_file_path = os.path.join(meta_data_dir, file_name)
    simvec_file_path = os.path.join(simvec_data_dir, file_name)
    output_file_path = os.path.join(output_dir, f"{file_base_name}.txt")

    print(f"\n正在处理文件: {file_name}")

    # 1. 读取 `metadata`
    with open(meta_file_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # 2. 读取 `simvec`
    with open(simvec_file_path, 'r', encoding='utf-8') as f:
        simvec_data = json.load(f)

    # 3. 提取 `X 轴` 和 `Y 轴` 刻度，并计算 `scale`
    x_ticks = metadata['xAxis']['ticks']
    y_ticks = metadata['yAxis']['ticks']

    # 计算 `X 轴` 像素与数值的缩放比例
    x_positions = {text['content']: text['position'][0] for text in simvec_data['text'] if text['content'] in x_ticks}
    x_min_pixel = min(x_positions.values())
    x_max_pixel = max(x_positions.values())

    x_min_value = float(x_ticks[0])
    x_max_value = float(x_ticks[-1])

    x_scale = (x_max_value - x_min_value) / (x_max_pixel - x_min_pixel)

    # 计算 `Y 轴` 像素与数值的缩放比例
    y_positions = {text['content']: text['position'][1] for text in simvec_data['text'] if text['content'] in y_ticks}
    y_min_pixel = min(y_positions.values())  # 低 y 坐标代表高数值
    y_max_pixel = max(y_positions.values())  # 高 y 坐标代表低数值

    y_min_value = float(y_ticks[0])
    y_max_value = float(y_ticks[-1])

    y_scale = (y_max_value - y_min_value) / (y_min_pixel - y_max_pixel)

    # 4. 解析 `legend` (颜色分类)
    color_to_category = {}
    tolerance = 60  # 颜色匹配的容差

    if 'legend' in metadata and isinstance(metadata['legend'], dict) and 'items' in metadata['legend'] and 'colors' in metadata['legend']:
        legend_items = metadata['legend']['items']
        legend_colors = [hex_to_rgb(color) for color in metadata['legend']['colors']]
        color_to_category = dict(zip(legend_colors, legend_items))
    else:
        print("⚠️ 没有 `legend` 数据，默认使用 RGB 颜色作为分类。")
        color_to_category = None  # 无图例模式

    # 5. 解析 `line` 数据
    line_data = []
    for line in simvec_data['line']:
        line_color = eval(line['color'])  # 解析 RGB 颜色
        points = line['points']

        # 确定类别 (category)
        if color_to_category:
            category = "Unknown"
            min_distance = float('inf')

            for legend_color, legend_category in color_to_category.items():
                distance = color_distance(line_color, legend_color)
                if distance < min_distance and distance <= tolerance:
                    min_distance = distance
                    category = legend_category
        else:
            category = f"RGB{line_color}"

        # 计算标准化坐标 (X, Y)
        for x_pixel, y_pixel in points:
            x_value = x_min_value + (x_pixel - x_min_pixel) * x_scale
            y_value = y_max_value - (y_pixel - y_max_pixel) * y_scale  # 由于像素坐标向下为正，需要反转 Y 轴

            line_data.append({"x": round(x_value, 2), "y": round(y_value, 2), "category": category})

    # 6. 输出到文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(f"计算出的折线图数据 ({file_name}):\n")
        for line in line_data:
            output_file.write(json.dumps(line, ensure_ascii=False) + ",\n")

    print(f" 结果已保存至: {output_file_path}")
