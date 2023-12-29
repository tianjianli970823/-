import pandas as pd
from sqlalchemy import create_engine

import pymysql

# 定义数据库连接信息
db_user = 'root'
db_password = '970823'
db_host = 'localhost'
db_name = '仓库'

# 创建数据库连接
connection = pymysql.connect(host=db_host,
                             user=db_user,
                             password=db_password,
                             db=db_name)

try:
    with connection.cursor() as cursor:
        # 检查表是否存在，如果存在则删除
        sql = """
        DROP TABLE IF EXISTS `仓库`.`an1014`;
        """
        cursor.execute(sql)

        # 创建新表
        sql = """
        CREATE TABLE `仓库`.`an1014` AS SELECT `SKU`, `FNSKU`,`ASIN`,`size_name`,`店铺`,`产品负责人`,`订单数量`,`可用量`,`颜色`,`item_name` FROM `an4006`.`an1014`;
        """
        cursor.execute(sql)

        # 在新表中添加新列
        sql = """
        ALTER TABLE `an1014` ADD `实际发货数量` INT;
        """
        cursor.execute(sql)

    # 提交事务
    connection.commit()
finally:
    # 关闭数据库连接
    connection.close()


import pandas as pd
from sqlalchemy import create_engine

# 定义数据库连接信息
db_user = 'root'
db_password = '970823'
db_host = 'localhost'
db_name = '仓库'

# 创建数据库引擎
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}')

# 从数据库中读取数据
df_db = pd.read_sql('SELECT * FROM an1014', con=engine)

# 读取Excel文件
df_excel = pd.read_excel('D:\\数据源\\PO下单表-数据源\\12.25-AN-空派.xlsx', sheet_name='工作表')

# 将“SKU（抓取）”列的数据和“数量（输入）”列的数据进行分组，并计算每组的总和
df_excel = df_excel.groupby('SKU（抓取）')['数量（输入）'].sum().reset_index()

# 将Excel文件中的数据和数据库中的数据进行比对，并更新数据库中的数据
for i, row in df_excel.iterrows():
    df_db.loc[df_db['SKU'] == row['SKU（抓取）'], '实际发货数量'] = row['数量（输入）']

# 将更新后的数据写回数据库
df_db.to_sql('an1014', con=engine, schema='仓库', if_exists='replace', index=False)
