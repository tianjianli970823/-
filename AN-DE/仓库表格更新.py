import pandas as pd
from sqlalchemy import create_engine

# 定义数据库连接信息
db_user = 'root'
db_password = '970823'
db_host = 'localhost'
db_name = 'an4006'

# 创建SQLAlchemy引擎并连接到MySQL数据库
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4")

# 从数据库中读取订单数量大于0的数据
df = pd.read_sql_query('SELECT * FROM an1014 WHERE 订单数量 > 0', con=engine)

# 选择需要的列
df_to_export = df[['SKU', 'ASIN', '款号', '色号', '颜色', 'size_name']]

# 重命名列
df_to_export.columns = ['仓库SKU', 'ASIN', '款号', '色号', '颜色', '码数']

# 导出到Excel
df_to_export.to_excel(r"D:\数据源\Test1\自己复制粘贴填到表格里.xlsx", index=False)
