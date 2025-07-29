#!/usr/bin/env python3
"""
综合调试脚本 - 专门测试问题3、4、5、6
"""

import sys
import os
import json
sys.path.append('/mnt/nvme0n1/tyj/TKGQA')

from MY.main.temporal_kgqa_experiment import TemporalKGQASystem
from MY.main.config import DEEPSEEK_CONFIG, PATHS, EXPERIMENT_CONFIG

def test_failed_questions():
    """测试失败的问题3、4、5、6"""
    print("=== 测试失败的问题 ===")
    
    # 问题定义
    failed_questions = [
        {
            'quid': 2007873,
            'question': 'Before 11 December 2009, who used conventional military force against France?',
            'answers': ['Separatist (France)', 'Comoros', 'Royal Air Force', 'Bolivia', 'Colombia', 'Christian (France)', 'Member of Parliament (France)', 'Military (Russia)'],
            'qtype': 'before_after',
            'atype': 'entity'
        },
        {
            'quid': 2044815,
            'question': 'Which country was the first to ask for France after the Algerian extremist?',
            'answers': ['Iran'],
            'qtype': 'after_first',
            'atype': 'entity'
        },
        {
            'quid': 2016117,
            'question': 'Before the Brazilian Ministry of Agriculture, Fishing and Forestry, which country was the last to condemn France?',
            'answers': ['Mexico'],
            'qtype': 'before_last',
            'atype': 'entity'
        },
        {
            'quid': 2018890,
            'question': 'Who received Juan Carlos I\'s visit from Juan Carlos I on the same month of Qatar?',
            'answers': ['Royal Administration (Spain)', 'Royal Administration (Jordan)', 'Royal Administration (Saudi Arabia)'],
            'qtype': 'equal_multi',
            'atype': 'entity'
        }
    ]
    
    # 创建系统实例
    config = {**DEEPSEEK_CONFIG, **PATHS, **EXPERIMENT_CONFIG}
    system = TemporalKGQASystem(config)
    system.load_data()
    
    for i, question_data in enumerate(failed_questions, 3):
        print(f"\n{'='*60}")
        print(f"测试问题 {i}: {question_data['question']}")
        print(f"问题类型: {question_data['qtype']}")
        print(f"预期答案: {question_data['answers']}")
        
        try:
            # 使用系统的process_single_question方法
            print("\n直接测试完整处理:")
            result = system.process_single_question(question_data)
            
            print(f"预测答案: {result.get('predicted_answers', [])}")
            print(f"F1: {result.get('f1', 0):.3f}")
            print(f"精确率: {result.get('precision', 0):.3f}")
            print(f"召回率: {result.get('recall', 0):.3f}")
            
            if 'error' in result:
                print(f"❌ 错误: {result['error']}")
            
            if result.get('f1', 0) > 0.5:
                print("✅ 测试通过")
            else:
                print("❌ 需要改进")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

def check_missing_methods():
    """检查CodeGenerator缺失的方法"""
    print("\n=== 检查CodeGenerator缺失的方法 ===")
    
    from MY.main.code_generator import CodeGenerator
    from openai import OpenAI
    
    # 创建必要的client和model参数
    config = {**DEEPSEEK_CONFIG, **PATHS, **EXPERIMENT_CONFIG}
    client = OpenAI(api_key=config['api_key'], base_url=config['base_url'])
    generator = CodeGenerator(client, config['model'])
    
    missing_methods = [
        '_generate_after_first_code',
        '_generate_before_last_code', 
        '_generate_equal_multi_code'
    ]
    
    for method in missing_methods:
        if hasattr(generator, method):
            print(f"✅ {method} 存在")
        else:
            print(f"❌ {method} 缺失")
    
    print(f"\n现有方法:")
    methods = [m for m in dir(generator) if m.startswith('_generate_') and callable(getattr(generator, m))]
    for method in methods:
        print(f"  - {method}")

def main():
    """主测试函数"""
    print("综合调试 - 专门测试问题3、4、5、6")
    print("=" * 60)
    
    # 首先检查缺失的方法
    check_missing_methods()
    
    # 然后测试失败的问题
    test_failed_questions()

if __name__ == "__main__":
    main()
