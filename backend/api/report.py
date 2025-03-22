from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from services.report_service import ReportService
from datetime import datetime
from urllib.parse import quote

router = APIRouter()

class ReportRequest(BaseModel):
    name: str
    month: str  # YYYY-MM格式
    dates: List[str]  # YYYY-MM-DD格式的日期列表

class ExpenseReportRequest(BaseModel):
    name: str
    month: str  # YYYY/MM格式
    expense_items: List[Dict[str, Any]]

@router.post("/generate")
async def generate_report(request: ReportRequest):
    try:
        # 验证月份格式
        try:
            datetime.strptime(request.month, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="月份格式错误，应为YYYY-MM格式")

        # 验证日期格式和有效性
        for date in request.dates:
            try:
                datetime.strptime(date, "%Y-%m-%d")
                if not date.startswith(request.month):
                    raise ValueError("日期不在所选月份内")
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"日期格式错误或日期无效: {date}")

        # 生成报表
        excel_data = ReportService.generate_business_trip_report(
            request.name,
            request.month,
            request.dates
        )

        # 设置文件名
        filename = f"{request.name}-{request.month}出差统计表.xlsx"
        # URL编码文件名，确保中文字符能正确处理
        encoded_filename = quote(filename)
        
        # 返回Excel文件
        return StreamingResponse(
            excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expense")
async def generate_expense_report(request: ExpenseReportRequest):
    try:
        # 验证月份格式
        try:
            datetime.strptime(request.month, "%Y/%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="月份格式错误，应为YYYY/MM格式")

        # 验证报销明细数据
        if not request.expense_items:
            raise HTTPException(status_code=400, detail="报销明细不能为空")

        # 生成报表
        excel_data = ReportService.generate_expense_report(
            request.name,
            request.month,
            request.expense_items
        )

        # 设置文件名（格式：202312陈裕报销明细.xlsx）
        filename = f"{request.month.replace('/', '')}{request.name}报销明细.xlsx"
        # URL编码文件名，确保中文字符能正确处理
        encoded_filename = quote(filename)
        
        # 返回Excel文件
        return StreamingResponse(
            excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 