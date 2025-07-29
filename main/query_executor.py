"""
查询执行器 - 负责执行生成的代码并修复错误
"""
import pandas as pd
import traceback
import logging
from typing import List, Any
from .result_processor import ResultProcessor


class QueryExecutor:
    def __init__(self):
        self.result_processor = ResultProcessor()
    
    def execute_query(self, code: str, kg_df: pd.DataFrame) -> list:
        """执行查询代码并返回清理后的结果"""
        try:
            # 创建执行环境
            exec_globals = {'df': kg_df, 'pd': pd}
            
            # 执行代码
            exec(code, exec_globals)
            
            # 获取查询函数并执行
            query_func = exec_globals.get('query_kg')
            if query_func:
                raw_results = query_func(kg_df)
                # 使用结果处理器清理结果
                cleaned_results = self.result_processor.process_results(raw_results)
                return cleaned_results
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"查询执行失败: {str(e)}")
            return []
    
    def _try_fix_code(self, code: str, error_msg: str) -> str:
        """尝试修复代码中的常见错误"""
        fixed_code = code
        
        # 修复括号不匹配问题
        if "closing parenthesis" in error_msg and "does not match" in error_msg:
            # 简单的括号修复
            lines = fixed_code.split('\n')
            for i, line in enumerate(lines):
                # 修复常见的括号问题
                if '(' in line and ')' not in line and i < len(lines) - 1:
                    if lines[i+1].strip().startswith(']'):
                        lines[i] = line + ')'
                elif line.strip() == '].copy()' and i > 0:
                    if '(' in lines[i-1] and ')' not in lines[i-1]:
                        lines[i-1] = lines[i-1] + ')'
            fixed_code = '\n'.join(lines)
        
        # 修复import错误
        if "__import__ not found" in error_msg:
            # 移除动态import，使用静态import
            fixed_code = "import pandas as pd\n" + fixed_code
            fixed_code = fixed_code.replace("import pandas as pd", "", 1)  # 移除重复的import
        
        # 修复字符串格式问题
        if "invalid syntax" in error_msg:
            # 修复f-string中的大括号问题
            fixed_code = fixed_code.replace("{{str(e)}}", "{str(e)}")
        
        return fixed_code
