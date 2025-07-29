#!/usr/bin/env python3
"""
检查实验结果
"""

import json
import os
import glob

def check_latest_results():
    """检查最新的结果文件"""
    results_dir = "/mnt/nvme0n1/tyj/TKGQA/MY"
    
    # 查找最新的结果文件
    pattern = os.path.join(results_dir, "final_results_*.json")
    result_files = glob.glob(pattern)
    
    if not result_files:
        print("未找到结果文件")
        return
    
    # 获取最新文件
    latest_file = max(result_files, key=os.path.getctime)
    print(f"检查文件: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print(f"总结果数: {len(results)}")
        
        # 检查问题3、4、5、6
        for i, result in enumerate(results):
            if i >= 2 and i <= 5:  # 问题3、4、5、6
                print(f"\n问题 {i+1}:")
                print(f"  QUID: {result.get('quid')}")
                print(f"  问题: {result.get('question', '')[:100]}...")
                print(f"  预期答案: {result.get('ground_truth')}")
                print(f"  预测答案: {result.get('predicted_answers')}")
                print(f"  F1分数: {result.get('f1', 0):.3f}")
                
                if 'error' in result:
                    print(f"  ❌ 错误: {result['error']}")
                
                if result.get('generated_code'):
                    print(f"  代码长度: {len(result['generated_code'])} 字符")
                else:
                    print(f"  ❌ 无生成代码")
                    
    except Exception as e:
        print(f"读取结果文件失败: {e}")

if __name__ == "__main__":
    check_latest_results()