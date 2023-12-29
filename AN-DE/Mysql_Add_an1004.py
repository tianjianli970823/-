import pandas as pd
from sqlalchemy import create_engine, text
import warnings
import re

warnings.filterwarnings('ignore', category=UserWarning)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# 读取整个Excel文件
with pd.ExcelFile(r"D:\数据源\Test1\PO231202AN1004-聚进加工单(2)(1).xlsx", engine='openpyxl') as xls:
    df_AN1004 = pd.read_excel(xls, '（运营）数据源')
    # 其他工作表
    other_sheets = {sheet_name: pd.read_excel(xls, sheet_name) for sheet_name in xls.sheet_names if
                    sheet_name != '（运营）数据源'}

# 更改列名
df_AN1004 = df_AN1004.rename(columns={'SKU ': 'SKU'})
df_AN1004 = df_AN1004.loc[:, 'SKU':'布行']
df_AN1004 = df_AN1004.dropna(subset=['颜色'])

# 创建一个函数来提取字符串中的中文部分
def extract_chinese(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]+', str(s)))

# 应用这个函数到 '颜色' 列
df_AN1004['颜色'] = df_AN1004['颜色'].apply(extract_chinese)


# 创建新的列 "型号"
df_AN1004['型号'] = df_AN1004.apply(lambda row: f"{row['布料类型']}-{row['颜色']}-{row['尺码']}", axis=1)


# 定义尺码的顺序
size_order = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']

# 将尺码列转换为Categorical类型
df_AN1004['尺码'] = pd.Categorical(df_AN1004['尺码'], categories=size_order, ordered=True)

# 首先按照色号分类，然后按照尺码列排序
df_AN1004 = df_AN1004.sort_values(['色号', '尺码'])

# 创建SQLAlchemy引擎并连接到MySQL服务器
engine = create_engine("mysql+pymysql://root:970823@localhost/?charset=utf8mb4")

# 创建一个新的数据库
with engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS an4006 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))

# 创建一个新的SQLAlchemy引擎，连接到an4006数据库
engine_an4006 = create_engine("mysql+pymysql://root:970823@localhost/an4006?charset=utf8mb4")

# 使用to_sql函数将数据框写入数据库
df_AN1004.to_sql('an1004', con=engine_an4006, if_exists='replace', index=False)

# 读取"亚马逊资料"表
df_amazon = pd.read_excel(r"D:\数据源\Test1\PO231202AN1004-聚进加工单(2)(1).xlsx", sheet_name='MySQLdata')

# 对于每一列
for column in df_amazon.columns:
    # 获取列的第一行数据
    column_value = df_amazon[column].iloc[0]

    # 将这个值添加到df_A1004数据框的每一行
    df_AN1004[column] = column_value

# 将更新后的数据框写入数据库
df_AN1004.to_sql('an1004', con=engine_an4006, if_exists='replace', index=False)

import os
from sqlalchemy import text

csv_file_path = r"D:\数据源\Test1\85398019719.csv"

# 从数据库中读取数据
df_AN1004 = pd.read_sql('an1004', con=engine_an4006)

# 在df_AN1004中创建新列，初始化为NaN
df_AN1004['FNSKU'] = pd.Series(dtype='str')
df_AN1004['ASIN'] = pd.Series(dtype='str')

# 检查CSV文件是否存在
if os.path.exists(csv_file_path):
    # 使用"ISO-8859-1"编码读取CSV文件
    df_csv = pd.read_csv(csv_file_path, encoding='ISO-8859-1')

    # 遍历df_csv的每一行
    for idx, row in df_csv.iterrows():
        # 找到SKU列和Merchant SKU列相同的行
        mask = df_AN1004['SKU'] == row['Merchant SKU']

        # 如果找到了匹配的行
        if mask.any():
            # 更新FNSKU和ASIN列
            df_AN1004.loc[mask, 'FNSKU'] = str(row['FNSKU'])  # 将FNSKU的值转换为字符串
            df_AN1004.loc[mask, 'ASIN'] = row['ASIN']

# 获取列名的列表
cols = df_AN1004.columns.tolist()

