import json
import pandas as pd
import re
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from openai import OpenAI
import time

# API配置信息
api_key = os.environ.get("DeepSeek_API_KEY")
base_url = "https://api.deepseek.com"


class TemporalKGQASystem:
    def __init__(self):
        # 设置日志
        self.setup_logging()
        
        # 初始化DeepSeek R1客户端
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
        # 加载数据
        self.questions = self.load_questions()
        self.kg_df = self.load_knowledge_graph()
        
        # 结果存储
        self.results = []
        
        self.logger.info(f"系统初始化完成 - 问题数: {len(self.questions)}, KG三元组数: {len(self.kg_df)}")
        
    def setup_logging(self):
        """设置日志系统"""
        # 创建输出目录
        os.makedirs("/mnt/nvme0n1/tyj/TKGQA/MY/logs", exist_ok=True)
        
        # 设置日志格式
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # 创建logger
        self.logger = logging.getLogger('TemporalKGQA')
        self.logger.setLevel(logging.INFO)
        
        # 清除已有的handlers
        self.logger.handlers.clear()
        
        # 文件handler
        log_file = f"/mnt/nvme0n1/tyj/TKGQA/MY/logs/experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # 控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"日志系统初始化完成，日志文件: {log_file}")
    
    def load_questions(self) -> List[Dict]:
        """加载问题数据集"""
        with open('MY/data/multitq/questions/dev_25.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_knowledge_graph(self) -> pd.DataFrame:
        """加载时序知识图谱四元组数据"""
        return pd.read_csv('MY/data/output/full_df.txt', sep='\t', 
                          names=['head','relation','tail', 'timestamp'])
    
    def call_deepseek_r1(self, messages: List[Dict], temperature: float = 0.1) -> str:
        """调用DeepSeek R1模型"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=messages,
                temperature=temperature,
                max_tokens=2048
            )
            
            # 获取推理内容和最终答案
            reasoning_content = response.choices[0].message.reasoning_content
            content = response.choices[0].message.content
            
            if reasoning_content:
                self.logger.debug(f"推理过程: {reasoning_content[:300]}...")
            
            return content
            
        except Exception as e:
            self.logger.error(f"API调用错误: {e}")
            return ""
    
    def step1_natural_language_question(self, question_data: Dict) -> str:
        """Step 1: 自然语言问题"""
        question = question_data['question']
        self.logger.info(f"Step 1 - 问题: {question}")
        return question
    
    def step2_question_understanding(self, question: str) -> Dict:
        """Step 2: 问题理解 + 时间表达抽取"""
        prompt = f"""
请分析以下时序问答问题，提取关键信息：

问题: {question}

请按以下格式输出JSON：
{{
    "question_type": "时间类型(before_after/equal/first_last等)",
    "time_expressions": ["提取的时间表达"],
    "key_entities": ["关键实体"],
    "temporal_relation": "时间关系描述",
    "answer_type": "答案类型(entity/time)"
}}
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.call_deepseek_r1(messages)
        
        try:
            understanding = json.loads(response)
            self.logger.info(f"Step 2 - 问题理解: {understanding}")
            return understanding
        except Exception as e:
            self.logger.warning(f"Step 2 - JSON解析失败: {e}, 使用默认值")
            return {
                "question_type": "unknown",
                "time_expressions": [],
                "key_entities": [],
                "temporal_relation": "",
                "answer_type": "entity"
            }
    
    def step3_path_planning(self, question: str, understanding: Dict) -> Dict:
        """Step 3: 路径规划：识别关键实体 + 多跳路径结构"""
        prompt = f"""
基于时序知识图谱，为以下问题规划查询路径：

问题: {question}
问题理解: {understanding}

请分析需要的查询路径，输出JSON格式：
{{
    "start_entities": ["起始实体"],
    "target_entities": ["目标实体"],
    "path_structure": [
        {{
            "hop": 1,
            "relation_pattern": "关系模式",
            "constraints": ["约束条件"]
        }}
    ],
    "temporal_constraints": ["时间约束"],
    "multi_hop_strategy": "多跳策略描述"
}}
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.call_deepseek_r1(messages)
        
        try:
            path_plan = json.loads(response)
            self.logger.info(f"Step 3 - 路径规划: {path_plan}")
            return path_plan
        except Exception as e:
            self.logger.warning(f"Step 3 - JSON解析失败: {e}, 使用默认值")
            return {
                "start_entities": understanding.get("key_entities", []),
                "target_entities": [],
                "path_structure": [],
                "temporal_constraints": [],
                "multi_hop_strategy": "direct_query"
            }
    
    def step4_temporal_logic_expression(self, question: str, understanding: Dict, path_plan: Dict) -> str:
        """Step 4: 构造时序逻辑表达式"""
        prompt = f"""
基于以下信息构造时序逻辑表达式：

问题: {question}
问题理解: {understanding}
路径规划: {path_plan}

请构造形式化的时序逻辑表达式，考虑：
1. 时间约束 (before, after, equal, first, last)
2. 实体关系
3. 多跳路径
4. 时间粒度 (day, month, year)

输出格式：
{{
    "logic_expression": "时序逻辑表达式",
    "variables": {{"变量定义"}},
    "constraints": ["约束条件"],
    "temporal_operators": ["时间操作符"]
}}
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.call_deepseek_r1(messages)
        self.logger.info(f"Step 4 - 时序逻辑表达式生成完成")
        return response
    
    def step5_generate_query_code(self, question: str, understanding: Dict, 
                                 path_plan: Dict, logic_expr: str) -> str:
        """Step 5: 转为 Python 可执行查询代码"""
        prompt = f"""
基于以下信息生成Python查询代码，用于查询时序知识图谱：

问题: {question}
问题理解: {understanding}
路径规划: {path_plan}
时序逻辑表达式: {logic_expr}

数据格式：pandas DataFrame，列名为 ['head','relation','tail', 'timestamp']
时间格式：YYYY-MM-DD

请生成完整的Python函数，函数名为query_kg，参数为df（DataFrame），返回查询结果：

```python
def query_kg(df):
    import pandas as pd
    import re
    from datetime import datetime
    
    # 你的查询代码
    # 处理时间约束、实体匹配、多跳查询
    # 返回答案列表
    return results
```

注意：
1. 必须包含完整的函数定义
2. 处理时间比较和排序
3. 支持模糊匹配实体名称
4. 处理多跳查询
5. 考虑first/last等时序操作
6. 返回具体的答案列表，不要返回DataFrame
"""
        
        messages = [{"role": "user", "content": prompt}]
        response = self.call_deepseek_r1(messages)
        
        # 改进的代码提取逻辑
        query_code = self.extract_query_code(response)
        self.logger.info(f"Step 5 - 查询代码生成完成，代码长度: {len(query_code)}")
        self.logger.debug(f"Step 5 - 生成的代码:\n{query_code}")
        
        return query_code
    
    def extract_query_code(self, response: str) -> str:
        """提取查询代码"""
        # 尝试多种模式提取代码
        patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(def query_kg.*?)\n```',
            r'(def query_kg\(.*?\n(?:.*\n)*?.*return.*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                code = match.group(1).strip()
                if 'def query_kg' in code:
                    return code
        
        # 如果没有找到完整函数，尝试构造一个基本的
        if 'query_kg' in response:
            self.logger.warning("未找到完整的query_kg函数，尝试构造基本版本")
            return """
def query_kg(df):
    import pandas as pd
    import re
    from datetime import datetime
    
    # 基本查询逻辑
    results = []
    try:
        # 这里应该有具体的查询逻辑
        # 由于LLM生成的代码不完整，返回空结果
        pass
    except Exception as e:
        print(f"查询执行错误: {e}")
    
    return results
"""
        
        self.logger.error("无法提取有效的query_kg函数")
        return ""
    
    def step6_execute_query(self, query_code: str) -> List[str]:
        """Step 6: 执行查询代码获取答案"""
        if not query_code or 'def query_kg' not in query_code:
            self.logger.error("Step 6 - 无效的查询代码")
            return ["执行错误：无效的查询代码"]
        
        try:
            # 创建安全的执行环境
            exec_globals = {
                'pd': pd,
                'df': self.kg_df,
                're': re,
                'datetime': datetime,
                '__builtins__': __builtins__
            }
            
            # 执行查询代码
            exec(query_code, exec_globals)
            
            # 调用查询函数
            if 'query_kg' in exec_globals:
                results = exec_globals['query_kg'](self.kg_df)
                if isinstance(results, list):
                    self.logger.info(f"Step 6 - 查询成功，返回 {len(results)} 个结果")
                    return results
                else:
                    result_list = [str(results)] if results is not None else []
                    self.logger.info(f"Step 6 - 查询成功，转换为列表: {result_list}")
                    return result_list
            else:
                self.logger.error("Step 6 - 执行环境中未找到query_kg函数")
                return ["执行错误：未找到query_kg函数"]
                
        except Exception as e:
            self.logger.error(f"Step 6 - 执行错误: {str(e)}")
            return [f"执行错误: {str(e)}"]
    
    def process_single_question(self, question_data: Dict) -> Dict:
        """处理单个问题的完整流程"""
        quid = question_data['quid']
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"开始处理问题 {quid}")
        self.logger.info(f"{'='*50}")
        
        # Step 1: 自然语言问题
        question = self.step1_natural_language_question(question_data)
        
        # Step 2: 问题理解 + 时间表达抽取
        understanding = self.step2_question_understanding(question)
        
        # Step 3: 路径规划
        path_plan = self.step3_path_planning(question, understanding)
        
        # Step 4: 构造时序逻辑表达式
        logic_expr = self.step4_temporal_logic_expression(question, understanding, path_plan)
        
        # Step 5: 生成查询代码
        query_code = self.step5_generate_query_code(question, understanding, path_plan, logic_expr)
        
        # Step 6: 执行查询
        predicted_answers = self.step6_execute_query(query_code)
        
        # 构造结果
        result = {
            'quid': quid,
            'question': question,
            'ground_truth': question_data['answers'],
            'predicted_answers': predicted_answers,
            'understanding': understanding,
            'path_plan': path_plan,
            'logic_expression': logic_expr,
            'query_code': query_code,
            'answer_type': question_data.get('answer_type', 'unknown'),
            'time_level': question_data.get('time_level', 'unknown'),
            'qtype': question_data.get('qtype', 'unknown')
        }
        
        self.logger.info(f"问题 {quid} 处理完成")
        self.logger.info(f"预测答案: {predicted_answers}")
        self.logger.info(f"标准答案: {question_data['answers']}")
        
        return result
    
    def evaluate_result(self, result: Dict) -> Dict:
        """评估单个结果"""
        ground_truth = set(result['ground_truth'])
        predicted = set(result['predicted_answers'])
        
        # 计算准确率指标
        if len(predicted) == 0:
            precision = recall = f1 = 0.0
        else:
            intersection = ground_truth.intersection(predicted)
            precision = len(intersection) / len(predicted) if len(predicted) > 0 else 0
            recall = len(intersection) / len(ground_truth) if len(ground_truth) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # 完全匹配
        exact_match = ground_truth == predicted
        
        evaluation = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'exact_match': exact_match
        }
        
        self.logger.info(f"评估结果: P={precision:.3f}, R={recall:.3f}, F1={f1:.3f}, EM={exact_match}")
        
        return evaluation
    
    def run_experiment(self):
        """运行完整实验"""
        self.logger.info("开始时序知识图谱问答实验...")
        self.logger.info(f"问题总数: {len(self.questions)}")
        self.logger.info(f"知识图谱三元组数: {len(self.kg_df)}")
        
        all_results = []
        
        for i, question_data in enumerate(self.questions):
            try:
                # 处理单个问题
                result = self.process_single_question(question_data)
                
                # 评估结果
                evaluation = self.evaluate_result(result)
                result['evaluation'] = evaluation
                
                all_results.append(result)
                
                # 保存中间结果
                if (i + 1) % 5 == 0:
                    self.save_results(all_results, f"intermediate_results_{i+1}.json")
                
                # 避免API限制
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"处理问题 {question_data['quid']} 时出错: {e}")
                continue
        
        # 保存最终结果
        self.save_results(all_results, "final_results.json")
        
        # 计算整体评估指标
        self.compute_overall_metrics(all_results)
        
        return all_results
    
    def save_results(self, results: List[Dict], filename: str):
        """保存结果到文件"""
        output_path = f"/mnt/nvme0n1/tyj/TKGQA/MY/{filename}"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        self.logger.info(f"结果已保存到: {output_path}")
    
    def compute_overall_metrics(self, results: List[Dict]):
        """计算整体评估指标"""
        if not results:
            return
        
        evaluations = [r['evaluation'] for r in results if 'evaluation' in r]
        
        avg_precision = sum(e['precision'] for e in evaluations) / len(evaluations)
        avg_recall = sum(e['recall'] for e in evaluations) / len(evaluations)
        avg_f1 = sum(e['f1'] for e in evaluations) / len(evaluations)
        exact_match_rate = sum(e['exact_match'] for e in evaluations) / len(evaluations)
        
        metrics = {
            'total_questions': len(results),
            'avg_precision': avg_precision,
            'avg_recall': avg_recall,
            'avg_f1': avg_f1,
            'exact_match_rate': exact_match_rate
        }
        
        self.logger.info("\n" + "="*50)
        self.logger.info("整体评估结果")
        self.logger.info("="*50)
        for key, value in metrics.items():
            self.logger.info(f"{key}: {value:.4f}")
        
        # 保存评估指标
        with open("/mnt/nvme0n1/tyj/TKGQA/MY/evaluation_metrics.json", 'w') as f:
            json.dump(metrics, f, indent=2)

def main():
    """主函数"""
    # 创建输出目录
    os.makedirs("/mnt/nvme0n1/tyj/TKGQA/MY", exist_ok=True)
    
    # 初始化系统
    system = TemporalKGQASystem()
    
    # 运行实验
    results = system.run_experiment()
    
    system.logger.info(f"\n实验完成！处理了 {len(results)} 个问题")

if __name__ == "__main__":
    main()
