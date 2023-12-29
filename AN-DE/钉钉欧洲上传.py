import pandas as pd
from sqlalchemy import create_engine

# 定义数据库连接信息
db_user = 'root'
db_password = '970823'
db_host = 'localhost'
db_name = '仓库'

# 创建数据库引擎
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4')

# 使用引擎连接到数据库
connection = engine.connect()

# 从数据库中读取订单数量大于0的数据
df = pd.read_sql_query('SELECT * FROM an1014 WHERE 订单数量 > 0', con=engine)

# 选择需要的列
df_to_export = df[['SKU', '颜色', 'ASIN', 'FNSKU', '可用量', '实际发货数量']].copy()

# 重命名列
df_to_export.columns = ['卖家SKU', '颜色', 'ASIN', 'FNSKU', '发货数量', '实际发货数量']

# 计算“SKU总数”和“商品总数”
sku_total = df_to_export['卖家SKU'].nunique()
product_total = df_to_export['实际发货数量'].sum()

# 在DataFrame的最后添加两列“SKU总数”和“商品总数”
df_to_export['SKU总数'] = [sku_total if i == 0 else '' for i in range(len(df_to_export))]
df_to_export['商品总数'] = [product_total if i == 0 else '' for i in range(len(df_to_export))]

# 添加两列“运输方式”和“备注”
df_to_export['运输方式'] = ''
df_to_export['备注'] = ''

# 导出到Excel
df_to_export.to_excel(r"D:\数据源\钉钉欧洲发货群\AN1014德国 互邮-空派包税发货计划表-空模板.xlsx", index=False)
