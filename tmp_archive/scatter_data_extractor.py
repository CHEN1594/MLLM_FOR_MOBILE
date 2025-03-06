import json
import math
import os

# 目录路径
meta_data_dir = 'intermediate_data/cleaned_meta_data/scatter'
simvec_data_dir = 'intermediate_data/cleaned_simvec_data/scatter'
output_dir = 'intermediate_data/extracted_data/scatter'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 颜色相关的辅助函数
def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色转换为 (R,G,B) 元组格式"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(rgb1: tuple, rgb2: tuple) -> float:
    """计算两个 RGB 颜色之间的欧氏距离"""
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)))

# 允许的颜色容差范围
tolerance = 60

# 遍历元数据文件夹中的每一个 JSON 文件
for file_name in os.listdir(meta_data_dir):
    if not file_name.endswith('.json'):
        continue
    
    file_base_name = os.path.splitext(file_name)[0]
    
    # 读取 metadata JSON 文件
    meta_file_path = os.path.join(meta_data_dir, file_name)
    simvec_file_path = os.path.join(simvec_data_dir, file_name)
    output_file_path = os.path.join(output_dir, f"{file_base_name}.txt")
    
    print(f"\n正在处理文件: {file_name}")
    
    with open(meta_file_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # 读取 simvec JSON 文件
    with open(simvec_file_path, 'r', encoding='utf-8') as f:
        simvec_data = json.load(f)

    # 提取 X 轴和 Y 轴 (定量数据) 刻度
    x_ticks_labels = metadata['xAxis']['ticks']
    y_ticks_labels = metadata['yAxis']['ticks']
    
    x_ticks_values = [float(t) for t in x_ticks_labels]
    y_ticks_values = [float(t) for t in y_ticks_labels]

    # 计算 X 和 Y 轴的像素比例 (scale)
    x_max_value = x_ticks_values[-1]
    x_min_value = x_ticks_values[0]
    y_max_value = y_ticks_values[-1]
    y_min_value = y_ticks_values[0]

    x_max_label = x_ticks_labels[-1]
    x_min_label = x_ticks_labels[0]
    y_max_label = y_ticks_labels[-1]
    y_min_label = y_ticks_labels[0]

    # 获取 X 轴的最大和最小像素坐标
    x_max_pixel = next(
        int(text['position'][0]) 
        for text in simvec_data['text'] 
        if text['content'] == x_max_label
    )
    x_min_pixel = next(
        int(text['position'][0]) 
        for text in simvec_data['text'] 
        if text['content'] == x_min_label
    )

    # 获取 Y 轴的最大和最小像素坐标
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

    # 计算 X 和 Y 轴的 scale
    x_scale = (x_max_value - x_min_value) / (x_max_pixel - x_min_pixel)
    y_scale = (y_max_value - y_min_value) / (y_min_pixel - y_max_pixel)

    # 解析图例 (legend) 中颜色到类别的映射关系 (使用 RGB 格式)
    color_to_category = {}
    if 'legend' in metadata and isinstance(metadata['legend'], dict) and 'items' in metadata['legend'] and 'colors' in metadata['legend']:
        legend_items = metadata['legend']['items']
        legend_colors = [hex_to_rgb(color) for color in metadata['legend']['colors']]
        color_to_category = dict(zip(legend_colors, legend_items))
    else:
        print("没有找到 legend 数据，默认直接根据 RGB 颜色进行分类。")
        color_to_category = None

    # 解析每一个圆 (散点图) 的数据值
    scatter_data = []
    for circle in simvec_data['circle']:
        x_center = int(circle['position'][0])  # 圆心的 X 坐标
        y_center = int(circle['position'][1])  # 圆心的 Y 坐标
        circle_color = eval(circle['color'])   # 颜色转换为 RGB 元组

        # 计算实际的 X 和 Y 轴数据值
        x_value = x_min_value + (x_center - x_min_pixel) * x_scale
        y_value = y_max_value - (y_center - y_max_pixel) * y_scale
        x_value = round(x_value, 2)
        y_value = round(y_value, 2)

        # 确定圆的分类 (category)
        if color_to_category:
            category = f"RGB{circle_color}"  # 默认分类为自身颜色表示
            min_distance = float('inf')
            
            for legend_color, legend_category in color_to_category.items():
                distance = color_distance(circle_color, legend_color)
                if distance < min_distance:
                    min_distance = distance
                    # 仅在距离小于容差时才更新为图例中的类别
                    if distance <= tolerance:
                        category = legend_category
        else:
            category = f"RGB{circle_color}"

        scatter_data.append({"x": x_value, "y": y_value, "category": category})

    # 输出计算结果到文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(f"计算出的散点图数据 ({file_name}):\n")
        for point in scatter_data:
            output_file.write(json.dumps(point, ensure_ascii=False) + ",\n")
    
    print(f"已保存到: {output_file_path}")
