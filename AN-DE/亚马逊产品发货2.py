import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# 文件路径
file_path = r'C:\Users\NINGMEI\Desktop\12.25-AN-空派2.xlsx'

# 读取 Excel 文件
df2 = pd.read_excel(file_path, sheet_name="工作表")

# 删除包含空值的行
df2.dropna(subset=['箱号（扫码）'], inplace=True)

# 创建一个空的字典来存储每个箱子的 DataFrame
boxes = {}

#获取所有的箱号（扫码）
box_numbers = df2['箱号（扫码）'].unique()

# 对于每个箱号，创建一个 DataFrame
for box_number in box_numbers:
    boxes[box_number] = df2[df2['箱号（扫码）'] == box_number][['名称（抓取）', 'SKU（抓取）', 'FNSKU（扫码）', '数量（输入）']]

# 现在，boxes 字典中的每个元素都是一个 DataFrame，代表一个箱子
# 例如，你可以通过 boxes[1.0] 来访问第一个箱子的 DataFrame


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

# 选择需要的列，并将'实际发货数量'列复制两次
df_to_export = df[['SKU', 'item_name', '实际发货数量', '实际发货数量']].copy()

# 重命名列
df_to_export.columns = ['SKU', '商品名称', '预计数量', '装箱数量']




# 在 df_to_export 中添加新的列
for i in range(1, 6):
    df_to_export[f'boxes{i}'] = 0

# 对比 'SKU（抓取）' 和 'SKU' 列，如果一样的话，在 'boxes1' 到 'boxes5' 这些列中填入 '数量（输入）'
for i in range(1, 6):
    if i in boxes:
        for index, row in boxes[i].iterrows():
            df_to_export.loc[df_to_export['SKU'] == row['SKU（抓取）'], f'boxes{i}'] = row['数量（输入）']


# # 保存 DataFrame 到 Excel 文件
df_to_export.to_excel("D:\数据源\亚马逊\output.xlsx", index=False)