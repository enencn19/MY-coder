#!/usr/bin/env python3
"""
分析当前实验存在的问题
"""

import sys
import os
import json
import pandas as pd
sys.path.append('/mnt/nvme0n1/tyj/TKGQA')

def analyze_log_issues():
    """分析日志中的问题"""
    print("=== 分析日志中的问题 ===")
    
    # 从日志中可以看到的问题：
    issues = [
        "1. print_final_stats()参数错误 - 方法签名不匹配",
        "2. 问题4/5/6的F1分数为0 - 查询逻辑有问题", 
        "3. 实体识别不准确 - 如'Juan Carlos I'、'Brazilian Ministry'等",
        "4. 时间约束提取失败 - 导致after_first/before_last查询失败",
        "5. 关系映射不完整 - 缺少关键关系映射",
        "6. 代码生成模板过于复杂 - 容易出错",
        "7. 错误处理不够健壮 - 异常时返回空结果"
    ]
    
    for issue in issues:
        print(f"  {issue}")
    
    return issues

def analyze_failed_questions():
    """分析失败的问题类型"""
    print("\n=== 分析失败的问题类型 ===")
    
    failed_patterns = {
        "after_first": "需要找到参考时间点，然后查找之后的第一个事件",
        "before_last": "需要找到参考时间点，然后查找之前的最后一个事件", 
        "equal_multi": "需要找到同一时间的多个相关事件",
        "first_last": "时间答案需要正确的时间格式和粒度",
        "entity_matching": "实体名称在KG中的实际存储格式不匹配"
    }
    
    for pattern, description in failed_patterns.items():
        print(f"  {pattern}: {description}")

def main():
    print("当前实验问题分析")
    print("=" * 60)
    
    analyze_log_issues()
    analyze_failed_questions()
    
    print("\n=== 改进建议 ===")
    improvements = [
        "1. 修复print_final_stats方法签名",
        "2. 简化代码生成模板，提高可靠性",
        "3. 改进实体识别和匹配逻辑",
        "4. 优化时间约束提取",
        "5. 完善关系映射表",
        "6. 增强错误处理和日志记录",
        "7. 添加查询结果验证机制"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")

if __name__ == "__main__":
    main()