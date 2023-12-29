# CMD
# mysql> CREATE DATABASE 仓库;
#
#

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
        # 创建新表
        sql = """
        CREATE TABLE `仓库`.`an1014` AS SELECT `SKU`, `FNSKU`,`ASIN`,`size_name`,`店铺`,`产品负责人`,`订单数量`,`可用量` FROM `an4006`.`an1014`;
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