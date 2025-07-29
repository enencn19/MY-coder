#!/usr/bin/env python3
"""
调试系统方法
"""

import sys
import os
sys.path.append('/mnt/nvme0n1/tyj/TKGQA')

from MY.temporal_kgqa_experiment import TemporalKGQASystem
from MY.config import DEEPSEEK_CONFIG, PATHS, EXPERIMENT_CONFIG

def debug_system_methods():
    """调试系统方法"""
    print("=== 调试系统方法 ===")
    
    # 创建系统实例
    config = {**DEEPSEEK_CONFIG, **PATHS, **EXPERIMENT_CONFIG}
    system = TemporalKGQASystem(config)
    
    # 检查系统方法
    print("系统可用方法:")
    methods = [method for method in dir(system) if not method.startswith('_')]
    for method in methods:
        print(f"  - {method}")
    
    # 检查是否有代码生成相关方法
    code_methods = [method for method in methods if 'code' in method.lower() or 'generate' in method.lower()]
    print(f"\n代码生成相关方法: {code_methods}")
    
    # 检查系统组件
    print(f"\n系统组件:")
    if hasattr(system, 'analyzer'):
        print(f"  - analyzer: {type(system.analyzer)}")
    if hasattr(system, 'code_generator'):
        print(f"  - code_generator: {type(system.code_generator)}")
    if hasattr(system, 'client'):
        print(f"  - client: {type(system.client)}")
    
    # 加载数据并测试一个简单问题
    try:
        system.load_data()
        print(f"\n数据加载成功:")
        print(f"  - 问题数量: {len(system.questions)}")
        print(f"  - KG三元组数量: {len(system.kg_df)}")
        
        # 测试第一个问题的处理
        if system.questions:
            test_question = system.questions[2]  # 问题3
            print(f"\n测试问题3: {test_question['question']}")
            
            # 尝试调用process_single_question
            if hasattr(system, 'process_single_question'):
                print("尝试调用process_single_question...")
                result = system.process_single_question(test_question)
                print(f"处理结果: {result}")
            else:
                print("❌ 没有process_single_question方法")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_system_methods()