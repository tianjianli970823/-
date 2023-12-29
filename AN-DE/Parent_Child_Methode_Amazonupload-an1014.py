import pandas as pd
from sqlalchemy import create_engine
import xlwings as xw

# 定义数据库连接信息
db_user = 'root'
db_password = '970823'
db_host = 'localhost'
db_name = 'an4006'

# 定义Excel文件路径和工作表名称
excel_file_path = r"D:\数据源\Li-副本.xlsm"
sheet_name = 'Template'

# 创建SQLAlchemy引擎并连接到MySQL数据库
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4")

# 从数据库中读取数据
df = pd.read_sql('SELECT * FROM an1014', con=engine)

# 首先保存Parent行的数据
parent_row = df[df['parent_child'] == 'Parent']  # 假设你的parent_child列中的Parent行是你想要写入的行

# 只保留订单数量大于0的行或者是Child行
child_row = df[(df['订单数量'] > 0) & (df['parent_child'] != 'Parent')]  # 假设你的列名是'订单数量'
child_row = child_row.reset_index(drop=True)  # 重置索引

# 打开Excel文件
book = xw.Book(excel_file_path)

# 选择要修改的工作表
sheet = book.sheets[sheet_name]

# 获取第三行的数据，作为列名
column_names = [cell.value for cell in sheet.range('3:3') if cell.value is not None]

# 获取两个数据框中都存在的列
common_columns = parent_row.columns.intersection(column_names)

# 首先写入Parent行的数据
for column in common_columns:
    # 获取列名对应的列号
    col_num = column_names.index(column) + 1
    # 检查值是否为NaN
    if pd.notnull(parent_row[column].values[0]):
        # 更新Excel中的数据
        sheet.range((4, col_num)).value = parent_row[column].values[0]

# 再写入Child行的数据
common_columns = child_row.columns.intersection(column_names)
for i in range(len(parent_row) + 4, len(child_row) + len(parent_row) + 4):
    # 检查行是否存在
    if i-len(parent_row)-4 < len(child_row):
        # 遍历每一个公共列
        for column in common_columns:
            # 获取列名对应的列号
            col_num = column_names.index(column) + 1
            # 检查值是否为NaN
            if pd.notnull(child_row.loc[i-len(parent_row)-4, column]):
                # 更新Excel中的数据
                sheet.range((i, col_num)).value = child_row.loc[i-len(parent_row)-4, column]

# 保存并关闭Excel文件
book.save()
book.close()

#父子体写入格式