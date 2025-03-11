from typing import List, Dict, Any
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
import calendar
import re

class ReportService:
    # 事项类型映射
    EXPENSE_TYPES = {
        "meal": "餐饮费",
        "taxi": "交通费",
        "highway": "高速费",
        "accommodation": "住宿费",
        "office": "办公用品",
        "other": "其他"
    }

    @staticmethod
    def _convert_expense_type(type_code: str) -> str:
        """
        将事项类型代码转换为中文名称
        :param type_code: 事项类型代码
        :return: 中文名称
        """
        return ReportService.EXPENSE_TYPES.get(type_code, "其他")

    @staticmethod
    def generate_business_trip_report(name: str, month: str, dates: List[str]) -> BytesIO:
        """
        生成出差统计Excel报表
        :param name: 出差人姓名
        :param month: 年月（YYYY-MM格式）
        :param dates: 出差日期列表
        :return: Excel文件的二进制数据
        """
        try:
            # 解析年月
            year_month = datetime.strptime(month, "%Y-%m")
            year = year_month.year
            month_num = year_month.month
            
            # 获取该月的天数
            _, days_in_month = calendar.monthrange(year, month_num)
            
            # 创建一个新的Excel writer，指定使用xlsxwriter引擎并设置编码为utf-8
            output = BytesIO()
            writer = pd.ExcelWriter(
                output, 
                engine='xlsxwriter',
                engine_kwargs={'options': {'encoding': 'utf-8'}}
            )
            workbook = writer.book
            
            # 设置标题格式（浅蓝背景，深色文字）
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#BDD7EE',  # 浅蓝色背景
                'font_color': '#000000',  # 黑色文字
                'border': 1
            })

            # 设置日期单元格格式
            cell_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '#,##0;-#,##0;0;@'  # 整数不显示小数点，0显示为0，文本保持原样
            })

            # 设置出差标记格式（浅黄色背景）
            mark_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'bg_color': '#FFEB9C',  # 浅黄色背景
                'num_format': '#,##0;-#,##0;0;@'
            })
            
            # 设置小数格式（用于显示小数的单元格）
            decimal_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '#,##0.0;-#,##0.0;0;@'  # 小数保留一位，0显示为0，文本保持原样
            })

            # 创建实际天数的日期列表（表头）
            days = list(range(1, days_in_month + 1))
            columns = ['姓名'] + [str(d) for d in days] + ['总天数(天)']

            # 创建数据框
            df = pd.DataFrame(columns=columns)
            
            # 添加出差人数据
            row_data = {'姓名': name}
            total_days = 0
            
            # 过滤有效的日期
            valid_dates = []
            for date_str in dates:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if date_obj.year == year and date_obj.month == month_num and 1 <= date_obj.day <= days_in_month:
                        valid_dates.append(date_str)
                except ValueError:
                    # 忽略无效日期
                    continue
            
            # 填充日期数据
            for day in days:
                date_str = f"{month}-{day:02d}"
                if date_str in valid_dates:
                    row_data[str(day)] = 1
                    total_days += 1
                else:
                    row_data[str(day)] = ''
            
            row_data['总天数(天)'] = total_days
            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)

            # 处理工作表名称，确保不包含特殊字符并且长度不超过31
            try:
                # 尝试使用pypinyin将中文转换为拼音（如果安装了pypinyin）
                try:
                    from pypinyin import lazy_pinyin
                    pinyin_list = lazy_pinyin(f"{month}出差统计表")
                    sheet_name = ''.join(pinyin_list)
                except ImportError:
                    # 如果没有安装pypinyin，则使用原始名称
                    sheet_name = f"{month}出差统计表"
                    # 移除可能导致问题的字符
                    sheet_name = ''.join(c for c in sheet_name if c.isalnum() or c in '-_')
            except Exception:
                # 如果转换失败，使用安全的英文名称
                sheet_name = f"BusinessTrip{month}"

            # 确保长度不超过31
            if len(sheet_name) > 31:
                sheet_name = sheet_name[:31]
            # 如果sheet_name为空，使用默认名称
            if not sheet_name:
                sheet_name = "BusinessTripReport"
            
            # 写入Excel，但从第2行开始，为表头留出空间
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=1, header=False)
            worksheet = writer.sheets[sheet_name]

            # 合并单元格并写入标题（年月）
            title = f"{year}年{month_num}月出差统计表（天）"
            
            # 写入并合并姓名列表头
            worksheet.merge_range(0, 0, 1, 0, '姓名', header_format)
            
            # 写入年月标题到日期区域
            worksheet.merge_range(0, 1, 0, days_in_month, title, header_format)
            
            # 写入日期数字（1-31）
            for col in range(1, days_in_month + 1):
                worksheet.write(1, col, str(col), header_format)
            
            # 写入并合并总天数列的表头
            worksheet.merge_range(0, days_in_month + 1, 1, days_in_month + 1, '总天数(天)', header_format)

            # 设置列宽
            worksheet.set_column(0, 0, 15)  # 姓名列
            worksheet.set_column(1, days_in_month, 4)  # 日期列宽度设为4
            worksheet.set_column(days_in_month + 1, days_in_month + 1, 10)  # 总天数列

            # 写入数据（根据数值类型使用不同的格式）
            for row in range(2, len(df) + 2):  # 从第3行开始写数据
                for col in range(len(columns)):
                    value = df.iloc[row-2][columns[col]]
                    if value != '':  # 只有非空值才进行格式化
                        try:
                            if isinstance(value, (int, float)):
                                # 判断是否为整数
                                if float(value).is_integer():
                                    if col > 0 and col <= days_in_month and value == 1:
                                        # 出差日期使用标记格式
                                        worksheet.write(row, col, int(value), mark_format)
                                    else:
                                        worksheet.write(row, col, int(value), cell_format)
                                else:
                                    worksheet.write(row, col, round(float(value), 1), decimal_format)
                            else:
                                worksheet.write(row, col, value, cell_format)
                        except:
                            worksheet.write(row, col, value, cell_format)
                    else:
                        worksheet.write(row, col, value, cell_format)

            # 保存文件
            writer.close()
            output.seek(0)
            
            return output
        except Exception as e:
            # 记录错误并重新抛出
            print(f"生成出差报表时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            raise 

    @staticmethod
    def generate_expense_report(name: str, month: str, expense_items: List[Dict[str, Any]]) -> BytesIO:
        """
        生成报销明细Excel报表
        :param name: 填报人姓名
        :param month: 报销周期（YYYY/MM格式）
        :param expense_items: 报销明细列表
        :return: Excel文件的二进制数据
        """
        try:
            # 创建一个新的Excel writer
            output = BytesIO()
            writer = pd.ExcelWriter(
                output, 
                engine='xlsxwriter',
                engine_kwargs={'options': {'encoding': 'utf-8'}}
            )
            workbook = writer.book

            # 设置标题格式（浅蓝背景，深色文字）
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#BDD7EE',  # 浅蓝色背景
                'font_color': '#000000',  # 黑色文字
                'border': 1
            })

            # 设置单元格格式
            cell_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'text_wrap': True  # 允许文本换行
            })

            # 设置金额格式
            amount_format = workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'border': 1,
                'num_format': '#,##0.00'  # 金额格式（保留两位小数）
            })

            # 创建数据框
            df = pd.DataFrame(columns=['序号', '日期', '事项', '事由', '发票金额', '发票号', '备注'])
            
            # 添加报销明细数据
            for i, item in enumerate(expense_items, 1):
                df = pd.concat([df, pd.DataFrame([{
                    '序号': i,
                    '日期': item['date'],
                    '事项': ReportService._convert_expense_type(item['type']),
                    '事由': item['reason'],
                    '发票金额': item['amount'],
                    '发票号': item['invoice_no'],
                    '备注': item['remark']
                }])], ignore_index=True)

            # 计算合计金额
            total_amount = df['发票金额'].sum()
            df = pd.concat([df, pd.DataFrame([{
                '序号': '',
                '日期': '',
                '事项': '',
                '事由': '',
                '发票金额': total_amount,
                '发票号': '',
                '备注': ''
            }])], ignore_index=True)

            # 处理工作表名称
            try:
                # 从月份中提取年月
                year_month = month.replace('/', '')
                sheet_name = f"{year_month}报销明细"
                
                # 移除所有不允许的字符
                sheet_name = re.sub(r'[\\/*?:\[\]]', '', sheet_name)
                
                # 确保长度不超过31
                if len(sheet_name) > 31:
                    sheet_name = sheet_name[:31]
                
                # 如果sheet_name为空或无效，使用默认名称
                if not sheet_name or not re.match(r'^[a-zA-Z0-9\u4e00-\u9fa5]+$', sheet_name):
                    sheet_name = "ExpenseReport"
            except Exception as e:
                print(f"处理工作表名称时出错: {str(e)}")
                sheet_name = "ExpenseReport"

            # 写入Excel
            df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2)  # 从第3行开始写入，为标题留出空间
            worksheet = writer.sheets[sheet_name]

            # 设置列宽
            worksheet.set_column('A:A', 8)   # 序号
            worksheet.set_column('B:B', 12)  # 日期
            worksheet.set_column('C:C', 12)  # 事项
            worksheet.set_column('D:D', 15)  # 事由
            worksheet.set_column('E:E', 12)  # 发票金额
            worksheet.set_column('F:F', 20)  # 发票号
            worksheet.set_column('G:G', 15)  # 备注

            # 合并单元格并写入标题
            title = "费用报销明细表"
            worksheet.merge_range('A1:G1', title, header_format)

            # 写入填报人和报销周期
            worksheet.merge_range('A2:B2', f"填报人：{name}", cell_format)
            worksheet.merge_range('F2:G2', f"报销周期：{month}", cell_format)

            # 写入表头
            headers = ['序号', '日期', '事项', '事由', '发票金额', '发票号', '备注']
            for col, header in enumerate(headers):
                worksheet.write(2, col, header, header_format)

            # 写入数据并应用格式
            for row in range(len(df)):
                row_data = df.iloc[row]
                for col in range(len(headers)):
                    value = row_data[headers[col]]
                    # 对最后一行（合计行）特殊处理
                    if row == len(df) - 1:
                        if col == 4:  # 发票金额列
                            worksheet.write(row + 3, col, value, amount_format)
                        else:
                            worksheet.write(row + 3, col, value, cell_format)
                    else:
                        if col == 4:  # 发票金额列
                            worksheet.write(row + 3, col, value, amount_format)
                        else:
                            worksheet.write(row + 3, col, value, cell_format)

            # 保存文件
            writer.close()
            output.seek(0)
            
            return output
        except Exception as e:
            # 记录错误并重新抛出
            print(f"生成报销明细报表时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            raise 