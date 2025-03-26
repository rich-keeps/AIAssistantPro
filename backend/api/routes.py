from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Body
from fastapi.responses import FileResponse
from services.excel_service import ExcelService
from models.schemas import ProcessingResponse, ExportRequest
from typing import Dict, Any, List
import os
from urllib.parse import quote
from api import holiday, settings
import numpy as np
import json
import traceback

router = APIRouter()
excel_service = ExcelService()

# 注册节假日路由
router.include_router(holiday.router, tags=["holiday"])

# 注册系统设置路由
router.include_router(settings.router, prefix="/settings", tags=["settings"])

@router.post("/upload", response_model=ProcessingResponse)
async def upload_file(file: UploadFile = File(...), type: str = Query(..., description="文件类型：overtime 或 leave")):
    """
    上传Excel文件并返回预览数据
    """
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件格式(.xlsx, .xls)")
    
    # 验证上传类型
    if type not in ['overtime', 'leave']:
        raise HTTPException(status_code=400, detail="文件类型必须是 overtime 或 leave")
    
    try:
        result = await excel_service.process_upload(file, type)
        return ProcessingResponse(
            success=True,
            message="文件上传成功",
            data=result
        )
    except Exception as e:
        return ProcessingResponse(
            success=False,
            message=str(e),
            data=None
        )

@router.get("/data/{file_id}", response_model=ProcessingResponse)
async def get_paginated_data(
    file_id: str,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量")
):
    """
    获取Excel文件的分页数据
    
    参数:
    - file_id: 文件ID
    - page: 页码，从1开始
    - size: 每页数量，默认10条
    """
    try:
        result = await excel_service.get_paginated_data(file_id, page, size)
        return ProcessingResponse(
            success=True,
            message="获取数据成功",
            data=result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file/{file_id}", response_model=ProcessingResponse)
async def delete_file(file_id: str):
    """
    删除Excel文件及其相关数据
    
    参数:
    - file_id: 文件ID
    """
    try:
        await excel_service.delete_file(file_id)
        return ProcessingResponse(
            success=True,
            message="文件删除成功",
            data=None
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/overtime", response_class=FileResponse)
async def export_overtime(request: ExportRequest):
    """
    导出加班记录
    
    参数:
    - request: 包含要导出的文件ID列表
    """
    try:
        file_path = await excel_service.export_overtime(request.file_ids)
        filename = os.path.basename(file_path)
        # 对中文文件名进行 URL 编码
        encoded_filename = quote(filename)
        headers = {
            'Content-Disposition': f'attachment; filename="{encoded_filename}"'
        }
        return FileResponse(
            file_path,
            headers=headers,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/leave", response_class=FileResponse)
async def export_leave(request: ExportRequest):
    """
    导出请假记录
    
    参数:
    - request: 包含要导出的文件ID列表
    """
    try:
        file_path = await excel_service.export_leave(request.file_ids)
        filename = os.path.basename(file_path)
        # 对中文文件名进行 URL 编码
        encoded_filename = quote(filename)
        headers = {
            'Content-Disposition': f'attachment; filename="{encoded_filename}"'
        }
        return FileResponse(
            file_path,
            headers=headers,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/attendance", response_class=FileResponse)
async def export_attendance(request: ExportRequest):
    """
    导出考勤记录
    
    参数:
    - request: 包含要导出的文件ID列表
    """
    try:
        if not request.file_ids:
            raise HTTPException(status_code=400, detail="请提供至少一个文件ID")

        file_path = await excel_service.export_attendance(request.file_ids)
        filename = os.path.basename(file_path)
        # 对中文文件名进行 URL 编码
        encoded_filename = quote(filename)
        headers = {
            'Content-Disposition': f'attachment; filename="{encoded_filename}"'
        }
        return FileResponse(
            file_path,
            headers=headers,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/merged-leave", response_class=FileResponse)
async def export_merged_leave(request: ExportRequest):
    """
    导出合并后的请假记录
    
    参数:
    - request: 包含要合并并导出的请假记录文件ID列表
    """
    try:
        if len(request.file_ids) < 2:
            return ProcessingResponse(
                success=False,
                message="至少需要两个请假记录文件才能合并",
                data=None
            ).dict()
        
        file_path = await excel_service.export_merged_leave(request.file_ids)
        filename = os.path.basename(file_path)
        # 对中文文件名进行 URL 编码
        encoded_filename = quote(filename)
        headers = {
            'Content-Disposition': f'attachment; filename="{encoded_filename}"'
        }
        return FileResponse(
            file_path,
            headers=headers,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except ValueError as e:
        print(f"导出合并请假记录值错误: {str(e)}")
        return ProcessingResponse(
            success=False,
            message=str(e),
            data=None
        ).dict()
    except Exception as e:
        print(f"导出合并请假记录异常: {str(e)}")
        print(traceback.format_exc())
        return ProcessingResponse(
            success=False,
            message=f"导出合并请假记录失败: {str(e)}",
            data=None
        ).dict()
