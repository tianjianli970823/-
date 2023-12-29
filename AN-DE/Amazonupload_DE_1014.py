import pandas as pd
from sqlalchemy import create_engine
import xlwings as xw

# 定义数据库连接信息
db_user = 'root'
db_password = '970823'
db_host = 'localhost'
db_name = 'an4006'

# 定义Excel文件路径和工作表名称
excel_file_path = r"D:\数据源\Li - 副本.xlsm"
sheet_name = 'Template'

# 创建SQLAlchemy引擎并连接到MySQL数据库
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4")

# 从数据库中读取数据
df = pd.read_sql('SELECT * FROM an1014', con=engine)

# 只保留订单数量大于0的行
df = df[df['订单数量'] > 0]  # 假设你的列名是'订单数量'
# 重置索引
df = df.reset_index(drop=True)
# 打开Excel文件
book = xw.Book(excel_file_path)

# 选择要修改的工作表
sheet = book.sheets[sheet_name]

# 获取第三行的数据，作为列名
column_names = [cell.value for cell in sheet.range('3:3') if cell.value is not None]

# 获取两个数据框中都存在的列
common_columns = df.columns.intersection(column_names)

# 找到"parent_child"列值为"Parent"的那一行
parent_row = df[df['parent_child'] == 'Parent']

# 将这一行写入Excel的第四行
for column in common_columns:
    # 获取列名对应的列号
    col_num = column_names.index(column) + 1
    # 检查值是否为NaN
    value = parent_row[column].values[0]
    if pd.isna(value):
        # 如果是NaN，不写入任何东西
        continue
    # 更新Excel中的数据
    sheet.range((4, col_num)).value = value


# 删除"parent_child"列值为"Parent"的那一行
df = df[df['parent_child'] != 'Parent']

# 只保留订单数量大于0的行
df = df[df['订单数量'] > 0]  # 假设你的列名是'订单数量'
# 重置索引
df = df.reset_index(drop=True)

# 遍历每一行，从第五行开始
for i in range(5, len(df) + 5):
    # 检查行是否存在
    if i-5 in df.index:
        # 遍历每一个公共列
        for column in common_columns:
            # 获取列名对应的列号
            col_num = column_names.index(column) + 1
            # 更新Excel中的数据
            sheet.range((i, col_num)).value = df.loc[i-5, column]

# 保存并关闭Excel文件
book.save()
book.close()