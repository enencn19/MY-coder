#!/usr/bin/env python3
"""
时序知识图谱问答实验结果分析
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os
import sys

def load_results(result_file):
    """加载实验结果"""
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    return results

def analyze_results(results):
    """分析实验结果"""
    # 转换为DataFrame
    df = pd.DataFrame(results)
    
    # 基本统计
    total = len(df)
    successful = len(df[df['predicted_answers'].apply(lambda x: len(x) > 0)])
    exact_match = sum(r['evaluation']['exact_match'] for r in results if 'evaluation' in r)
    
    print(f"总问题数: {total}")
    print(f"有答案的问题数: {successful} ({successful/total:.1%})")
    print(f"精确匹配的问题数: {exact_match} ({exact_match/total:.1%})")
    
    # 按问题类型分析
    question_types = Counter(df['analysis'].apply(lambda x: x.get('question_type', 'unknown')))
    print("\n问题类型分布:")
    for qtype, count in question_types.most_common():
        success_count = len(df[(df['analysis'].apply(lambda x: x.get('question_type', 'unknown') == qtype)) & 
                              (df['predicted_answers'].apply(lambda x: len(x) > 0))])
        print(f"  {qtype}: {count} 问题, {success_count} 成功 ({success_count/count:.1%})")
    
    # 按答案类型分析
    answer_types = Counter(df['analysis'].apply(lambda x: x.get('answer_type', 'unknown')))
    print("\n答案类型分布:")
    for atype, count in answer_types.most_common():
        success_count = len(df[(df['analysis'].apply(lambda x: x.get('answer_type', 'unknown') == atype)) & 
                              (df['predicted_answers'].apply(lambda x: len(x) > 0))])
        print(f"  {atype}: {count} 问题, {success_count} 成功 ({success_count/count:.1%})")
    
    # 错误分析
    error_cases = df[df['evaluation'].apply(lambda x: not x.get('exact_match', False) if isinstance(x, dict) else True)]
    print(f"\n错误案例数: {len(error_cases)}")
    
    # 常见错误模式
    error_patterns = []
    for _, row in error_cases.iterrows():
        if not row['predicted_answers']:
            error_patterns.append("空结果")
        elif isinstance(row['evaluation'], dict) and row['evaluation'].get('precision', 0) > 0:
            error_patterns.append("部分正确")
        else:
            error_patterns.append("完全错误")
    
    error_counter = Counter(error_patterns)
    print("\n错误模式分布:")
    for pattern, count in error_counter.most_common():
        print(f"  {pattern}: {count} ({count/len(error_cases):.1%})")
    
    return df

def analyze_failure_cases(results):
    """详细分析失败案例"""
    df = pd.DataFrame(results)
    
    print("=" * 60)
    print("失败案例详细分析")
    print("=" * 60)
    
    # 1. 按失败类型分类
    failure_types = {
        'empty_results': [],      # 空结果
        'code_generation_failed': [],  # 代码生成失败
        'execution_failed': [],   # 执行失败
        'analysis_failed': [],    # 分析失败
        'wrong_results': []       # 结果错误
    }
    
    for _, row in df.iterrows():
        predicted = row.get('predicted_answer', [])
        evaluation = row.get('evaluation', {})
        
        if not predicted or len(predicted) == 0:
            failure_types['empty_results'].append(row)
        elif any(fail_msg in str(predicted) for fail_msg in ['代码生成失败', '函数提取失败']):
            failure_types['code_generation_failed'].append(row)
        elif any(fail_msg in str(predicted) for fail_msg in ['执行错误', '查询执行错误']):
            failure_types['execution_failed'].append(row)
        elif row.get('analysis', {}).get('question_type') == 'entity_query' and not row.get('analysis', {}).get('key_entities'):
            failure_types['analysis_failed'].append(row)
        elif not evaluation.get('exact_match', False):
            failure_types['wrong_results'].append(row)
    
    # 2. 打印各类失败统计
    total_failures = len(df[df['evaluation'].apply(lambda x: not x.get('exact_match', False))])
    
    print(f"总失败案例: {total_failures}")
    for failure_type, cases in failure_types.items():
        if cases:
            print(f"\n{failure_type}: {len(cases)} 案例")
            # 显示前3个案例的详细信息
            for i, case in enumerate(cases[:3]):
                print(f"  案例 {i+1}:")
                print(f"    问题: {case.get('question', 'N/A')[:100]}...")
                print(f"    预测: {case.get('predicted_answer', 'N/A')}")
                print(f"    标准答案: {case.get('ground_truth', 'N/A')}")
                if 'analysis' in case:
                    analysis = case['analysis']
                    print(f"    分析结果: 类型={analysis.get('question_type', 'N/A')}, 实体={analysis.get('key_entities', [])}")
    
    # 3. 分析代码生成模式
    print("\n" + "=" * 40)
    print("代码生成问题分析")
    print("=" * 40)
    
    code_issues = []
    for _, row in df.iterrows():
        if 'generated_code' in row:
            code = row['generated_code']
            if not code or len(code) < 100:
                code_issues.append(f"代码过短: {row.get('quid', 'N/A')}")
            elif 'def query_kg' not in code:
                code_issues.append(f"缺少函数定义: {row.get('quid', 'N/A')}")
            elif code.count('return') == 0:
                code_issues.append(f"缺少返回语句: {row.get('quid', 'N/A')}")
    
    if code_issues:
        print("发现的代码问题:")
        for issue in code_issues[:10]:  # 显示前10个
            print(f"  - {issue}")
    
    return failure_types

def suggest_improvements(failure_types):
    """基于失败分析提出改进建议"""
    print("\n" + "=" * 40)
    print("改进建议")
    print("=" * 40)
    
    suggestions = []
    
    if failure_types['empty_results']:
        suggestions.append("1. 空结果问题:")
        suggestions.append("   - 改进实体识别和匹配逻辑")
        suggestions.append("   - 增加模糊匹配和同义词处理")
        suggestions.append("   - 优化时间范围查询")
    
    if failure_types['code_generation_failed']:
        suggestions.append("2. 代码生成问题:")
        suggestions.append("   - 改进prompt模板")
        suggestions.append("   - 增加代码验证步骤")
        suggestions.append("   - 提供更多代码示例")
    
    if failure_types['analysis_failed']:
        suggestions.append("3. 问题分析问题:")
        suggestions.append("   - 改进实体抽取算法")
        suggestions.append("   - 增加问题类型识别准确性")
        suggestions.append("   - 优化时间信息提取")
    
    if failure_types['execution_failed']:
        suggestions.append("4. 执行失败问题:")
        suggestions.append("   - 增加异常处理")
        suggestions.append("   - 验证数据格式")
        suggestions.append("   - 优化查询逻辑")
    
    for suggestion in suggestions:
        print(suggestion)

def visualize_results(df, output_dir):
    """可视化实验结果"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置风格
    sns.set(style="whitegrid")
    
    # 1. 问题类型分布
    plt.figure(figsize=(10, 6))
    question_types = df['analysis'].apply(lambda x: x.get('question_type', 'unknown')).value_counts()
    ax = question_types.plot(kind='bar', color='skyblue')
    plt.title('问题类型分布')
    plt.xlabel('问题类型')
    plt.ylabel('数量')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/question_types.png")
    
    # 2. 答案类型分布
    plt.figure(figsize=(10, 6))
    answer_types = df['analysis'].apply(lambda x: x.get('answer_type', 'unknown')).value_counts()
    ax = answer_types.plot(kind='bar', color='lightgreen')
    plt.title('答案类型分布')
    plt.xlabel('答案类型')
    plt.ylabel('数量')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/answer_types.png")
    
    # 3. 评估指标分布
    plt.figure(figsize=(12, 6))
    metrics = pd.DataFrame([
        {
            'precision': r['evaluation'].get('precision', 0),
            'recall': r['evaluation'].get('recall', 0),
            'f1': r['evaluation'].get('f1', 0)
        }
        for r in df['evaluation'] if isinstance(r, dict)
    ])
    
    metrics.plot(kind='box')
    plt.title('评估指标分布')
    plt.ylabel('分数')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/metrics_distribution.png")
    
    # 4. 成功率按问题类型
    plt.figure(figsize=(12, 6))
    success_by_type = df.groupby(df['analysis'].apply(lambda x: x.get('question_type', 'unknown')))['evaluation'].apply(
        lambda x: sum(1 for e in x if isinstance(e, dict) and e.get('exact_match', False)) / len(x)
    )
    ax = success_by_type.plot(kind='bar', color='salmon')
    plt.title('各问题类型的成功率')
    plt.xlabel('问题类型')
    plt.ylabel('成功率')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/success_by_type.png")
    
    print(f"可视化结果已保存到 {output_dir} 目录")

def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_results.py <结果文件路径> [输出目录]")
        sys.exit(1)
    
    result_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "analysis_results"
    
    print(f"分析结果文件: {result_file}")
    results = load_results(result_file)
    df = analyze_results(results)
    
    # 新增：失败案例分析
    failure_types = analyze_failure_cases(results)
    suggest_improvements(failure_types)
    
    visualize_results(df, output_dir)

if __name__ == "__main__":
    main()
