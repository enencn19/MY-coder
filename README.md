# 时序知识图谱问答实验

## 实验概述

本实验实现了一个完整的时序知识图谱问答系统，通过6个步骤处理时序敏感的多跳推理问题：

1. **自然语言问题** - 输入原始问题
2. **问题理解 + 时间表达抽取** - 分析问题类型和时间信息
3. **路径规划** - 识别关键实体和多跳路径结构
4. **构造时序逻辑表达式** - 形式化表示查询逻辑
5. **转为Python可执行查询代码** - 生成具体查询代码
6. **执行获取答案** - 运行查询并返回结果

## 文件结构

```
MY/
├── temporal_kgqa_experiment.py  # 主实验代码
├── run_experiment.py           # 实验运行脚本
├── config.py                   # 配置文件
├── README.md                   # 说明文档
├── data/
│   ├── multitq/questions/dev_25.json  # 问题数据集
│   └── output/full_df.txt             # 知识图谱四元组
└── results/                    # 实验结果输出目录
```

temporal_kgqa_experiment.py - 主文件，包含核心系统类
utils.py - 工具函数模块，包含JSON解析、代码提取、答案标准化等
code_generator.py - 代码生成模块，包含各种查询代码模板
query_executor.py - 查询执行模块，负责执行代码和错误修复
config.py - 配置文件，包含所有配置参数


## 使用方法

### 1. 配置API密钥

编辑 `config.py` 文件，设置你的DeepSeek API密钥：

```python
DEEPSEEK_CONFIG = {
    "api_key": "sk-your-actual-api-key-here",
    # ...
}
```

### 2. 运行实验

```bash
cd /mnt/nvme0n1/tyj/TKGQA
python MY/run_experiment.py
```

### 3. 查看结果

实验结果将保存在 `/mnt/nvme0n1/tyj/TKGQA/MY/` 目录下：

- `final_results.json` - 完整实验结果
- `evaluation_metrics.json` - 评估指标
- `intermediate_results_*.json` - 中间结果文件

## 数据格式

### 输入数据

**问题数据** (`dev_25.json`):
```json
{
    "quid": 2000001,
    "question": "Who made optimistic remarks about Yasuo Fukuda after Japan?",
    "answers": ["Government Official (Japan)", "China"],
    "answer_type": "entity",
    "time_level": "day",
    "qtype": "before_after"
}
```

**知识图谱** (`full_df.txt`):
```
subject    predicate    object    timestamp
Iran       praise       Bahamas   2015-01-15
...
```

### 输出结果

```json
{
    "quid": 2000001,
    "question": "原始问题",
    "ground_truth": ["正确答案"],
    "predicted_answers": ["预测答案"],
    "understanding": {...},
    "path_plan": {...},
    "logic_expression": "...",
    "query_code": "...",
    "evaluation": {
        "precision": 0.8,
        "recall": 0.9,
        "f1": 0.85,
        "exact_match": true
    }
}
```

## 评估指标

- **Precision**: 预测答案中正确的比例
- **Recall**: 正确答案中被预测出的比例  
- **F1**: Precision和Recall的调和平均
- **Exact Match**: 预测答案与标准答案完全匹配的比例

## 注意事项

1. 确保DeepSeek API密钥有效且有足够配额
2. 实验会自动保存中间结果，可以断点续传
3. 每个API调用间有1秒延迟，避免触发限制
4. 如遇到错误，检查数据文件路径和格式