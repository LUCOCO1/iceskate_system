import pandas as pd

# 创建示例数据
data = {
    '产品编码': ['P001', 'P002', 'P003'],
    '产品名称': ['产品A', '产品B', '产品C'],
    '规格': ['10x20cm', '30x40cm', '50x60cm'],
    '单位': ['个', '个', '个']
}

# 创建DataFrame
df = pd.DataFrame(data)

# 保存为Excel文件
df.to_excel('产品导入模板.xlsx', index=False)