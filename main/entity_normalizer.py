class EntityNormalizer:
    def __init__(self):
        self.entity_mappings = {
            'Kuomintang': ['Kuomintang', 'KMT', 'Chinese Nationalist Party'],
            'Brazilian Ministry of Agriculture, Fishing and Forestry': [
                'Brazilian Ministry of Agriculture', 'Brazil Ministry', 'Ministry (Brazil)'
            ],
            'Algerian extremist': ['Algeria', 'Algerian', 'Extremist (Algeria)'],
            'Juan Carlos I': ['Juan Carlos I', 'Juan Carlos', 'Royal Administration (Spain)']
        }
    
    def normalize_entity(self, entity: str) -> list:
        """标准化实体名称，返回可能的变体"""
        if entity in self.entity_mappings:
            return self.entity_mappings[entity]
        
        # 生成标准变体
        variants = [
            entity,
            entity.replace(' ', '_'),
            entity.replace('_', ' '),
            entity.lower(),
            entity.upper(),
            entity.title()
        ]
        
        return list(set(variants))