# 移除'FNSKU'和'ASIN'
cols.remove('FNSKU')
cols.remove('ASIN')

# 将'FNSKU'和'ASIN'插入到正确的位置
cols.insert(1, 'FNSKU')
cols.insert(2, 'ASIN')

# 使用新的列顺序重新排序数据框
df_AN1004 = df_AN1004[cols]

# 将更新后的数据框写入数据库
df_AN1004.to_sql('an1004', con=engine_an4006, if_exists='replace', index=False)

# 定义一个字典，映射原始尺码到新的尺码
size_mapping = {
    '2XL': 'XXL',
    '3XL': 'XXXL',
    '4XL': 'XXXXL',
    '5XL': 'XXXXXL'
}

# 使用字典替换尺码信息
df_AN1004['尺码'] = df_AN1004['尺码'].replace(size_mapping)

# 将更新后的数据框写入数据库
df_AN1004.to_sql('an1004', con=engine_an4006, if_exists='replace', index=False)

# # 从 'SKU' 列中提取颜色信息
# df_AN1004['color_name'] = df_AN1004['SKU'].apply(lambda x: x.split('-')[1])
#
# # 在 df_AN1004 中创建新列，初始化为 NaN
# df_AN1004['main_image_url'] = pd.Series(dtype='str')
#
#
# def update_image_url(df_AN1004, df_amazon, column_name):
#     # 从列中提取颜色信息和网页链接
#     df_amazon[['color_name', 'url']] = df_amazon[column_name].str.split('+', expand=True)
#
#     # 在df_AN1004中创建新列，初始化为NaN
#     df_AN1004[column_name] = pd.Series(dtype='str')
#
#     # 遍历df_amazon的每一行
#     for idx, row in df_amazon.iterrows():
#         # 找到颜色相同的行
#         mask = df_AN1004['color_name'] == row['color_name']
#
#         # 如果找到了匹配的行
#         if mask.any():
#             # 更新列
#             df_AN1004.loc[mask, column_name] = row['url']  # 将网页链接写入列
#
#
# update_image_url(df_AN1004, df_amazon, 'main_image_url')
# update_image_url(df_AN1004, df_amazon, 'other_image_url1')
# update_image_url(df_AN1004, df_amazon, 'other_image_url2')
# update_image_url(df_AN1004, df_amazon, 'other_image_url3')
# update_image_url(df_AN1004, df_amazon, 'other_image_url4')
# update_image_url(df_AN1004, df_amazon, 'other_image_url5')
#
# # 调用函数更新每个列
# update_image_url(df_AN1004, df_amazon, 'main_image_url')
# update_image_url(df_AN1004, df_amazon, 'other_image_url1')
# update_image_url(df_AN1004, df_amazon, 'other_image_url2')
# update_image_url(df_AN1004, df_amazon, 'other_image_url3')
# update_image_url(df_AN1004, df_amazon, 'other_image_url4')
# update_image_url(df_AN1004, df_amazon, 'other_image_url5')
#
# # 将更新后的数据框写入数据库
# df_AN1004.to_sql('an1004', con=engine_an4006, if_exists='replace', index=False)

# 复制'SKU'列的数据到新的'item_sku'列
df_AN1004['item_sku'] = df_AN1004['SKU']
df_AN1004['external_product_id'] = df_AN1004['ASIN']
# 定义一个字典，映射原始尺码到新的尺码
size_mapping = {
    'XXL': '2XL',
    'XXXL': '3XL',
    'XXXXL': '4XL',
    'XXXXXL': '5XL'
}

# 使用字典替换尺码信息
df_AN1004['size_name'] = df_AN1004['尺码'].replace(size_mapping)

# 将更新后的数据框写入数据库
df_AN1004.to_sql('an1004', con=engine_an4006, if_exists='replace', index=False)

# 从数据库中读取SKU数据
db_df = pd.read_sql('SELECT SKU FROM an1004', con=engine_an4006)

from sqlalchemy import text

