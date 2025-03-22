import pandas as pd
from datetime import datetime, timedelta
import uuid
import os
from typing import Dict, List, Any
from models.schemas import ExcelPreview, PaginatedData
import math
import calendar
from chinese_calendar import is_workday
from services.settings_service import settings_service

class ExcelService:
    def __init__(self):
        self.upload_dir = "uploads/excel"
        os.makedirs(self.upload_dir, exist_ok=True)
        self.files: Dict[str, Dict[str, Any]] = {}  # 存储文件ID和文件信息的映射
        self.file_cache: Dict[str, pd.DataFrame] = {}

    def ensure_upload_dir(self):
        """确保上传目录存在"""
        os.makedirs(self.upload_dir, exist_ok=True)
        
    def check_and_clean_files(self):
        """检查文件数量，如果超过最大值则清理旧文件"""
        try:
            # 获取最大文件数量设置
            max_files = settings_service.get_max_files()
            
            # 获取上传目录中的所有文件
            files = [f for f in os.listdir(self.upload_dir) if os.path.isfile(os.path.join(self.upload_dir, f))]
            
            # 如果文件数量超过最大值，清理旧文件
            if len(files) > max_files:
                print(f"文件数量({len(files)})超过最大值({max_files})，开始清理旧文件")
                
                # 获取文件的创建时间
                file_times = []
                for file in files:
                    file_path = os.path.join(self.upload_dir, file)
                    # 获取文件的创建时间或修改时间
                    ctime = os.path.getctime(file_path)
                    file_times.append((file, ctime))
                
                # 按创建时间排序
                file_times.sort(key=lambda x: x[1])
                
                # 计算需要删除的文件数量
                files_to_delete = len(files) - max_files
                
                # 删除最旧的文件
                for i in range(files_to_delete):
                    file_to_delete = file_times[i][0]
                    file_path = os.path.join(self.upload_dir, file_to_delete)
                    try:
                        os.remove(file_path)
                        print(f"已删除旧文件: {file_to_delete}")
                    except Exception as e:
                        print(f"删除文件 {file_to_delete} 失败: {str(e)}")
                
                print(f"文件清理完成，已删除 {files_to_delete} 个文件")
        except Exception as e:
            print(f"检查和清理文件时出错: {str(e)}")
            
    def process_headers(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """处理表头信息
        
        Args:
            df: pandas DataFrame对象
            
        Returns:
            List[Dict[str, Any]]: 处理后的表头信息列表，每个表头包含：
                - key: 列的原始名称
                - label: 显示的标签
                - type: 数据类型
                - width: 建议的列宽度
        """
        headers = []
        for col in df.columns:
            try:
                # 获取列的数据类型
                col_type = 'string'  # 默认为字符串类型
                
                # 安全地获取列数据
                col_data = df[col].copy()
                
                # 检查数据类型
                if pd.api.types.is_numeric_dtype(col_data):
                    col_type = 'number'
                elif pd.api.types.is_datetime64_any_dtype(col_data):
                    col_type = 'datetime'
                
                # 计算建议的列宽度（基于内容长度）
                # 计算表头长度
                header_length = len(str(col))
                
                # 安全地计算数据最大长度
                try:
                    data_length = col_data.astype(str).str.len().max()
                    if pd.isna(data_length):
                        data_length = 0
                except:
                    data_length = 0
                
                max_length = max(header_length, data_length)
                
                # 设置最小宽度100，最大宽度300
                suggested_width = min(max(100, max_length * 15), 300)
                
                headers.append({
                    'key': str(col),
                    'label': str(col),
                    'type': col_type,
                    'width': suggested_width
                })
            except Exception as e:
                print(f"处理列 {col} 时出错: {str(e)}")
                # 如果处理出错，添加一个基本的列信息
                headers.append({
                    'key': str(col),
                    'label': str(col),
                    'type': 'string',
                    'width': 100
                })
        
        return headers

    async def process_upload(self, file, file_type: str) -> ExcelPreview:
        """处理上传的Excel文件并返回预览数据
        
        Args:
            file: 上传的文件对象
            file_type: 文件类型，'overtime' 或 'leave'
            
        Returns:
            ExcelPreview: 文件预览数据
        """
        # 检查并清理文件
        self.check_and_clean_files()
        
        # 生成唯一文件ID
        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_dir, f"{file_id}.xlsx")
        
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 存储文件映射
        self.files[file_id] = {
            'path': file_path,
            'name': file.filename,
            'type': file_type
        }
        
        # 读取Excel文件，不使用第一行作为表头
        df = pd.read_excel(file_path, header=None)
        
        # 使用第一行作为列名
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)
        
        # 存入缓存
        self.file_cache[file_id] = df
        
        # 处理表头信息
        headers = self.process_headers(df)
        
        # 生成预览数据
        preview = ExcelPreview(
            headers=headers,
            sample_data=df.head(10).to_dict('records'),
            total_rows=len(df),
            file_id=file_id
        )
        
        return preview

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗数据"""
        # 删除完全为空的行
        df = df.dropna(how='all')
        
        # 删除重复行
        df = df.drop_duplicates()
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        return df

    def format_date_columns(self, df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """格式化日期列"""
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[col] = df[col].dt.strftime('%Y-%m-%d')
        return df

    def format_numeric_columns(self, df: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
        """格式化数字列"""
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

    def categorize_data(self, df: pd.DataFrame, category_column: str) -> Dict[str, pd.DataFrame]:
        """按类别分类数据"""
        if category_column not in df.columns:
            raise ValueError(f"列 {category_column} 不存在")
        
        return {name: group for name, group in df.groupby(category_column)}

    def export_excel(self, df: pd.DataFrame, file_path: str):
        """导出数据到Excel文件"""
        df.to_excel(file_path, index=False)

    async def process_file(self, file_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """处理Excel文件"""
        if file_id not in self.files:
            raise ValueError("文件不存在")
        
        file_path = self.files[file_id]['path']
        df = pd.read_excel(file_path)
        
        # 数据清洗
        df = self.clean_data(df)
        
        # 格式化日期列
        if 'date_columns' in config:
            df = self.format_date_columns(df, config['date_columns'])
        
        # 格式化数字列
        if 'numeric_columns' in config:
            df = self.format_numeric_columns(df, config['numeric_columns'])
        
        # 按类别分类数据
        categorized_data = None
        if 'category_column' in config:
            try:
                categorized_data = self.categorize_data(df, config['category_column'])
            except ValueError as e:
                pass
        
        # 生成统计信息
        stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_types": df.dtypes.astype(str).to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
        }
        
        # 如果有分类数据，添加分类统计
        if categorized_data:
            stats["categories"] = {
                category: len(data) for category, data in categorized_data.items()
            }
        
        # 导出处理后的数据
        output_path = os.path.join(self.upload_dir, f"processed_{file_id}.xlsx")
        self.export_excel(df, output_path)
        
        return {
            "stats": stats,
            "processed_file": output_path
        }

    async def get_paginated_data(self, file_id: str, page: int, size: int) -> PaginatedData:
        """
        获取Excel文件的分页数据
        
        参数:
        - file_id: 文件ID
        - page: 页码，从1开始
        - size: 每页数量
        
        返回:
        - PaginatedData: 分页后的数据
        """
        try:
            # 检查文件ID是否存在
            if file_id not in self.files:
                raise ValueError(f"文件ID {file_id} 不存在")

            # 获取文件路径
            file_path = self.files[file_id]['path']
            if not os.path.exists(file_path):
                # 如果文件不存在，清理缓存
                if file_id in self.file_cache:
                    del self.file_cache[file_id]
                if file_id in self.files:
                    del self.files[file_id]
                raise ValueError(f"文件 {file_path} 不存在")

            # 如果数据不在缓存中，则读取文件
            if file_id not in self.file_cache:
                try:
                    # 读取Excel文件，不使用第一行作为表头
                    df = pd.read_excel(file_path, header=None)
                    # 使用第一行作为列名
                    df.columns = df.iloc[0]
                    df = df.iloc[1:].reset_index(drop=True)
                    self.file_cache[file_id] = df
                except Exception as e:
                    raise ValueError(f"读取文件失败: {str(e)}")
            else:
                df = self.file_cache[file_id]

            # 计算分页信息
            total = len(df)
            total_pages = math.ceil(total / size)
            
            # 验证页码是否有效
            if page < 1 or page > total_pages:
                raise ValueError(f"页码 {page} 无效，总页数为 {total_pages}")
            
            start_idx = (page - 1) * size
            end_idx = min(start_idx + size, total)

            # 获取当前页的数据
            page_data = df.iloc[start_idx:end_idx]
            items = page_data.to_dict('records')

            # 处理表头信息
            headers = self.process_headers(df)

            return PaginatedData(
                items=items,
                total=total,
                page=page,
                size=size,
                total_pages=total_pages,
                headers=headers
            )
        except Exception as e:
            raise ValueError(str(e))

    async def delete_file(self, file_id: str) -> None:
        """
        删除Excel文件及其相关数据
        
        参数:
        - file_id: 文件ID
        
        异常:
        - ValueError: 文件不存在时抛出
        """
        # 检查文件是否存在
        file_path = self.files[file_id]['path']
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_id} 不存在")
        
        try:
            # 删除物理文件
            os.remove(file_path)
            
            # 清理缓存
            if file_id in self.file_cache:
                del self.file_cache[file_id]
            if file_id in self.files:
                del self.files[file_id]
                
        except Exception as e:
            raise Exception(f"删除文件失败: {str(e)}")

    async def export_overtime(self, file_ids: List[str]) -> str:
        """
        导出加班记录
        
        参数:
        - file_ids: 要导出的文件ID列表
        
        返回:
        - str: 导出文件的路径
        """
        try:
            # 读取并合并所有加班记录
            dfs = []
            for file_id in file_ids:
                if file_id not in self.file_cache:
                    if file_id not in self.files:
                        print(f"文件ID {file_id} 不存在于files映射中")
                        continue
                    file_path = self.files[file_id]['path']
                    if not os.path.exists(file_path):
                        print(f"文件 {file_path} 不存在")
                        continue
                    try:
                        df = pd.read_excel(file_path)
                        print(f"成功读取文件 {file_path}")
                        print(f"列名: {df.columns.tolist()}")
                        dfs.append(df)
                    except Exception as e:
                        print(f"读取文件 {file_path} 失败: {str(e)}")
                else:
                    df = self.file_cache[file_id]
                    print(f"从缓存中获取文件 {file_id}")
                    print(f"列名: {df.columns.tolist()}")
                    dfs.append(df)
            
            if not dfs:
                raise ValueError("没有找到可导出的加班记录")
            
            # 合并所有数据
            merged_df = pd.concat(dfs, ignore_index=True)
            print(f"合并后的列名: {merged_df.columns.tolist()}")
            
            # 只保留需要的列
            required_columns = ['加班人', '开始时间', '结束时间', '时长', '加班原因']
            # 检查所需列是否存在，如果不存在则跳过
            existing_columns = [col for col in required_columns if col in merged_df.columns]
            if not existing_columns:
                raise ValueError(f"未找到所需的列名。当前列名: {merged_df.columns.tolist()}")
            
            print(f"找到的列: {existing_columns}")
            merged_df = merged_df[existing_columns]
            
            # 生成当前年月日的文件名
            current_date = datetime.now()
            year_month_day = current_date.strftime('%Y%m%d')
            
            # 确保上传目录存在
            self.ensure_upload_dir()
            
            export_file = os.path.join(self.upload_dir, f"{year_month_day}加班记录.xlsx")
            print(f"准备导出到文件: {export_file}")
            
            # 导出到Excel
            merged_df.to_excel(export_file, index=False)
            print(f"成功导出到文件: {export_file}")
            
            return export_file
        except Exception as e:
            print(f"导出加班记录时发生错误: {str(e)}")
            raise ValueError(f"导出加班记录失败: {str(e)}")

    async def export_leave(self, file_ids: List[str]) -> str:
        """
        导出请假记录
        
        参数:
        - file_ids: 要导出的文件ID列表
        
        返回:
        - str: 导出文件的路径
        """
        try:
            # 读取并合并所有请假记录
            dfs = []
            for file_id in file_ids:
                if file_id not in self.file_cache:
                    if file_id not in self.files:
                        print(f"文件ID {file_id} 不存在于files映射中")
                        continue
                    file_path = self.files[file_id]['path']
                    if not os.path.exists(file_path):
                        print(f"文件 {file_path} 不存在")
                        continue
                    try:
                        df = pd.read_excel(file_path)
                        print(f"成功读取文件 {file_path}")
                        print(f"列名: {df.columns.tolist()}")
                        dfs.append(df)
                    except Exception as e:
                        print(f"读取文件 {file_path} 失败: {str(e)}")
                else:
                    df = self.file_cache[file_id]
                    print(f"从缓存中获取文件 {file_id}")
                    print(f"列名: {df.columns.tolist()}")
                    dfs.append(df)
            
            if not dfs:
                raise ValueError("没有找到可导出的请假记录")
            
            # 合并所有数据
            merged_df = pd.concat(dfs, ignore_index=True)
            print(f"合并后的列名: {merged_df.columns.tolist()}")
            
            # 只保留需要的列
            required_columns = ['请假类型', '开始时间', '结束时间', '时长', '请假事由', '创建人']
            # 检查所需列是否存在，如果不存在则跳过
            existing_columns = [col for col in required_columns if col in merged_df.columns]
            if not existing_columns:
                raise ValueError(f"未找到所需的列名。当前列名: {merged_df.columns.tolist()}")
            
            print(f"找到的列: {existing_columns}")
            merged_df = merged_df[existing_columns]
            
            # 生成当前年月日的文件名
            current_date = datetime.now()
            year_month_day = current_date.strftime('%Y%m%d')
            
            # 确保上传目录存在
            self.ensure_upload_dir()
            
            export_file = os.path.join(self.upload_dir, f"{year_month_day}请假记录.xlsx")
            print(f"准备导出到文件: {export_file}")
            
            # 导出到Excel
            merged_df.to_excel(export_file, index=False)
            print(f"成功导出到文件: {export_file}")
            
            return export_file
        except Exception as e:
            print(f"导出请假记录时发生错误: {str(e)}")
            raise ValueError(f"导出请假记录失败: {str(e)}")

    async def export_attendance(self, file_ids: List[str]) -> str:
        """
        导出考勤记录
        """
        try:
            # 定义计算天数的函数
            def calculate_days(total_hours):
                # 如果总时长为负数，说明请假时长大于加班时长
                if total_hours < 0:
                    # 取绝对值后计算
                    abs_hours = abs(total_hours)
                    # 计算整天数
                    full_days = abs_hours // 8
                    # 计算余下的小时数
                    remaining_hours = abs_hours % 8
                    
                    # 根据余下的小时数调整天数
                    if remaining_hours > 4:
                        full_days += 1
                    elif remaining_hours == 4:
                        full_days += 0.5
                        
                    # 返回负数天数
                    return -full_days
                else:
                    # 正数时长的处理保持不变
                    if total_hours < 4:
                        return 0
                    elif total_hours == 4:
                        return 0.5
                    else:
                        # 计算整天数
                        full_days = total_hours // 8
                        # 计算余下的小时数
                        remaining_hours = total_hours % 8
                        
                        # 根据余下的小时数调整天数
                        if remaining_hours > 4:
                            full_days += 1
                        elif remaining_hours == 4:
                            full_days += 0.5
                            
                        return full_days

            print(f"开始处理考勤记录导出，文件ID列表: {file_ids}")
            
            # 创建一个列表存储所有开始时间
            all_start_times = []
            
            # 首先遍历所有文件，收集开始时间
            for file_id in file_ids:
                if file_id not in self.files:
                    print(f"文件ID {file_id} 不存在")
                    continue
                    
                file_info = self.files[file_id]
                print(f"处理文件: {file_info['name']}")
                
                try:
                    # 从缓存或文件系统读取数据
                    if file_id in self.file_cache:
                        df = self.file_cache[file_id]
                    else:
                        df = pd.read_excel(file_info['path'])
                        self.file_cache[file_id] = df
                    
                    # 确定文件类型
                    file_type = 'unknown'
                    if any(col in df.columns for col in ['加班人', '加班时长']):
                        file_type = 'overtime'
                    elif any(col in df.columns for col in ['创建人', '请假时长', '请假类型']):
                        file_type = 'leave'
                    
                    # 收集开始时间
                    if '开始时间' in df.columns:
                        # 提取日期部分（去掉上午/下午）
                        start_times = df['开始时间'].apply(lambda x: str(x).split()[0] if pd.notna(x) else None)
                        start_times = pd.to_datetime(start_times, errors='coerce')
                        all_start_times.extend(start_times.dropna())
                
                except Exception as e:
                    print(f"处理文件出错: {str(e)}")
                    continue
            
            if not all_start_times:
                raise ValueError("没有找到有效的开始时间")
            
            # 将所有开始时间转换为pandas的时间序列
            time_series = pd.Series(all_start_times)
            
            # 获取出现最多的年月
            year_month_counts = time_series.dt.to_period('M').value_counts()
            if len(year_month_counts) == 0:
                raise ValueError("无法确定考勤统计月份")
            
            # 获取最常见的年月
            most_common_year_month = year_month_counts.index[0]
            target_year = most_common_year_month.year
            target_month = most_common_year_month.month
            
            # 获取目标月份的天数
            days_in_month = calendar.monthrange(target_year, target_month)[1]
            
            print(f"确定统计年月为: {target_year}年{target_month}月，共{days_in_month}天")
            
            # 创建一个空的DataFrame，列为日期
            columns = ['姓名'] + [str(i) for i in range(1, days_in_month + 1)] + \
                     ['加班时长', '调/请假', '总时长', '总时长(天)']
            result_df = pd.DataFrame(columns=columns)
            
            # 初始化一个字典来存储每个人的数据
            person_data = {}
            
            # 处理每个文件
            for file_id in file_ids:
                if file_id not in self.files:
                    print(f"文件ID {file_id} 不存在")
                    continue
                    
                file_info = self.files[file_id]
                print(f"处理文件: {file_info['name']}")
                
                try:
                    # 从缓存或文件系统读取数据
                    if file_id in self.file_cache:
                        df = self.file_cache[file_id]
                    else:
                        df = pd.read_excel(file_info['path'])
                        self.file_cache[file_id] = df
                    
                    print(f"数据行数: {len(df)}")
                    print(f"文件列名: {df.columns.tolist()}")
                    
                    # 确定文件类型
                    file_type = 'unknown'
                    if any(col in df.columns for col in ['加班人', '加班时长']):
                        file_type = 'overtime'
                    elif any(col in df.columns for col in ['创建人', '请假时长', '请假类型']):
                        file_type = 'leave'
                    print(f"文件类型: {file_type}")
                    
                    # 处理数据
                    if file_type == 'overtime':
                        print("处理加班记录...")
                        for _, row in df.iterrows():
                            name = row.get('加班人', row.get('姓名', '未知'))
                            try:
                                # 打印原始时间字符串以便调试
                                start_time_str = str(row.get('开始时间', ''))
                                print(f"处理 {name} 的加班记录，原始开始时间: {start_time_str}")
                                
                                # 尝试多种日期格式解析
                                try:
                                    start_time = pd.to_datetime(start_time_str, format='%Y-%m-%d %H:%M:%S')
                                except:
                                    try:
                                        start_time = pd.to_datetime(start_time_str, format='%Y/%m/%d %H:%M:%S')
                                    except:
                                        try:
                                            start_time = pd.to_datetime(start_time_str)
                                        except:
                                            print(f"无法解析时间格式: {start_time_str}")
                                            continue
                                
                                # 获取时长
                                duration_str = str(row.get('时长', '0'))
                                try:
                                    if '小时' in duration_str:
                                        duration = float(duration_str.replace('小时', ''))
                                    elif '天' in duration_str:
                                        duration = float(duration_str.replace('天', '')) * 8
                                    else:
                                        duration = float(duration_str)
                                except:
                                    print(f"无法解析时长: {duration_str}")
                                    continue
                                
                                if pd.isna(start_time):
                                    print(f"开始时间为空: {start_time_str}")
                                    continue
                                    
                                day = str(start_time.day)
                                print(f"解析成功 - 日期: {day}, 时长: {duration}")
                                
                                # 初始化该员工的数据
                                if name not in person_data:
                                    person_data[name] = {
                                        '姓名': name,
                                        '加班时长': 0,
                                        '调/请假': 0,
                                        '总时长': 0,
                                        '总时长(天)': 0
                                    }
                                
                                # 更新加班记录
                                if day not in person_data[name]:
                                    person_data[name][day] = 0
                                person_data[name][day] = int(person_data[name][day] + duration)
                                person_data[name]['加班时长'] += duration
                                
                            except Exception as e:
                                print(f"处理加班记录出错: {str(e)}")
                                continue
                            
                    elif file_type == 'leave':
                        print("处理请假记录...")
                        for _, row in df.iterrows():
                            name = row.get('创建人', row.get('姓名', '未知'))
                            try:
                                # 提取日期部分
                                start_time_str = str(row.get('开始时间', ''))
                                end_time_str = str(row.get('结束时间', ''))
                                duration_str = str(row.get('时长', '0'))

                                print(f"处理 {name} 的请假记录: {start_time_str} 到 {end_time_str}, 时长: {duration_str}")

                                # 解析时长
                                if '小时' in duration_str:
                                    duration = float(duration_str.replace('小时', ''))
                                elif '天' in duration_str:
                                    duration = float(duration_str.replace('天', '')) * 8
                                else:
                                    try:
                                        duration = float(duration_str)
                                    except:
                                        print(f"无法解析时长: {duration_str}")
                                        continue

                                # 获取开始和结束日期
                                start_date = pd.to_datetime(start_time_str.split()[0]).date()
                                end_date = pd.to_datetime(end_time_str.split()[0]).date()
                                
                                print(f"请假时间段: {start_date} 到 {end_date}")
                                
                                # 初始化该员工的数据
                                if name not in person_data:
                                    person_data[name] = {
                                        '姓名': name,
                                        '加班时长': 0,
                                        '调/请假': 0,
                                        '总时长': 0,
                                        '总时长(天)': 0
                                    }

                                # 如果总时长小于等于8小时，只记录在开始日期
                                if duration <= 8:
                                    if start_date.year == target_year and start_date.month == target_month:
                                        date_str = start_date.strftime('%Y-%m-%d')
                                        # 先判断是否是工作日
                                        if self.is_workday(date_str):
                                            day = str(start_date.day)
                                            if day not in person_data[name]:
                                                person_data[name][day] = 0
                                            person_data[name][day] = -duration
                                            person_data[name]['调/请假'] -= duration
                                            person_data[name]['总时长'] -= duration
                                else:
                                    # 对于多天请假，计算工作日天数并平均分配时长
                                    workdays_count = 0
                                    workdays = []
                                    current_date = start_date
                                    
                                    # 先统计工作日数量和收集工作日
                                    while current_date <= end_date:
                                        if current_date.year == target_year and current_date.month == target_month:
                                            date_str = current_date.strftime('%Y-%m-%d')
                                            if self.is_workday(date_str):
                                                workdays_count += 1
                                                workdays.append(current_date)
                                        current_date += timedelta(days=1)
                                    
                                    # 如果有工作日，则记录请假时间
                                    if workdays_count > 0:
                                        # 每个工作日记录8小时
                                        for work_date in workdays:
                                            day = str(work_date.day)
                                            if day not in person_data[name]:
                                                person_data[name][day] = 0
                                            person_data[name][day] = -8
                                            person_data[name]['调/请假'] -= 8
                                            person_data[name]['总时长'] -= 8

                                # 更新总时长(天)
                                person_data[name]['总时长(天)'] = calculate_days(person_data[name]['总时长'])
                                
                            except Exception as e:
                                print(f"处理请假记录时发生错误: {str(e)}")
                                continue
                
                except Exception as e:
                    print(f"处理文件出错: {str(e)}")
                    continue
            
            # 处理每个人的数据
            rows = []
            for name, data in person_data.items():
                row = {'姓名': name}
                # 填充每一天的数据
                for day in range(1, days_in_month + 1):
                    day_str = str(day)
                    row[day_str] = data.get(day_str, '') if data.get(day_str, 0) != 0 else ''
                
                # 计算总时长
                total_hours = data['加班时长'] + data['调/请假']
                
                # 格式化数字：如果是整数就显示整数，如果是小数就保留一位小数
                def format_number(value):
                    if value == 0:
                        return 0
                    # 先将值转换为float再判断是否为整数
                    float_value = float(value)
                    return int(value) if float_value.is_integer() else round(value, 1)
                
                # 应用数字格式化
                row['加班时长'] = format_number(data['加班时长'])
                row['调/请假'] = format_number(data['调/请假'])
                row['总时长'] = format_number(total_hours)
                
                # 计算总时长(天)
                days_value = calculate_days(total_hours)
                row['总时长(天)'] = format_number(float(days_value))
                
                rows.append(row)
            
            result_df = pd.DataFrame(rows, columns=columns)
            
            # 导出到Excel
            self.ensure_upload_dir()
            # 生成当前年月日的文件名
            current_date = datetime.now()
            year_month_day = current_date.strftime('%Y%m%d')
            output_file = os.path.join(self.upload_dir, f'{year_month_day}考勤记录.xlsx')
            
            # 使用xlsxwriter引擎以支持更多格式设置
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # 写入数据，但从第2行开始，为表头留出空间
                result_df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=1, header=False)
                
                # 获取workbook和worksheet对象
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                
                # 设置列宽
                worksheet.set_column('A:A', 15)  # 姓名列
                worksheet.set_column(1, days_in_month, 4)  # 日期列宽度从8改为4
                worksheet.set_column(days_in_month + 1, days_in_month + 4, 10)  # 统计列
                
                # 设置统一的表头格式（浅蓝背景，深色文字）
                header_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'valign': 'vcenter',
                    'bg_color': '#BDD7EE',  # 浅蓝色背景
                    'font_color': '#000000',  # 黑色文字
                    'border': 1
                })
                
                # 设置单元格格式（无背景色）
                cell_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'num_format': '#,##0;-#,##0;0;@'  # 整数不显示小数点，0显示为0，文本保持原样
                })
                
                # 设置小数格式（用于显示小数的单元格）
                decimal_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1,
                    'num_format': '#,##0.0;-#,##0.0;0;@'  # 小数保留一位，0显示为0，文本保持原样
                })
                
                # 合并单元格并写入标题（年月）
                title = f"{target_year}年{target_month}月加班统计表（小时）"
                
                # 写入并合并姓名列表头
                worksheet.merge_range(0, 0, 1, 0, '姓名', header_format)
                
                # 写入年月标题到日期区域
                worksheet.merge_range(0, 1, 0, days_in_month, title, header_format)
                
                # 写入日期数字（1-31）
                for col in range(1, days_in_month + 1):
                    worksheet.write(1, col, str(col), header_format)
                
                # 写入并合并最后四个统计列的表头
                stat_headers = ['加班时长', '调/请假', '总时长', '总时长(天)']
                for idx, header in enumerate(stat_headers):
                    col = days_in_month + 1 + idx
                    worksheet.merge_range(0, col, 1, col, header, header_format)
                
                # 写入数据（根据数值类型使用不同的格式）
                for row in range(2, len(result_df) + 2):  # 从第3行开始写数据
                    for col in range(len(columns)):
                        value = result_df.iloc[row-2][columns[col]]
                        if value != '':  # 只有非空值才进行格式化
                            try:
                                if isinstance(value, (int, float)):
                                    # 判断是否为整数
                                    float_value = float(value)
                                    if float_value.is_integer():
                                        worksheet.write(row, col, int(value), cell_format)
                                    else:
                                        worksheet.write(row, col, round(float(value), 1), decimal_format)
                                else:
                                    worksheet.write(row, col, value, cell_format)
                            except:
                                worksheet.write(row, col, value, cell_format)
                        else:
                            worksheet.write(row, col, value, cell_format)
            
            print(f"考勤统计表导出完成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"导出考勤记录时发生错误: {str(e)}")
            raise ValueError(f"导出考勤记录失败: {str(e)}")

    def is_workday(self, date_str: str) -> bool:
        """
        判断是否为工作日（包含调休）
        
        Args:
            date_str: 日期字符串，格式为 YYYY-MM-DD
            
        Returns:
            bool: 是否为工作日
        """
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            return is_workday(date)
        except ValueError:
            return False
