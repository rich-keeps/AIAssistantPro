from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from models.schemas import ProcessingResponse
from services.invoice_service import InvoiceService

router = APIRouter()
invoice_service = InvoiceService()

@router.post("/upload", response_model=ProcessingResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    type: str = Form(..., description="文件类型：invoice")
):
    """
    上传发票文件并进行识别
    
    Args:
        file: 上传的发票文件（支持JPG、PNG、PDF格式）
        type: 文件类型，必须为"invoice"
        
    Returns:
        ProcessingResponse: 包含识别结果的响应
    """
    try:
        # 验证文件类型
        if type != "invoice":
            raise HTTPException(status_code=400, detail="文件类型必须为invoice")
        
        # 验证文件格式
        allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
        file_extension = "." + file.filename.split(".")[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式，仅支持{', '.join(allowed_extensions)}"
            )
        
        # 读取文件内容
        contents = await file.read()
        
        # 调用发票识别服务
        invoice_data = await invoice_service.recognize_invoice(contents, file_extension)
        
        return ProcessingResponse(
            success=True,
            message="发票识别成功",
            data=invoice_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"发票识别失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发票识别失败: {str(e)}") 