with engine_an4006.connect() as connection:
    connection.execute(text("ALTER TABLE an1004 ADD 订单数量 DOUBLE"))
    connection.execute(text("ALTER TABLE an1004 ADD 可用量 DOUBLE"))

# 从数据库中读取SKU数据
with engine_an4006.connect() as connection:
    db_df = pd.read_sql('SELECT SKU FROM an1004', con=connection)

    # 读取Excel文件，将第三行设为列名
    df2_AN1004 = pd.read_excel(r"D:\数据源\Test1\PO231202AN1004-聚进加工单(2)(1).xlsx",
                               sheet_name='（运营）采购订单', header=2)
    # # 筛选出"订单数量"大于0且"SKU"在数据库中存在的行
    df2_AN1004 = df2_AN1004[(df2_AN1004['订单数量'] > 0) & (df2_AN1004['SKU'].isin(db_df['SKU']))]

    # 将'订单数量'列的数据添加到数据库中
    for index, row in df2_AN1004.iterrows():
        sql = text(f"UPDATE an1004 SET 订单数量 = :order_quantity WHERE SKU = :sku")
        params = {'order_quantity': row['订单数量'], 'sku': row['SKU']}
        connection.execute(sql, params)

with engine_an4006.connect() as connection:
    db_df = pd.read_sql('SELECT SKU FROM an1004', con=connection)

    # 读取Excel文件，将第一行设为列名
    df3_AN1004 = pd.read_excel(r"D:\数据源\Test1\PO231202AN1004-聚进加工单(2)(1).xlsx",
                               sheet_name='（仓库）批量导入库数据模板', header=0)

    # 筛选出"*SKU"列的数据在数据库中存在的行
    df3_AN1004 = df3_AN1004[df3_AN1004['*SKU'].isin(db_df['SKU'])]
    # 删除'*SKU'列中包含空值的行
    df3_AN1004 = df3_AN1004.dropna(subset=['*SKU'])

    # 将'可用量'列的数据添加到数据库中
    for index, row in df3_AN1004.iterrows():
        sql = text(f"UPDATE an1004 SET 可用量 = :available_quantity WHERE SKU = :sku")
        params = {'available_quantity': row['可用量'], 'sku': row['*SKU']}
        connection.execute(sql, params)

with engine_an4006.connect() as connection:
    trans = connection.begin()
    try:
        for index, row in df2_AN1004.iterrows():
            # 更新'订单数量'列
            sql_order_quantity = text(f"UPDATE an1004 SET 订单数量 = :order_quantity WHERE SKU = :sku")
            params_order_quantity = {'order_quantity': row['订单数量'], 'sku': row['SKU']}
            connection.execute(sql_order_quantity, params_order_quantity)
    except:
        trans.rollback()
        raise



    try:
        for index, row in df3_AN1004.iterrows():
            # 更新'可用量'列
            sql_available_quantity = text(f"UPDATE an1004 SET 可用量 = :available_quantity WHERE SKU = :sku")
            params_available_quantity = {'available_quantity': row['可用量'], 'sku': row['*SKU']}
            connection.execute(sql_available_quantity, params_available_quantity)

        trans.commit()
    except:
        trans.rollback()
        raise



# 读取整个Excel文件
df_full = pd.read_excel(r"D:\数据源\Test1\PO231202AN1004-聚进加工单(2)(1).xlsx", sheet_name='MySQLdata')

# 创建一个新的DataFrame，只包含你需要的行和列
df01 = df_full.iloc[[1], :49]

# 定义数据库连接信息
db_user = 'root'
db_password = '970823'
db_host = 'localhost'
db_name = 'an4006'

# 创建SQLAlchemy引擎并连接到MySQL数据库
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4")

# 执行SQL命令
with engine.begin() as connection:
    connection.execute(text("ALTER TABLE an1004 MODIFY condition_type VARCHAR(255);"))

# 添加SKU列
df01['SKU'] = df_full.loc[0, 'parent_sku']

# 复制'SKU'列的数据到新的'item_sku'列

df01['item_sku'] = df01['SKU']
# 将df01导入到数据库中
df01.to_sql('an1004', con=engine_an4006, if_exists='append', index=False)
