"""
关系映射工具 - 将自然语言关系映射到KG中的实际关系
"""

class RelationMapper:
    def __init__(self):
        self.relation_mappings = {
            # 访问相关
            'visit': ['Make_a_visit', 'Host_a_visit', 'Express_intent_to_meet_or_negotiate'],
            'received visit from': ['Host_a_visit', 'Make_a_visit'],
            'make a visit': ['Make_a_visit'],
            'host a visit': ['Host_a_visit'],
            'visit from': ['Host_a_visit', 'Make_a_visit'],
            'received': ['Host_a_visit', 'Receive'],
            
            # 合作相关
            'cooperate': ['Express_intent_to_cooperate', 'Engage_in_diplomatic_cooperation', 'Cooperate'],
            'work with': ['Express_intent_to_cooperate', 'Engage_in_diplomatic_cooperation'],
            'express interest in working with': ['Express_intent_to_cooperate'],
            'wanted to cooperate with': ['Express_intent_to_cooperate'],
            'engage in diplomatic cooperation': ['Engage_in_diplomatic_cooperation'],
            
            # 声明相关
            'condemn': ['Criticize_or_denounce', 'Disapprove'],
            'criticize': ['Criticize_or_denounce'],
            'denounce': ['Criticize_or_denounce'],
            'disapprove': ['Disapprove'],
            'praise': ['Praise_or_endorse'],
            'endorse': ['Praise_or_endorse'],
            
            # 请求相关
            'ask for': ['Appeal_to', 'Make_an_appeal_or_request', 'Express_intent_to_meet_or_negotiate'],
            'appeal to': ['Appeal_to'],
            'make an appeal or request': ['Make_an_appeal_or_request'],
            'request': ['Make_an_appeal_or_request'],
            
            # 军事相关
            'used conventional military force against': ['Use_conventional_military_force'],
            'use conventional military force': ['Use_conventional_military_force'],
            'military force': ['Use_conventional_military_force', 'Use_unconventional_violence', 'Fight_with_small_arms_and_light_weapons'],
            'conventional military force': ['Use_conventional_military_force'],
            'unconventional violence': ['Use_unconventional_violence'],
            'fight with small arms and light weapons': ['Fight_with_small_arms_and_light_weapons'],
            'threaten': ['Threaten'],
            'threaten with military force': ['Threaten_with_military_force'],
            
            # 谈判和会面
            'negotiate': ['Express_intent_to_meet_or_negotiate', 'Engage_in_negotiation'],
            'meet': ['Express_intent_to_meet_or_negotiate'],
            'express intent to meet or negotiate': ['Express_intent_to_meet_or_negotiate'],
            
            # 其他外交行为
            'provide aid': ['Provide_aid'],
            'aid': ['Provide_aid'],
            'provide military aid': ['Provide_military_aid'],
            'provide economic aid': ['Provide_economic_aid'],
            'make statement': ['Make_statement'],
            'statement': ['Make_statement'],
            
            # 经济相关
            'impose embargo': ['Impose_embargo'],
            'embargo': ['Impose_embargo'],
            'reduce or break diplomatic relations': ['Reduce_or_break_diplomatic_relations'],
            
            # 抗议和示威
            'demonstrate or rally': ['Demonstrate_or_rally'],
            'protest': ['Demonstrate_or_rally'],
            'rally': ['Demonstrate_or_rally'],
            
            # 拒绝和否定相关
            'rejected': ['Criticize_or_denounce', 'Disapprove', 'Reject'],
            'reject': ['Criticize_or_denounce', 'Disapprove', 'Reject'],
            'declined': ['Criticize_or_denounce', 'Disapprove', 'Reject'],
            'decline': ['Criticize_or_denounce', 'Disapprove', 'Reject'],
            'refused': ['Criticize_or_denounce', 'Disapprove', 'Reject'],
            'refuse': ['Criticize_or_denounce', 'Disapprove', 'Reject'],
        }
    
    def map_relation(self, natural_relation: str) -> list:
        """将自然语言关系映射到KG关系"""
        if not natural_relation:
            return []
            
        natural_relation = natural_relation.lower().strip()
        
        # 精确匹配
        if natural_relation in self.relation_mappings:
            return self.relation_mappings[natural_relation]
        
        # 模糊匹配 - 改进版
        matched_relations = []
        
        # 按关键词匹配
        for key, relations in self.relation_mappings.items():
            # 检查是否包含关键词
            if self._fuzzy_match(natural_relation, key):
                matched_relations.extend(relations)
        
        # 去重并返回
        return list(set(matched_relations)) if matched_relations else []
    
    def _fuzzy_match(self, query: str, key: str) -> bool:
        """改进的模糊匹配逻辑"""
        query_words = set(query.split())
        key_words = set(key.split())
        
        # 如果查询词在关键词中有重叠
        overlap = query_words.intersection(key_words)
        
        # 至少有一个长度>3的词匹配，或者有多个短词匹配
        significant_overlap = any(len(word) > 3 for word in overlap)
        multiple_overlap = len(overlap) >= 2
        
        return significant_overlap or multiple_overlap
    
    def map_from_question(self, question: str) -> list:
        """从完整问题中提取和映射关系"""
        question_lower = question.lower()
        all_relations = []
        
        # 特殊模式匹配
        patterns = {
            'express interest in working with': ['Express_intent_to_cooperate'],
            'wanted to cooperate with': ['Express_intent_to_cooperate'],
            'used conventional military force against': ['Use_conventional_military_force'],
            'first express interest in working with': ['Express_intent_to_cooperate'],
            'ask for help from': ['Make_an_appeal_or_request', 'Appeal_to'],
        }
        
        # 检查特殊模式
        for pattern, relations in patterns.items():
            if pattern in question_lower:
                all_relations.extend(relations)
        
        # 如果没有特殊模式匹配，使用关键词匹配
        if not all_relations:
            keywords = [
                'military force', 'cooperate', 'visit', 'condemn', 'criticize',
                'ask', 'appeal', 'threaten', 'negotiate', 'meet', 'work'
            ]
            
            for keyword in keywords:
                if keyword in question_lower:
                    mapped = self.map_relation(keyword)
                    all_relations.extend(mapped)
        
        # 默认关系 - 如果还是没有找到
        if not all_relations:
            all_relations = [
                'Make_a_visit', 'Host_a_visit', 'Express_intent_to_cooperate',
                'Criticize_or_denounce', 'Use_conventional_military_force',
                'Make_an_appeal_or_request'
            ]
        
        return list(set(all_relations))
    
    def get_all_kg_relations(self, kg_df) -> list:
        """获取KG中所有实际存在的关系"""
        return kg_df['relation'].unique().tolist()
    
    def suggest_relations_for_question(self, question: str, kg_df) -> list:
        """为特定问题建议最相关的关系"""
        question_lower = question.lower()
        available_relations = self.get_all_kg_relations(kg_df)
        
        # 基于问题内容的启发式规则
        if 'military force' in question_lower:
            preferred = ['Use_conventional_military_force', 'Use_unconventional_violence', 'Fight_with_small_arms_and_light_weapons']
        elif 'cooperate' in question_lower or 'work' in question_lower:
            preferred = ['Express_intent_to_cooperate', 'Engage_in_diplomatic_cooperation']
        elif 'visit' in question_lower:
            preferred = ['Make_a_visit', 'Host_a_visit']
        elif 'ask' in question_lower or 'appeal' in question_lower:
            preferred = ['Make_an_appeal_or_request', 'Appeal_to']
        else:
            preferred = self.map_from_question(question)
        
        # 只返回在KG中实际存在的关系
        return [rel for rel in preferred if rel in available_relations]
    
    def get_broader_relations(self, question: str) -> list:
        """获取更广泛的关系，用于模糊匹配"""
        question_lower = question.lower()
        
        # 基于问题类型的广泛关系映射
        if any(word in question_lower for word in ['reject', 'decline', 'refuse']):
            return ['Criticize_or_denounce', 'Disapprove', 'Reject', 'Express_intent_to_criticize_or_denounce']
        
        elif any(word in question_lower for word in ['ask', 'request', 'appeal']):
            return ['Make_an_appeal_or_request', 'Appeal_to', 'Express_intent_to_meet_or_negotiate']
        
        elif any(word in question_lower for word in ['condemn', 'criticize']):
            return ['Criticize_or_denounce', 'Disapprove', 'Express_intent_to_criticize_or_denounce']
        
        elif any(word in question_lower for word in ['visit', 'received']):
            return ['Make_a_visit', 'Host_a_visit', 'Express_intent_to_meet_or_negotiate']
        
        # 返回最常见的关系作为默认
        return ['Make_a_visit', 'Host_a_visit', 'Express_intent_to_cooperate', 'Criticize_or_denounce', 'Make_an_appeal_or_request']