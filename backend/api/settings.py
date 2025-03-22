from fastapi import APIRouter, HTTPException
from models.schemas import SystemSettings, UpdateSystemSettingsRequest, ProcessingResponse
from services.settings_service import settings_service
from services.excel_service import ExcelService

router = APIRouter()
excel_service = ExcelService()

@router.get("/system", response_model=ProcessingResponse)
async def get_system_settings():
    """
    获取系统设置
    """
    try:
        settings = settings_service.get_settings()
        return ProcessingResponse(
            success=True,
            message="获取系统设置成功",
            data=settings
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/system", response_model=ProcessingResponse)
async def update_system_settings(request: UpdateSystemSettingsRequest):
    """
    更新系统设置
    """
    try:
        # 过滤掉None值
        settings_dict = {k: v for k, v in request.dict().items() if v is not None}
        
        # 验证max_files参数
        if "max_files" in settings_dict and settings_dict["max_files"] < 10:
            raise ValueError("最大文件数量不能小于10")
        
        updated_settings = settings_service.update_settings(settings_dict)
        return ProcessingResponse(
            success=True,
            message="更新系统设置成功",
            data=updated_settings
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clean-files", response_model=ProcessingResponse)
async def clean_files():
    """
    立即清理文件
    """
    try:
        # 强制清理文件
        excel_service.check_and_clean_files()
        return ProcessingResponse(
            success=True,
            message="文件清理成功",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 