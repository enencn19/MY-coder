"""
调试查询问题的脚本
"""
import sys
import os
import pandas as pd

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 现在可以正常导入
from main.kg_explorer import KGExplorer

def debug_failed_queries():
    # 加载KG数据
    try:
        kg_df = pd.read_csv('MY/data/output/full_df.txt', sep='\t', names=['head', 'relation', 'tail', 'timestamp'])
    except FileNotFoundError:
        # 尝试其他可能的路径
        try:
            kg_df = pd.read_csv('data/output/full_df.txt', sep='\t', names=['head', 'relation', 'tail', 'timestamp'])
        except FileNotFoundError:
            print("错误: 找不到KG数据文件")
            print("请确认以下路径之一存在:")
            print("  - MY/data/output/full_df.txt")
            print("  - data/output/full_df.txt")
            return
    
    explorer = KGExplorer(kg_df)
    
    print("=== KG数据统计 ===")
    print(f"总记录数: {len(kg_df)}")
    print(f"时间范围: {kg_df['timestamp'].min()} 到 {kg_df['timestamp'].max()}")
    
    # 首先查看所有关系
    print("\n=== 所有关系类型 ===")
    explorer.explore_relations()
    
    # 探索失败的查询
    print("\n=== 探索问题1: rejected by Kuomintang ===")
    explorer.explore_question_data(['Kuomintang'], ['reject', 'decline', 'criticize'])
    
    print("\n=== 探索问题2: declined Iran ===")
    explorer.explore_question_data(['Iran'], ['decline', 'reject', 'criticize'])
    
    print("\n=== 探索问题3: ask for France after Algerian ===")
    explorer.explore_question_data(['France', 'Algeria'], ['ask', 'request', 'appeal'])

if __name__ == "__main__":
    debug_failed_queries()