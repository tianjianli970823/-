import pandas as pd
import re
import xlwings as xw

# 打开 Excel 文件
book = xw.Book(r"D:\数据源\PO下单表-数据源\PO231131AN1014-美致加工单-1月8日出货.xlsx")

# 选择工作表
sheet = book.sheets['（运营）数据源']

# 获取列名
column_names = sheet.range('1:1').value

# 找到 "颜色" 列的位置
color_column_index = column_names.index('颜色') + 1  # 加 1 是因为 Excel 的列索引是从 1 开始的

# 获取 "颜色" 列的数据
color_column_data = sheet.range(f'{chr(64 + color_column_index)}2:{chr(64 + color_column_index)}1048576').value

# 检查每个单元格的数据，如果是标量就转换为列表
color_column_data = [data if isinstance(data, list) else [data] for data in color_column_data]

# 将列表转换为 pandas.Series
color_column_data = pd.Series(color_column_data)


# 将非字符串类型的值转换为字符串
color_column_data = color_column_data.astype(str)

# 创建一个函数来提取字符串中的中文部分
def extract_chinese(s):
    return ''.join(re.findall(r'[\u4e00-\u9fff]+', s))

# 应用这个函数到 "颜色" 列
color_column_data = color_column_data.apply(extract_chinese)

# 将修改后的 "颜色" 列数据写回 Excel 文件
for i in range(len(color_column_data)):
    sheet.range(f'{chr(64 + color_column_index)}{i+2}').value = color_column_data[i]

# 保存并关闭 Excel 文件
book.save()
book.close()
