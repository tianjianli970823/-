import pandas as pd
from sqlalchemy import create_engine
import xlwings as xw

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
df_to_export = df[['SKU', '实际发货数量']].copy()

#重命名 列
df_to_export.columns = ['Merchant SKU', 'Quantity']

# 定义Excel文件路径和工作表名称
excel_file_path = r"D:\数据源\亚马逊\亚马逊发货匹配表格1.xlsx"
sheet_name = 'Create workflow – template'

# 打开Excel文件
book = xw.Book(excel_file_path)
# 选择要修改的工作表
sheet = book.sheets[sheet_name]

# 获取第八行的数据，作为列名
column_names = [cell.value for cell in sheet.range('8:8') if cell.value is not None]

# 获取两个数据框中都存在的列
common_columns = df_to_export.columns.intersection(column_names)

# 遍历每一行，从第九行开始（因为第八行是列名）
for i in range(9, len(df) + 9):
    # 检查行是否存在
    if i-9 in df_to_export.index:
        # 遍历每一个公共列
        for column in common_columns:
            # 获取列名对应的列号
            col_num = column_names.index(column) + 1
            # 更新Excel中的数据
            sheet.range((i, col_num)).value = df_to_export.loc[i-9, column]

# 保存并关闭Excel文件
book.save()
book.close()