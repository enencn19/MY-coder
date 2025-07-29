#!/usr/bin/env python3
"""
分析失败问题的脚本
"""

import sys
import os
import json
import pandas as pd
sys.path.append('/mnt/nvme0n1/tyj/TKGQA')

from MY.temporal_kgqa_experiment import TemporalKGQASystem
from MY.config import DEEPSEEK_CONFIG, PATHS, EXPERIMENT_CONFIG

def analyze_question(system, question_data, question_idx):
    """分析单个问题"""
    print(f"\n{'='*60}")
    print(f"分析问题 {question_idx}: {question_data['quid']}")
    print(f"问题: {question_data['question']}")
    
    # 修复字段名问题
    answers = question_data.get('answers', question_data.get('answer', []))
    print(f"预期答案: {answers}")
    print(f"问题类型: {question_data.get('qtype', 'unknown')}")
    print(f"答案类型: {question_data.get('atype', 'unknown')}")
    
    # 检查相关实体是否存在于知识图谱中
    question_text = question_data['question']
    
    # 检查知识图谱中的实体
    unique_heads = set(system.kg_df['head'].unique())
    unique_tails = set(system.kg_df['tail'].unique())
    all_entities = unique_heads.union(unique_tails)
    
    print(f"\n知识图谱统计:")
    print(f"- 总三元组数: {len(system.kg_df)}")
    print(f"- 唯一实体数: {len(all_entities)}")
    print(f"- 唯一关系数: {len(system.kg_df['relation'].unique())}")
    
    # 检查问题中可能的实体
    words = question_text.replace('?', '').replace(',', '').split()
    found_entities = []
    for word in words:
        if word in all_entities:
            found_entities.append(word)
    
    if found_entities:
        print(f"\n在知识图谱中找到的实体: {found_entities}")
    else:
        print(f"\n⚠️ 在知识图谱中未找到明显的实体")
        
        # 尝试更智能的实体匹配
        print(f"\n尝试模糊匹配...")
        fuzzy_matches = []
        for word in words:
            if len(word) > 3:  # 只检查长度大于3的词
                for entity in list(all_entities)[:1000]:  # 限制检查数量
                    if word.lower() in entity.lower() or entity.lower() in word.lower():
                        fuzzy_matches.append((word, entity))
                        break
        
        if fuzzy_matches:
            print(f"模糊匹配结果: {fuzzy_matches[:5]}")
    
    # 直接调用系统的处理方法
    try:
        print(f"\n尝试完整处理...")
        result = system.process_single_question(question_data)
        
        print(f"✅ 处理完成")
        print(f"预测答案: {result.get('predicted_answers', [])}")
        print(f"F1分数: {result.get('f1', 0):.3f}")
        print(f"精确率: {result.get('precision', 0):.3f}")
        print(f"召回率: {result.get('recall', 0):.3f}")
        
        # 显示生成的代码
        if 'query_code' in result:
            code = result['query_code']
            print(f"\n生成的代码长度: {len(code)} 字符")
            print(f"代码预览:\n{code[:500]}...")
            
            # 分析为什么答案不完全正确
            expected = set(str(x).lower() for x in result.get('expected_answers', []))
            predicted = set(str(x).lower() for x in result.get('predicted_answers', []))
            
            missing = expected - predicted
            extra = predicted - expected
            
            if missing:
                print(f"\n❌ 缺失的答案: {list(missing)}")
            if extra:
                print(f"⚠️ 多余的答案: {list(extra)}")
                
            # 检查KG中是否存在缺失的答案
            if missing:
                print(f"\n检查缺失答案在KG中的存在情况:")
                for missing_answer in list(missing)[:3]:  # 只检查前3个
                    count = len(system.kg_df[
                        (system.kg_df['head'].str.contains(missing_answer, case=False, na=False)) |
                        (system.kg_df['tail'].str.contains(missing_answer, case=False, na=False))
                    ])
                    print(f"  '{missing_answer}': {count} 条记录")
        else:
            print(f"❌ 没有生成代码")
            
    except Exception as e:
        print(f"❌ 处理异常: {e}")
        import traceback
        print(traceback.format_exc()[:500])

def main():
    print("分析失败问题")
    
    # 创建系统实例
    config = {**DEEPSEEK_CONFIG, **PATHS, **EXPERIMENT_CONFIG}
    system = TemporalKGQASystem(config)
    
    # 加载数据
    system.load_data()
    
    # 分析问题3、4、5、6（索引2、3、4、5）
    target_questions = [2, 3, 4, 5]  # 问题3、4、5、6的索引
    
    for idx in target_questions:
        if idx < len(system.questions):
            analyze_question(system, system.questions[idx], idx + 1)
        else:
            print(f"问题 {idx + 1} 不存在")

if __name__ == "__main__":
    main()
