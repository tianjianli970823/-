import pandas as pd
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# 读取AN4076产品的Excel文件
df_AN4076 = pd.read_excel(r"D:\数据源\PO下单表-数据源\PO230000NT4076-1(佳韵加工厂-包工包料)(1).xlsx", sheet_name='（运营）数据源')

# 更改列名
df_AN4076 = df_AN4076.rename(columns={'SKU ': 'SKU'})
df_AN4076 = df_AN4076.loc[:, 'SKU':'布行']
df_AN4076 = df_AN4076.dropna(subset=['颜色'])
df_AN4076['款号'] = df_AN4076['款号'].replace('NT4076', 'AN4076')
df_AN4076['SKU'] = df_AN4076['SKU'].str.replace('NT4076', 'AN4076') + '-CD-DE'

# 定义尺码的顺序
size_order = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']

# 将尺码列转换为Categorical类型
df_AN4076['尺码'] = pd.Categorical(df_AN4076['尺码'], categories=size_order, ordered=True)

# 首先按照色号分类，然后按照尺码列排序
df_AN4076 = df_AN4076.sort_values(['色号', '尺码'])

# 创建SQLAlchemy引擎并连接到MySQL服务器
engine = create_engine("mysql+pymysql://root:970823@localhost/?charset=utf8mb4")

# 创建一个新的数据库
with engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS an4006 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))

# 创建一个新的SQLAlchemy引擎，连接到an4006数据库
engine_an4006 = create_engine("mysql+pymysql://root:970823@localhost/an4006?charset=utf8mb4")

# 使用to_sql函数将数据框写入数据库
df_AN4076.to_sql('an4076', con=engine_an4006, if_exists='replace', index=False)

# 读取"亚马逊资料"表
df_amazon = pd.read_excel(r"D:\数据源\PO下单表-数据源\PO230000NT4076-1(佳韵加工厂-包工包料)(1).xlsx", sheet_name='亚马逊资料')

# 检查"feed_product_type"列是否存在
if 'feed_product_type' in df_amazon.columns:
    # 获取"feed_product_type"列的第一行数据
    feed_product_type_value = df_amazon['feed_product_type'].iloc[0]

    # 将这个值添加到df_AN4076数据框的每一行
    df_AN4076['feed_product_type'] = feed_product_type_value

    # 将更新后的数据框写入数据库
    df_AN4076.to_sql('an4076', con=engine_an4006, if_exists='replace', index=False)
else:
    print("列'feed_product_type'在'亚马逊资料'表中不存在。")

# 检查"brand_name"列是否存在
if 'brand_name' in df_amazon.columns:
    # 获取"brand_name"列的第一行数据
    brand_name_value = df_amazon['brand_name'].iloc[0]

    # 将这个值添加到df_AN4076数据框的每一行
    df_AN4076['brand_name'] = brand_name_value

    # 将更新后的数据框写入数据库
    df_AN4076.to_sql('an4076', con=engine_an4006, if_exists='replace', index=False)
else:
    print("列'brand_name'在'亚马逊资料'表中不存在。")

if 'update_delete' in df_amazon.columns:
    update_delete_value = df_amazon['update_delete'].iloc[0]
    df_AN4076['update_delete'] = update_delete_value
    df_AN4076.to_sql('an4076', con=engine_an4006, if_exists='replace', index=False)

else:
    print("列'update_delete'在‘'亚马逊资料'表中不存在。")

