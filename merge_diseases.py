# -*- coding: utf-8 -*-
import re
import time

def extract_diseases_from_file(filename, source_name):
    """
    从文件中只提取ul.ks-ill-list中的疾病名称
    """
    diseases = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 只提取ul.ks-ill-list中的疾病
        in_ul_section = False
        
        for line in lines:
            line = line.strip()
            
            # 检测是否进入ul部分
            if "从 ul.ks-ill-list 中爬取的疾病:" in line:
                in_ul_section = True
                continue
            
            # 如果遇到总计行，停止提取ul部分
            if "总计:" in line and in_ul_section:
                in_ul_section = False
                break
            
            # 在ul部分提取疾病名称
            if in_ul_section and line and not line.startswith('-') and not line.startswith('='):
                # 匹配格式: "  1. 疾病名称"
                if re.match(r'^\s*\d+\.\s+', line):
                    # 提取疾病名称（去掉序号）
                    disease = re.sub(r'^\s*\d+\.\s+', '', line)
                    if disease and len(disease) > 1:
                        diseases.append(disease)
                        print(f"  {source_name}: {disease}")
        
        print(f"从 {filename} 的ul部分提取到 {len(diseases)} 个疾病")
        return diseases
        
    except Exception as e:
        print(f"读取文件 {filename} 时出错: {e}")
        return []

def merge_diseases():
    """
    合并神经内科和神经外科的疾病名称
    """
    print("开始合并神经内科和神经外科疾病名称...")
    print("=" * 60)
    
    # 提取神经内科疾病
    print("1. 提取神经内科疾病:")
    neike_diseases = extract_diseases_from_file('precise_diseases.txt', '神经内科')
    
    # 提取神经外科疾病
    print("\n2. 提取神经外科疾病:")
    waike_diseases = extract_diseases_from_file('precise_diseases_waike.txt', '神经外科')
    
    # 合并所有疾病
    all_diseases = neike_diseases + waike_diseases
    
    # 找出重复的疾病（神经内科和神经外科之间的重复）
    disease_count = {}
    for disease in all_diseases:
        disease_count[disease] = disease_count.get(disease, 0) + 1
    
    # 找出重复的疾病名称
    duplicate_diseases = [disease for disease, count in disease_count.items() if count > 1]
    duplicate_diseases.sort()
    
    # 去重并排序
    unique_diseases = sorted(list(set(all_diseases)))
    
    # 保存到统一文件
    output_file = 'nsd_name.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("神经系统疾病名称统一列表\n")
        f.write("=" * 60 + "\n")
        f.write(f"合并时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据来源: 寻医问药网神经内科和神经外科页面\n")
        f.write("-" * 60 + "\n")
        f.write(f"神经内科疾病数: {len(neike_diseases)}\n")
        f.write(f"神经外科疾病数: {len(waike_diseases)}\n")
        f.write(f"合并前总数: {len(all_diseases)}\n")
        f.write(f"去重后总数: {len(unique_diseases)}\n")
        f.write(f"神经内科和神经外科之间的重复疾病数: {len(duplicate_diseases)}\n")
        f.write("-" * 60 + "\n")
        f.write("统一疾病名称列表:\n")
        f.write("-" * 60 + "\n")
        
        for i, disease in enumerate(unique_diseases, 1):
            f.write(f"{i:3d}. {disease}\n")
        
        # 在底部显示重复的疾病名称
        if duplicate_diseases:
            f.write("-" * 60 + "\n")
            f.write("神经内科和神经外科之间的重复疾病名称:\n")
            f.write("-" * 60 + "\n")
            for i, disease in enumerate(duplicate_diseases, 1):
                f.write(f"{i:3d}. {disease}\n")
        
        f.write("-" * 60 + "\n")
        f.write("合并完成！\n")
    
    print(f"\n合并完成！")
    print(f"神经内科疾病数: {len(neike_diseases)}")
    print(f"神经外科疾病数: {len(waike_diseases)}")
    print(f"合并前总数: {len(all_diseases)}")
    print(f"去重后总数: {len(unique_diseases)}")
    print(f"神经内科和神经外科之间的重复疾病数: {len(duplicate_diseases)}")
    print(f"结果已保存到: {output_file}")
    
    # 显示前20个疾病名称
    print(f"\n前20个疾病名称:")
    for i, disease in enumerate(unique_diseases[:20], 1):
        print(f"{i:2d}. {disease}")
    
    if len(unique_diseases) > 20:
        print(f"... 还有 {len(unique_diseases) - 20} 个疾病名称")
    
    # 显示重复的疾病名称
    if duplicate_diseases:
        print(f"\n神经内科和神经外科之间的重复疾病名称 ({len(duplicate_diseases)}个):")
        for i, disease in enumerate(duplicate_diseases, 1):
            print(f"{i:2d}. {disease}")
    else:
        print(f"\n✅ 神经内科和神经外科之间没有重复的疾病名称！")

if __name__ == "__main__":
    merge_diseases()
