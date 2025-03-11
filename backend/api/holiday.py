from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from datetime import datetime, date, timedelta
from chinese_calendar import is_workday, is_holiday
import subprocess
import sys
import importlib
import pkg_resources

router = APIRouter()

def check_and_update_chinese_calendar():
    """
    检查chinese-calendar库的版本，并在需要时尝试更新
    
    Returns:
        bool: 是否成功更新
    """
    try:
        # 获取当前安装的版本
        current_version = pkg_resources.get_distribution("chinese-calendar").version
        print(f"当前chinese-calendar版本: {current_version}")
        
        # 尝试获取最新版本信息
        try:
            # 使用pip命令获取最新版本信息
            result = subprocess.run(
                [sys.executable, "-m", "pip", "index", "versions", "chinese-calendar"],
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout
            
            # 解析输出获取最新版本
            import re
            latest_version_match = re.search(r"chinese-calendar \((.*?)\)", output)
            if latest_version_match:
                latest_version = latest_version_match.group(1).split(",")[0]
                print(f"最新chinese-calendar版本: {latest_version}")
                
                # 如果当前版本不是最新版本，尝试更新
                if current_version != latest_version:
                    print(f"正在更新chinese-calendar从 {current_version} 到 {latest_version}...")
                    update_result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", "chinese-calendar", "--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org"],
                        capture_output=True,
                        text=True
                    )
                    
                    if update_result.returncode == 0:
                        print("chinese-calendar更新成功")
                        # 重新加载模块
                        importlib.reload(sys.modules['chinese_calendar'])
                        return True
                    else:
                        print(f"chinese-calendar更新失败: {update_result.stderr}")
            
        except Exception as e:
            print(f"获取最新版本信息失败: {e}")
        
        return False
    
    except Exception as e:
        print(f"检查chinese-calendar版本失败: {e}")
        return False

@router.get("/holidays")
async def get_holidays(year: int) -> Dict[str, List[str]]:
    """
    获取指定年份的节假日和调休工作日信息
    
    Args:
        year: 年份
        
    Returns:
        Dict[str, List[str]]: 包含节假日和调休工作日的字典
    """
    # 验证年份范围
    current_year = datetime.now().year
    if year < 1949 or year > current_year + 5:  # 允许查询未来5年的数据
        return {
            "holidays": [],
            "workdaysOnWeekends": []
        }
    
    # 获取该年的所有日期
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    delta = end_date - start_date
    
    holidays = []
    workdaysOnWeekends = []
    
    update_attempted = False
    
    # 遍历该年的每一天
    for i in range(delta.days + 1):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        weekday = current_date.weekday()
        
        try:
            # 判断是否为节假日（周一至周五的法定节假日）
            if is_holiday(current_date) and weekday < 5:
                holidays.append(date_str)
            
            # 判断是否为调休工作日（周末但需要上班）
            if is_workday(current_date) and weekday >= 5:
                workdaysOnWeekends.append(date_str)
        except NotImplementedError as e:
            # 如果是因为年份不支持导致的错误，尝试更新库
            if not update_attempted:
                print(f"获取 {year} 年数据失败，尝试更新chinese-calendar库...")
                update_attempted = True
                updated = check_and_update_chinese_calendar()
                
                if updated:
                    # 如果更新成功，重新尝试获取数据
                    try:
                        if is_holiday(current_date) and weekday < 5:
                            holidays.append(date_str)
                        
                        if is_workday(current_date) and weekday >= 5:
                            workdaysOnWeekends.append(date_str)
                        
                        # 如果成功获取数据，继续处理
                        continue
                    except Exception as inner_e:
                        print(f"更新后仍然无法获取数据: {inner_e}")
            
            # 如果更新失败或者更新后仍然无法获取数据，使用基本的周末判断
            print(f"处理日期 {date_str} 时出错: {e}")
            if weekday >= 5:  # 周六和周日
                holidays.append(date_str)
        except Exception as e:
            # 如果出错，记录日志但不中断处理
            print(f"处理日期 {date_str} 时出错: {e}")
            # 对于出错的日期，使用基本的周末判断
            if weekday >= 5:  # 周六和周日
                holidays.append(date_str)
    
    return {
        "holidays": holidays,
        "workdaysOnWeekends": workdaysOnWeekends
    } 