import json
import math
import os

# 目录路径
meta_data_dir = 'intermediate_data/cleaned_meta_data/pie'
simvec_data_dir = 'intermediate_data/cleaned_simvec_data/pie'
output_dir = 'intermediate_data/extracted_data/pie'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 将十六进制颜色转换为 RGB 格式
def hex_to_rgb(hex_color: str) -> tuple:
    """将十六进制颜色转换为 (R,G,B) 元组格式"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# 计算颜色的欧氏距离
def color_distance(rgb1: tuple, rgb2: tuple) -> float:
    """计算两个 RGB 颜色之间的欧氏距离"""
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)))

# 计算两个点之间的角度 (以圆心为基准)
def calculate_angle(center: tuple, point: tuple) -> float:
    """计算从圆心到某点的角度 (0-360 度)"""
    dx, dy = point[0] - center[0], point[1] - center[1]
    angle = math.degrees(math.atan2(dy, dx))
    return angle % 360

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

    # 解析图例 (legend) 中颜色到类别的映射关系 (使用 RGB 格式)
    color_to_category = {}
    tolerance = 60  # 允许的颜色容差范围

    if 'legend' in metadata and isinstance(metadata['legend'], dict) and 'items' in metadata['legend'] and 'colors' in metadata['legend']:
        legend_items = metadata['legend']['items']
        legend_colors = [hex_to_rgb(color) for color in metadata['legend']['colors']]
        color_to_category = dict(zip(legend_colors, legend_items))
    else:
        print("没有找到 legend 数据，默认直接根据 RGB 颜色进行分类。")
        color_to_category = None  # 标记为无图例模式

    # 解析饼图数据
    pie_data = []

    # 寻找圆心 (出现在所有区域中的点)
    all_points = [tuple(p) for area in simvec_data['area'] for p in area['points']]
    center = max(set(all_points), key=all_points.count)
    print(f"检测到的圆心: {center}")

    # 计算每个区域的角度和类别
    for area in simvec_data['area']:
        area_color = eval(area['color'])
        points = [tuple(p) for p in area['points'] if tuple(p) != center]

        if len(points) < 2:
            print(f"区域 {area} 的点数不足，跳过")
            continue

        # 计算区域起始和结束角度
        start_angle = calculate_angle(center, points[0])
        end_angle = calculate_angle(center, points[1])

        # 计算区域的占比 (圆心角度 / 360)
        angle_diff = (end_angle - start_angle) % 360
        percentage = round(angle_diff / 360, 4)

        # 确定区域的分类 (category)
        if color_to_category:
            category = f"RGB{area_color}"
            min_distance = float('inf')
            
            for legend_color, legend_category in color_to_category.items():
                distance = color_distance(area_color, legend_color)
                if distance < min_distance and distance <= tolerance:
                    min_distance = distance
                    category = legend_category
        else:
            category = f"RGB{area_color}"

        pie_data.append({"category": category, "percentage": percentage})

    # 输出计算结果到文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(f"计算出的饼图数据 ({file_name}):\n")
        for pie in pie_data:
            output_file.write(json.dumps(pie, ensure_ascii=False) + ",\n")
    
    print(f"已保存到: {output_file_path}")
