import pandas as pd
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# 读取AN811产品的Excel文件
df_AN811 = pd.read_excel(r"D:\数据源\PO下单表-数据源\TZ811下单新模板-展翼-23.11.23 嘉豪.xlsx", sheet_name='（运营）数据源')

# 更改列名
df_AN811 = df_AN811.rename(columns={'SKU ': 'SKU'})
df_AN811 = df_AN811.loc[:, 'SKU':'布行']
df_AN811 = df_AN811.dropna(subset=['颜色'])
df_AN811['款号'] = df_AN811['款号'].replace('TZ811', 'AN811')
df_AN811['SKU'] = df_AN811['SKU'].str.replace('TZ811', 'AN811') + '-CD-DE'

# 定义尺码的顺序
size_order = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']

# 将尺码列转换为Categorical类型
df_AN811['尺码'] = pd.Categorical(df_AN811['尺码'], categories=size_order, ordered=True)

# 首先按照色号分类，然后按照尺码列排序
df_AN811 = df_AN811.sort_values(['色号', '尺码'])

# 创建SQLAlchemy引擎并连接到MySQL服务器
engine = create_engine("mysql+pymysql://root:970823@localhost/?charset=utf8mb4")

# 创建一个新的数据库
with engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS an4006 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))

# 创建一个新的SQLAlchemy引擎，连接到an4006数据库
engine_an4006 = create_engine("mysql+pymysql://root:970823@localhost/an4006?charset=utf8mb4")

# 使用to_sql函数将数据框写入数据库
df_AN811.to_sql('an811', con=engine_an4006, if_exists='replace', index=False)
