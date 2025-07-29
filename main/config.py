"""
配置文件 - 包含所有实验配置参数
"""
import os

# DeepSeek API配置
DEEPSEEK_CONFIG = {
    "api_key": os.environ.get("OPENROUTER_API_KEY"),  # 请替换为你的API密钥
    # "base_url": "https://api.deepseek.com",
    "base_url": "https://openrouter.ai/api/v1",  
    "model": "qwen/qwen3-coder:free"
}

# 文件路径配置
PATHS = {
    "kg_path": "MY/data/output/full_df.txt",  # 知识图谱文件路径
    "questions_path": "MY/data/multitq/questions/sample_20_questions.json",  # 问题文件路径
    "output_dir": "MY/results"  # 输出目录
}

# 实验配置
EXPERIMENT_CONFIG = {
    "max_questions": 10,  # 最大处理问题数，0表示处理所有问题
    "save_interval": 5,   # 每处理多少个问题保存一次中间结果
    "timeout": 30,        # 单个查询超时时间（秒）
    "max_retries": 3      # 最大重试次数
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file_encoding": "utf-8"
}
