"""
KG数据探索工具 - 用于分析查询失败的原因
"""
import pandas as pd
import re

class KGExplorer:
    def __init__(self, kg_df):
        self.kg_df = kg_df
    
    def explore_relations(self):
        """探索所有关系"""
        relations = self.kg_df['relation'].value_counts()
        print("KG中的所有关系:")
        for rel, count in relations.head(20).items():
            print(f"  {rel}: {count}")
        return relations
    
    def find_entity_matches(self, entity_name):
        """查找实体匹配"""
        matches = []
        
        # 在head中查找
        head_matches = self.kg_df[
            self.kg_df['head'].str.contains(entity_name, case=False, na=False)
        ]['head'].unique()
        
        # 在tail中查找
        tail_matches = self.kg_df[
            self.kg_df['tail'].str.contains(entity_name, case=False, na=False)
        ]['tail'].unique()
        
        all_matches = list(set(list(head_matches) + list(tail_matches)))
        
        print(f"包含'{entity_name}'的实体:")
        for match in all_matches[:10]:
            print(f"  {match}")
        
        return all_matches
    
    def find_relation_matches(self, relation_keywords):
        """查找关系匹配"""
        matches = []
        for keyword in relation_keywords:
            keyword_matches = self.kg_df[
                self.kg_df['relation'].str.contains(keyword, case=False, na=False)
            ]['relation'].unique()
            matches.extend(keyword_matches)
        
        matches = list(set(matches))
        print(f"包含关键词{relation_keywords}的关系:")
        for match in matches:
            print(f"  {match}")
        
        return matches
    
    def explore_question_data(self, entities, relations_keywords, time_filter=None):
        """探索特定问题的数据"""
        print(f"\n=== 探索问题相关数据 ===")
        print(f"实体: {entities}")
        print(f"关系关键词: {relations_keywords}")
        
        # 查找实体
        for entity in entities:
            print(f"\n--- 实体 '{entity}' ---")
            self.find_entity_matches(entity)
        
        # 查找关系
        print(f"\n--- 关系匹配 ---")
        matched_relations = self.find_relation_matches(relations_keywords)
        
        # 组合查询
        print(f"\n--- 组合查询结果 ---")
        for entity in entities[:1]:  # 只查看第一个实体
            for relation in matched_relations[:3]:  # 只查看前3个关系
                mask = (
                    (self.kg_df['head'].str.contains(entity, case=False, na=False)) |
                    (self.kg_df['tail'].str.contains(entity, case=False, na=False))
                ) & (self.kg_df['relation'] == relation)
                
                if mask.any():
                    results = self.kg_df[mask].head(3)
                    print(f"  {entity} + {relation}:")
                    for _, row in results.iterrows():
                        print(f"    {row['head']} --{row['relation']}--> {row['tail']} ({row['timestamp']})")