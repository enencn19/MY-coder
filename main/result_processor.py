"""
结果处理模块 - 负责清理和标准化查询结果
"""
import re

class ResultProcessor:
    def __init__(self):
        self.region_indicators = [
            'United States', 'Somalia', 'France', 'China', 'Russia', 'Jordan', 
            'Saudi Arabia', 'Spain', 'Iran', 'Iraq', 'Afghanistan', 'Pakistan', 
            'India', 'Japan', 'Korea', 'Brazil', 'Mexico', 'Canada', 'Australia', 
            'Germany', 'Italy', 'UK', 'Britain', 'Egypt', 'Turkey', 'Greece'
        ]
    
    def clean_entity_name(self, entity_name: str) -> str:
        """清理实体名称，保留重要的地区信息"""
        if not entity_name:
            return entity_name
        
        # 将下划线替换为空格
        cleaned = entity_name.replace('_', ' ')
        
        # 如果包含括号，检查是否是地区信息
        if '(' in cleaned and ')' in cleaned:
            # 提取括号内容
            bracket_match = re.search(r'\((.*?)\)', cleaned)
            if bracket_match:
                bracket_text = bracket_match.group(1)
                # 如果括号内容包含地区名称，保留整个名称
                if any(region in bracket_text for region in self.region_indicators):
                    return cleaned
                
                # 如果括号内容是单个大写字母开头的词，也保留
                if bracket_text and bracket_text[0].isupper():
                    return cleaned
        
        return cleaned
    
    def process_results(self, raw_results: list) -> list:
        """处理查询结果列表"""
        if not raw_results:
            return []
        
        cleaned_results = []
        for result in raw_results:
            if isinstance(result, str):
                cleaned = self.clean_entity_name(result)
                if cleaned and cleaned not in cleaned_results:
                    cleaned_results.append(cleaned)
        
        return cleaned_results