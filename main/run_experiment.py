#!/usr/bin/env python3
"""
时序知识图谱问答实验运行脚本
"""

import sys
import os
import logging
import json
from datetime import datetime
sys.path.append('/mnt/nvme0n1/tyj/TKGQA')

from MY.main.temporal_kgqa_experiment import TemporalKGQASystem
from MY.main.config import DEEPSEEK_CONFIG, PATHS, EXPERIMENT_CONFIG

def setup_logging():
    """设置日志系统"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"experiment_{timestamp}.log"
    log_path = os.path.join("/mnt/nvme0n1/tyj/TKGQA/MY/logs", log_filename)
    
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger()
    logger.info(f"日志系统初始化完成，日志文件: {log_path}")
    return logger

def run_complete_experiment(system, logger):
    """运行完整实验"""
    try:
        # 加载数据
        system.load_data()
        
        # 准备结果文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(system.results_dir, f"final_results_{timestamp}.json")
        
        # 确保结果目录存在
        os.makedirs(system.results_dir, exist_ok=True)
        
        # 处理所有问题，边处理边保存
        results = []
        total_questions = len(system.questions)
        
        logger.info(f"开始处理 {total_questions} 个问题")
        
        for i, question_data in enumerate(system.questions):
            logger.info(f"\n{'='*60}")
            logger.info(f"进度: {i+1}/{total_questions}")
            
            # 处理单个问题
            result = system.process_single_question(question_data)
            results.append(result)
            
            # 实时保存结果到文件
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"结果已更新到: {results_file}")
            
            # 如果设置了最大问题数限制
            max_questions = system.config.get('max_questions')
            if max_questions and max_questions > 0 and i + 1 >= max_questions:
                logger.info(f"达到最大问题数限制: {max_questions}")
                break
        
        # 打印最终统计信息 - 修改这里
        # system.print_final_stats(results)  # 原来的错误调用
        system.print_final_stats()  # 修改为不传参数
        
        # 或者手动打印统计信息
        total_questions = len(results)
        successful_results = [r for r in results if r.get('f1', 0) > 0]
        success_rate = len(successful_results) / total_questions if total_questions > 0 else 0
        avg_f1 = sum(r.get('f1', 0) for r in results) / total_questions if total_questions > 0 else 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 实验统计信息:")
        logger.info(f"总问题数: {total_questions}")
        logger.info(f"成功回答数: {len(successful_results)}")
        logger.info(f"成功率: {success_rate:.2%}")
        logger.info(f"平均F1分数: {avg_f1:.3f}")
        logger.info(f"{'='*60}")
        
        logger.info(f"✅ 实验成功完成！")
        logger.info(f"📊 处理问题数: {len(results)}")
        logger.info(f"📁 最终结果文件: {results_file}")
        
        return results
        
    except Exception as e:
        logger.error(f"实验执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

def main():
    print("=" * 60)
    print("时序知识图谱问答实验")
    print("=" * 60)
    
    try:
        # 设置日志
        logger = setup_logging()
        
        # 检查必要文件
        question_file = PATHS["questions_path"]
        kg_file = PATHS["kg_path"]
        
        if not os.path.exists(question_file):
            logger.error(f"问题文件不存在 {question_file}")
            return
            
        if not os.path.exists(kg_file):
            logger.error(f"知识图谱文件不存在 {kg_file}")
            return
        
        # 合并配置
        config = {
            **DEEPSEEK_CONFIG,
            **PATHS,
            **EXPERIMENT_CONFIG
        }
        
        # 创建系统实例
        system = TemporalKGQASystem(config)
        
        # 运行完整实验
        results = run_complete_experiment(system, logger)
        
        logger.info("🎉 实验全部完成！")
        
    except Exception as e:
        logger.error(f"❌ 实验运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
