#!/usr/bin/env python3
"""
修复查询问题的脚本
"""

import sys
import os
import pandas as pd
import re
sys.path.append('/mnt/nvme0n1/tyj/TKGQA')

from MY.temporal_kgqa_experiment import TemporalKGQASystem
from MY.config import DEEPSEEK_CONFIG, PATHS, EXPERIMENT_CONFIG

def fix_entity_matching():
    """修复实体匹配问题"""
    print("=== 修复实体匹配问题 ===")
    
    # 创建系统实例
    config = {**DEEPSEEK_CONFIG, **PATHS, **EXPERIMENT_CONFIG}
    system = TemporalKGQASystem(config)
    system.load_data()
    
    # 问题3: 检查缺失答案的实际存在形式
    print("\n问题3 - 检查缺失答案的实际存在形式:")
    missing_answers = ['Royal Air Force', 'Christian (France)', 'Separatist (France)', 'Member of Parliament (France)', 'Comoros']
    
    for answer in missing_answers:
        print(f"\n查找 '{answer}':")
        
        # 尝试不同的匹配方式
        patterns = [
            answer,
            answer.replace(' ', '_'),
            answer.replace('(', '').replace(')', ''),
            answer.split('(')[0].strip() if '(' in answer else answer
        ]
        
        found = False
        for pattern in patterns:
            # 在head中查找
            head_matches = system.kg_df[system.kg_df['head'].str.contains(pattern, case=False, na=False, regex=False)]
            if not head_matches.empty:
                print(f"  在head中找到 '{pattern}': {len(head_matches)} 条")
                print(f"    样例: {head_matches['head'].unique()[:3].tolist()}")
                found = True
                
            # 在tail中查找
            tail_matches = system.kg_df[system.kg_df['tail'].str.contains(pattern, case=False, na=False, regex=False)]
            if not tail_matches.empty:
                print(f"  在tail中找到 '{pattern}': {len(tail_matches)} 条")
                print(f"    样例: {tail_matches['tail'].unique()[:3].tolist()}")
                found = True
        
        if not found:
            print(f"  ❌ 未找到任何匹配")

def fix_time_parsing():
    """修复时间解析问题"""
    print("\n=== 修复时间解析问题 ===")
    
    # 问题4的时间解析
    question4 = "Which country was the first to ask for France after the Algerian extremist?"
    print(f"问题4: {question4}")
    
    # 这个问题的时间约束应该是"Algerian extremist"事件的时间
    # 需要先找到这个事件的时间
    config = {**DEEPSEEK_CONFIG, **PATHS, **EXPERIMENT_CONFIG}
    system = TemporalKGQASystem(config)
    system.load_data()
    
    # 查找Algerian相关的事件
    algerian_events = system.kg_df[
        (system.kg_df['head'].str.contains('Algeria', case=False, na=False)) |
        (system.kg_df['tail'].str.contains('Algeria', case=False, na=False)) |
        (system.kg_df['head'].str.contains('Algerian', case=False, na=False)) |
        (system.kg_df['tail'].str.contains('Algerian', case=False, na=False))
    ]
    
    print(f"找到Algerian相关事件: {len(algerian_events)} 条")
    if not algerian_events.empty:
        print("时间范围:")
        print(f"  最早: {algerian_events['timestamp'].min()}")
        print(f"  最晚: {algerian_events['timestamp'].max()}")
        
        # 查找extremist相关的
        extremist_events = algerian_events[
            (algerian_events['head'].str.contains('extremist', case=False, na=False)) |
            (algerian_events['tail'].str.contains('extremist', case=False, na=False))
        ]
        
        if not extremist_events.empty:
            print(f"找到extremist事件: {len(extremist_events)} 条")
            print("样例:")
            print(extremist_events[['head', 'relation', 'tail', 'timestamp']].head())

def fix_reference_entity():
    """修复参考实体识别问题"""
    print("\n=== 修复参考实体识别问题 ===")
    
    # 问题5的参考实体问题
    question5 = "Before the Brazilian Ministry of Agriculture, Fishing and Forestry, which country was the last to condemn France?"
    print(f"问题5: {question5}")
    
    config = {**DEEPSEEK_CONFIG, **PATHS, **EXPERIMENT_CONFIG}
    system = TemporalKGQASystem(config)
    system.load_data()
    
    # 查找Brazilian Ministry相关的实体
    brazilian_ministry = system.kg_df[
        (system.kg_df['head'].str.contains('Brazil', case=False, na=False)) &
        (system.kg_df['head'].str.contains('Ministry', case=False, na=False))
    ]
    
    print(f"找到Brazilian Ministry相关实体: {len(brazilian_ministry)} 条")
    if not brazilian_ministry.empty:
        print("实体样例:")
        unique_heads = brazilian_ministry['head'].unique()
        for head in unique_heads[:5]:
            if 'agriculture' in head.lower() or 'fishing' in head.lower() or 'forestry' in head.lower():
                print(f"  ✅ {head}")
            else:
                print(f"  - {head}")

def test_fixed_queries():
    """测试修复后的查询"""
    print("\n=== 测试修复后的查询 ===")
    
    config = {**DEEPSEEK_CONFIG, **PATHS, **EXPERIMENT_CONFIG}
    system = TemporalKGQASystem(config)
    system.load_data()
    
    # 测试问题3的修复查询
    print("\n测试问题3修复:")
    
    # 手动构建更准确的查询
    def fixed_query_3(df):
        results = []
        
        # 查找在2009-12-11之前对France使用军事力量的实体
        before_date = df['timestamp'] < '2009-12-11'
        military_relations = df['relation'].str.contains('military|force', case=False, na=False)
        france_target = df['tail'].str.contains('France', case=False, na=False)
        
        mask = before_date & military_relations & france_target
        
        if mask.any():
            matched_df = df[mask]
            for _, row in matched_df.iterrows():
                entity = row['head'].replace('_', ' ')
                if entity not in results:
                    results.append(entity)
        
        return results[:10]
    
    result3 = fixed_query_3(system.kg_df)
    print(f"修复后的问题3结果: {result3}")

if __name__ == "__main__":
    fix_entity_matching()
    fix_time_parsing()
    fix_reference_entity()
    test_fixed_queries()