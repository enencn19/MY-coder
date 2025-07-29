import pandas as pd
import os

input_path = "MY/data/multitq/kg/full.txt"
output_path = "MY/data/output/full_df.txt"

# 确保输出目录存在
os.makedirs(os.path.dirname(output_path), exist_ok=True)

try:
    # 读取数据
    df = pd.read_csv(
        input_path,
        sep=",",
        header=None,
        names=["head", "relation", "tail", "timestamp"],
        encoding="utf-8"
    )
    # 保存为新的TSV文件
    df.to_csv(output_path, sep="\t", index=False, encoding="utf-8")
    print(f"文件已保存到: {os.path.abspath(output_path)}")
    print(df.head())
except Exception as e:
    print("发生错误：", e)