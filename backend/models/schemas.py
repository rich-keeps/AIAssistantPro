from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ProcessingResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

class ColumnHeader(BaseModel):
    """表头信息模型"""
    key: str
    label: str
    type: str
    width: int

class ExcelPreview(BaseModel):
    """Excel预览数据模型"""
    headers: List[ColumnHeader]
    sample_data: List[Dict[str, Any]]
    total_rows: int
    file_id: Optional[str] = None

class PaginatedData(BaseModel):
    """分页数据模型"""
    items: List[Dict[str, Any]]
    total: int
    page: int
    size: int
    total_pages: int
    headers: List[ColumnHeader]

class ExportRequest(BaseModel):
    """导出请求模型"""
    file_ids: List[str]

class SystemSettings(BaseModel):
    """系统设置模型"""
    max_files: int = Field(default=100, description="最大文件数量，超过此数量将清理旧文件")
    system_name: str = Field(default="Encan考勤系统", description="系统名称")
    theme_color: str = Field(default="#4CAF50", description="系统主题色")

class UpdateSystemSettingsRequest(BaseModel):
    """更新系统设置请求模型"""
    max_files: Optional[int] = None
    system_name: Optional[str] = None
    theme_color: Optional[str] = None
