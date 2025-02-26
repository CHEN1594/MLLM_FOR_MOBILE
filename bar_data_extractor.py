import json
import math
import os

# 目录路径
meta_data_dir = 'intermediate_data/cleaned_meta_data/bar'
simvec_data_dir = 'intermediate_data/cleaned_simvec_data/bar'
output_dir = 'intermediate_data/extracted_data/bar'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 7. 将十六进制颜色转换为 RGB 格式
def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色转换为 (R,G,B) 元组格式"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# 8. 计算颜色的欧氏距离
def color_distance(rgb1: tuple, rgb2: tuple) -> float:
    """计算两个 RGB 颜色之间的欧氏距离"""
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)))

# 遍历元数据文件夹中的每一个 JSON 文件
for file_name in os.listdir(meta_data_dir):
    if not file_name.endswith('.json'):
        continue
    
    file_base_name = os.path.splitext(file_name)[0]
    
    # 1. 读取 metadata JSON 文件
    meta_file_path = os.path.join(meta_data_dir, file_name)
    simvec_file_path = os.path.join(simvec_data_dir, file_name)
    output_file_path = os.path.join(output_dir, f"{file_base_name}.txt")
    
    print(f"\n正在处理文件: {file_name}")
    
    with open(meta_file_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # 2. 读取 simvec JSON 文件
    with open(simvec_file_path, 'r', encoding='utf-8') as f:
        simvec_data = json.load(f)

    # 3. 提取 X 轴 (分类数据) 和 Y 轴 (定量数据) 刻度
    x_ticks = metadata['xAxis']['ticks']
    y_ticks_labels = metadata['yAxis']['ticks']

    # 4. 计算 Y 轴的像素比例 (scale)
    y_max_value = int(y_ticks_labels[-1])  # Y 轴数据的最大值
    y_min_value = int(y_ticks_labels[0])   # Y 轴数据的最小值

    y_max_label = y_ticks_labels[-1]  # 最大值的原始标签
    y_min_label = y_ticks_labels[0]   # 最小值的原始标签

    # 5. 获取 Y 轴的最大和最小像素坐标
    y_max_pixel = next(
        int(text['position'][1]) 
        for text in simvec_data['text'] 
        if text['content'] == y_max_label
    )

    y_min_pixel = next(
        int(text['position'][1]) 
        for text in simvec_data['text'] 
        if text['content'] == y_min_label
    )

    # 计算 Y 轴的 scale
    y_scale = (y_max_value - y_min_value) / (y_min_pixel - y_max_pixel)

    # 6. 提取 X 轴刻度和像素坐标的映射关系
    x_label_positions = {
        text['content']: int(text['position'][0])
        for text in simvec_data['text']
        if text['content'] in x_ticks
    }

    # 9. 解析图例 (legend) 中颜色到类别的映射关系 (使用 RGB 格式)
    color_to_category = {}
    tolerance = 60  # 允许的颜色容差范围

    if 'legend' in metadata and isinstance(metadata['legend'], dict) and 'items' in metadata['legend'] and 'colors' in metadata['legend']:
        legend_items = metadata['legend']['items']
        legend_colors = [hex_to_rgb(color) for color in metadata['legend']['colors']]
        color_to_category = dict(zip(legend_colors, legend_items))
    else:
        print("没有找到 legend 数据，默认直接根据 RGB 颜色进行分类。")
        color_to_category = None  # 标记为无图例模式

    # 10. 解析每一个矩形（柱状图）的数据值
    bar_data = []
    for rect in simvec_data['rect']:
        x_center = int(rect['position'][0])  # 矩形顶部中点的 X 坐标
        y_top = int(rect['position'][1])     # 矩形顶部边缘的 Y 坐标
        rect_color = eval(rect['color'])     # 矩形的填充颜色 (转换为 RGB 元组)

        # 计算 X 轴分类（找到最接近的 x_tick）
        closest_x = min(
            [(abs(x_center - pos), label) for label, pos in x_label_positions.items()],
            key=lambda x: x[0]
        )[1]

        # 计算 Y 轴数据值
        y_value = y_max_value - (y_top - y_max_pixel) * y_scale
        y_value = round(y_value, 1)

        # 确定矩形的分类 (category)
        if color_to_category:
            category = "Unknown"
            min_distance = float('inf')
            
            for legend_color, legend_category in color_to_category.items():
                distance = color_distance(rect_color, legend_color)
                if distance < min_distance and distance <= tolerance:
                    min_distance = distance
                    category = legend_category
        else:
            category = f"RGB{rect_color}"

        bar_data.append({"x": closest_x, "y": y_value, "category": category})

    # 11. 输出计算结果到文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(f"计算出的柱状图数据 ({file_name}):\n")
        for bar in bar_data:
            output_file.write(json.dumps(bar, ensure_ascii=False) + ",\n")
    
    print(f"已保存到: {output_file_path}")
