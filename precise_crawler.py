# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import re

def crawl_diseases_from_ul():
    """
    从 <ul class="ks-ill-list clearfix mt10"> 中爬取疾病信息
    """
    print("开始从 ul.ks-ill-list 爬取疾病信息...")
    
    url = "https://jib.xywy.com/html/shenjingneike.html"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'gbk'
        print(f"请求成功，状态码: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有 ul.ks-ill-list 元素
        ul_elements = soup.find_all('ul', class_='ks-ill-list clearfix mt10')
        print(f"找到 {len(ul_elements)} 个 ul.ks-ill-list 元素")
        
        diseases_from_ul = []
        
        for i, ul in enumerate(ul_elements):
            print(f"处理第 {i+1} 个 ul 元素...")
            # 查找 ul 中的所有 li 元素
            li_elements = ul.find_all('li')
            print(f"  找到 {len(li_elements)} 个 li 元素")
            
            for li in li_elements:
                # 查找 li 中的链接
                links = li.find_all('a')
                for link in links:
                    disease_name = link.get_text().strip()
                    if disease_name and len(disease_name) > 1:
                        diseases_from_ul.append(disease_name)
                        print(f"    找到疾病: {disease_name}")
        
        # 去重并排序
        unique_diseases = sorted(list(set(diseases_from_ul)))
        print(f"去重前: {len(diseases_from_ul)} 个疾病")
        print(f"去重后: {len(unique_diseases)} 个疾病")
        
        return unique_diseases
        
    except Exception as e:
        print(f"爬取 ul 元素时出错: {e}")
        return []



def save_results(ul_diseases):
    """
    保存爬取结果到文件
    """
    output_file = 'precise_diseases.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("精确爬取的神经内科疾病信息\n")
        f.write("=" * 60 + "\n")
        f.write(f"爬取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"目标网址: https://jib.xywy.com/html/shenjingneike.html\n")
        f.write("-" * 60 + "\n")
        
        # 保存 ul 元素中的疾病
        f.write("从 ul.ks-ill-list 中爬取的疾病:\n")
        f.write("-" * 40 + "\n")
        for i, disease in enumerate(ul_diseases, 1):
            f.write(f"{i:3d}. {disease}\n")
        f.write(f"总计: {len(ul_diseases)} 个疾病\n")
        
        f.write("-" * 60 + "\n")
        f.write("爬取完成！\n")
    
    print(f"\n结果已保存到: {output_file}")
    return ul_diseases

def main():
    """
    主函数
    """
    print("开始精确爬取神经内科疾病信息...")
    print("=" * 60)
    
    # 从 ul 元素爬取
    ul_diseases = crawl_diseases_from_ul()
    
    # 保存结果
    save_results(ul_diseases)
    
    print("\n爬取完成！")
    print(f"ul 元素疾病数: {len(ul_diseases)}")
    
    # 显示前20个疾病名称
    print("\n前20个疾病名称:")
    for i, disease in enumerate(ul_diseases[:20], 1):
        print(f"{i:2d}. {disease}")
    
    if len(ul_diseases) > 20:
        print(f"... 还有 {len(ul_diseases) - 20} 个疾病名称")

if __name__ == "__main__":
    main()
