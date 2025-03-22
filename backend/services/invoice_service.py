import os
import uuid
import tempfile
from typing import Dict, Any, Optional, List, Tuple
import re

# 尝试导入PaddleOCR依赖
try:
    from paddleocr import PaddleOCR
    PADDLE_OCR_AVAILABLE = True
except ImportError:
    PADDLE_OCR_AVAILABLE = False
    print("警告: PaddleOCR 未安装，请执行 'pip install paddlepaddle paddleocr' 安装")

# 尝试导入PDF处理依赖
try:
    import pdf2image
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("警告: pdf2image 未安装，PDF处理功能将不可用")

# 尝试导入图像处理依赖
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("警告: opencv-python 未安装，图像预处理功能将不可用")

class InvoiceService:
    """发票识别服务 - 使用PaddleOCR实现"""
    
    # 发票类型关键词映射
    INVOICE_TYPES = {
        "highway": ["高速", "通行费", "路桥费", "ETC", "运输服务", "客运服务"],
        "taxi": ["出租车", "打车", "taxi", "滴滴", "快车"],
        "meal": ["餐饮", "餐厅", "饭店", "食堂", "小吃", "烧烤", "火锅"],
        "accommodation": ["酒店", "宾馆", "住宿", "客房", "旅店"],
        "office": ["办公", "文具", "打印", "复印", "纸张"]
    }
    
    # 金额识别模式
    AMOUNT_PATTERNS = {
        "price_tax_total": [  # 价税合计（最高优先级）
            r"[（(]小写[)）]\s*[¥￥]?\s*([0-9,]+\.?[0-9]*)",  # 匹配"（小写）¥15.69"格式
            r"[（(]小写[)）].*?([0-9,]+\.?[0-9]*)",  # 匹配"（小写）15.69"格式
            r"价税合计[¥￥]?[:：]?\s*([0-9,]+\.?[0-9]*)",
            r"价税合计.*?[¥￥]\s*([0-9,]+\.?[0-9]*)",
            r"（大写）.*?整.*?[¥￥]?\s*([0-9,]+\.?[0-9]*)",
            r"TOTAL[:：]?\s*[¥￥]?\s*([0-9,]+\.?[0-9]*)",
            r"合计金额[:：]?\s*[¥￥]?\s*([0-9,]+\.?[0-9]*)"
        ],
        "amount_with_tax": [  # 含税金额
            r"含税金额[:：]?\s*[¥￥]?\s*([0-9,]+\.?[0-9]*)",
            r"金额[:：]?\s*[¥￥]?\s*([0-9,]+\.?[0-9]*)",
            r"AMOUNT[:：]?\s*[¥￥]?\s*([0-9,]+\.?[0-9]*)"
        ]
    }
    
    # 发票号码识别模式 - 优化后的正则表达式
    INVOICE_NUMBER_PATTERNS = [
        r"发票号码[:：]\s*(\d+)",  # 基本匹配
        r"发票号码[:：]?\s*([0-9０-９]+)",  # 兼容全角数字
        r"发票号码.*?[:：]?\s*(\d+)",  # 宽松匹配
        r"(?<![0-9])(\d{7,8})(?![0-9])",  # 独立的7-8位数字
        r"NO[.:：]?\s*(\d+)",  # 英文格式
        r"发票号[码碼]?[:：]?\s*(\d+)"  # 兼容繁体
    ]

    # 需要排除的编号模式（避免误识别）
    EXCLUDE_NUMBER_PATTERNS = [
        r"机器编号[:：]?\s*(\d+)",
        r"校验码[:：]?\s*(\d+)",
        r"发票代码[:：]?\s*(\d+)",
        r"税号[:：]?\s*(\d+)",
        r"纳税人识别号[:：]?\s*(\d+)",
        r"密码区[:：]?\s*(\d+)",
        r"证件号码[:：]?\s*(\d+)",
        r"地址[:：]?\s*(\d+)",
        r"电话[:：]?\s*(\d+)"
    ]
    
    def __init__(self):
        """初始化发票识别服务"""
        self.temp_dir = "uploads/temp"
        self.ensure_temp_dir()
        self.ocr_engine = None
    
    def ensure_temp_dir(self):
        """确保临时目录存在"""
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def get_ocr_engine(self):
        """获取OCR引擎实例（延迟加载）"""
        if self.ocr_engine is None:
            if not PADDLE_OCR_AVAILABLE:
                raise ImportError("PaddleOCR未安装，请执行 'pip install paddlepaddle paddleocr' 安装")
            
            print("初始化PaddleOCR引擎...")
            # 使用更稳定的配置初始化PaddleOCR
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True,     # 启用方向分类，自动处理倾斜文本
                lang="ch",              # 中文模型
                use_gpu=False,          # 默认使用CPU
                show_log=False,         # 不显示日志
                det_db_thresh=0.3,      # 检测阈值，适当降低可以提高对模糊文本的检测
                det_db_box_thresh=0.5,  # 检测框阈值
                det_db_unclip_ratio=1.6,# 文本框扩张比例
                rec_batch_num=1,        # 降低批处理大小，提高稳定性
                cls_batch_num=1,        # 降低批处理大小，提高稳定性
                use_mp=False,           # 禁用多进程，避免潜在的问题
                total_process_num=1,    # 单进程处理
                use_pdserving=False,    # 禁用PaddleServing
                drop_score=0.5          # 设置文本识别置信度阈值
            )
            print("PaddleOCR引擎初始化完成")
        
        return self.ocr_engine
    
    async def recognize_invoice(self, file_content: bytes, file_extension: str) -> Dict[str, Any]:
        """
        识别发票内容
        
        Args:
            file_content: 文件内容
            file_extension: 文件扩展名
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        print(f"开始识别发票，文件类型: {file_extension}")
        
        # 检查PaddleOCR是否可用
        if not PADDLE_OCR_AVAILABLE:
            print("警告: PaddleOCR未安装，发票识别功能不可用")
            return {
                "amount": None,
                "invoice_no": None,
                "type": "other",
                "error": "PaddleOCR未安装，请执行 'pip install paddlepaddle paddleocr' 安装"
            }
        
        # 生成临时文件路径
        temp_file_path = os.path.join(self.temp_dir, f"{uuid.uuid4()}{file_extension}")
        
        try:
            # 保存文件到临时目录
            with open(temp_file_path, "wb") as f:
                f.write(file_content)
            
            print(f"临时文件已保存: {temp_file_path}")
            
            # 根据文件类型处理图像
            if file_extension.lower() == ".pdf":
                if not PDF_SUPPORT:
                    print("PDF处理功能不可用")
                    return {
                        "amount": None,
                        "invoice_no": None,
                        "type": "other",
                        "error": "PDF处理功能不可用，请安装pdf2image"
                    }
                
                # 处理PDF文件
                print("开始处理PDF文件...")
                images = pdf2image.convert_from_path(temp_file_path, dpi=300)
                if not images:
                    print("PDF转换失败，未能提取图像")
                    return {
                        "amount": None,
                        "invoice_no": None,
                        "type": "other",
                        "error": "PDF转换失败，未能提取图像"
                    }
                
                # 使用第一页进行识别
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                    images[0].save(tmp_file.name, 'JPEG')
                    image_path = tmp_file.name
                    print(f"PDF已转换为图像: {image_path}")
            else:
                # 处理图像文件
                image_path = temp_file_path
                print(f"使用图像文件: {image_path}")
            
            # 图像预处理（可选，提高识别准确率）
            preprocessed_image_path = None
            if CV2_AVAILABLE:
                print("进行图像预处理...")
                preprocessed_image_path = self._preprocess_image(image_path)
                if preprocessed_image_path:
                    image_path = preprocessed_image_path
                    print(f"使用预处理后的图像: {image_path}")
            
            # 使用PaddleOCR识别文本
            print("开始使用PaddleOCR识别文本...")
            ocr_result = self._recognize_text_with_paddle(image_path)
            
            # 解析发票信息
            print("开始解析发票信息...")
            invoice_data = self._parse_invoice_data(ocr_result)
            print(f"解析结果: {invoice_data}")
            
            # 清理临时文件
            if file_extension.lower() == ".pdf" and os.path.exists(image_path) and image_path != temp_file_path:
                os.remove(image_path)
            
            if preprocessed_image_path and os.path.exists(preprocessed_image_path):
                os.remove(preprocessed_image_path)
            
            return invoice_data
        
        except Exception as e:
            print(f"发票识别过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "amount": None,
                "invoice_no": None,
                "type": "other",
                "error": f"发票识别失败: {str(e)}"
            }
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    print(f"删除临时文件失败: {str(e)}")
    
    def _preprocess_image(self, image_path: str) -> Optional[str]:
        """
        图像预处理，提高OCR识别准确率
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            Optional[str]: 预处理后的图像路径，如果预处理失败则返回None
        """
        try:
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                print(f"无法读取图像: {image_path}")
                return None
            
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 自适应阈值处理，提高文本对比度
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 降噪处理
            denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
            
            # 保存预处理后的图像
            preprocessed_path = f"{image_path}_preprocessed.jpg"
            cv2.imwrite(preprocessed_path, denoised)
            
            return preprocessed_path
        except Exception as e:
            print(f"图像预处理失败: {str(e)}")
            return None
    
    def _recognize_text_with_paddle(self, image_path: str) -> List[Tuple[str, List[List[int]], float]]:
        """
        使用PaddleOCR识别图像中的文本
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            List[Tuple[str, List[List[int]], float]]: 识别结果，每项包含文本内容和位置坐标
        """
        try:
            # 获取OCR引擎
            ocr = self.get_ocr_engine()
            
            # 识别图像
            result = ocr.ocr(image_path, cls=True)
            
            # 提取文本和位置信息
            text_with_positions = []
            
            # PaddleOCR返回格式可能因版本而异
            if isinstance(result, list) and len(result) > 0:
                # 新版PaddleOCR
                if isinstance(result[0], list) and len(result[0]) > 0:
                    for line in result:
                        for item in line:
                            if len(item) >= 2:
                                position = item[0]  # 文本框位置坐标
                                text = item[1][0]   # 识别的文本内容
                                confidence = item[1][1]  # 置信度
                                text_with_positions.append((text, position, confidence))
                # 旧版PaddleOCR
                else:
                    for item in result:
                        if len(item) >= 2:
                            position = item[0]  # 文本框位置坐标
                            text = item[1][0]   # 识别的文本内容
                            confidence = item[1][1]  # 置信度
                            text_with_positions.append((text, position, confidence))
            
            print(f"PaddleOCR识别完成，共识别出{len(text_with_positions)}个文本块")
            return text_with_positions
        except Exception as e:
            print(f"PaddleOCR识别失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_invoice_data(self, ocr_result: List[Tuple[str, List[List[int]], float]]) -> Dict[str, Any]:
        """
        解析OCR识别结果，提取发票信息
        
        Args:
            ocr_result: OCR识别结果，包含文本内容和位置信息
            
        Returns:
            Dict[str, Any]: 解析后的发票数据
        """
        # 初始化结果
        result = {
            "amount": None,
            "invoice_no": None,
            "type": "other"
        }
        
        if not ocr_result:
            print("OCR结果为空，返回默认值")
            return result
        
        # 提取所有文本内容
        all_texts = [text for text, _, _ in ocr_result]
        full_text = " ".join(all_texts)
        print(f"合并后的文本内容(前200个字符): {full_text[:200]}")
        
        # 1. 提取发票号码
        invoice_no = self._extract_invoice_number(full_text)
        if invoice_no:
            result["invoice_no"] = invoice_no
        
        # 2. 提取金额
        amount = self._extract_amount(ocr_result, full_text)
        if amount is not None:
            result["amount"] = amount
        
        # 3. 确定发票类型
        result["type"] = self._determine_invoice_type(full_text)
        
        print(f"最终解析结果: {result}")
        return result
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """
        从OCR结果中提取发票号码，使用优化后的识别逻辑
        
        Args:
            text: 合并后的完整文本
            
        Returns:
            Optional[str]: 提取的发票号码，如果未找到则返回None
        """
        # 预处理文本：将全角数字转换为半角数字
        text = text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        
        # 首先获取需要排除的编号
        exclude_numbers = set()
        for pattern in self.EXCLUDE_NUMBER_PATTERNS:
            matches = re.finditer(pattern, text)
            for match in matches:
                exclude_numbers.add(match.group(1).strip())
        
        print(f"需要排除的编号: {exclude_numbers}")
        
        # 方法1: 使用优化后的关键词匹配
        for pattern in self.INVOICE_NUMBER_PATTERNS:
            matches = re.finditer(pattern, text)
            for match in matches:
                invoice_no = match.group(1).strip()
                # 验证提取的号码
                if invoice_no not in exclude_numbers and self._validate_invoice_number(invoice_no):
                    print(f"通过正则表达式找到有效发票号码: {invoice_no}")
                    return invoice_no
        
        print("未找到有效的发票号码")
        return None
    
    def _validate_invoice_number(self, number: str) -> bool:
        """
        验证发票号码的有效性
        
        Args:
            number: 待验证的发票号码
            
        Returns:
            bool: 是否为有效的发票号码
        """
        # 1. 基本格式验证：必须全部是数字
        if not number.isdigit():
            return False
        
        # 2. 数值范围检查：不能为0或负数
        if int(number) <= 0:
            return False
        
        # 3. 避免误识别校验码（通常是5组4位数）
        if re.match(r'^\d{4}\s+\d{4}\s+\d{4}\s+\d{4}\s+\d{4}$', number):
            return False
        
        # 4. 避免误识别电话号码（11位手机号）
        if re.match(r'^1[3-9]\d{9}$', number):
            return False
        
        return True
    
    def _extract_amount(self, ocr_result: List[Tuple[str, List[List[int]], float]], full_text: str) -> Optional[float]:
        """
        从OCR结果中提取金额，优先提取价税合计金额
        
        Args:
            ocr_result: OCR识别结果
            full_text: 合并后的完整文本
            
        Returns:
            Optional[float]: 提取的金额，如果未找到则返回None
        """
        candidates = []
        
        # 预处理文本，移除多余的空格和特殊字符
        full_text = re.sub(r'\s+', ' ', full_text)
        
        # 方法1: 通过关键词模式匹配
        for priority, patterns in enumerate(self.AMOUNT_PATTERNS.values()):
            for pattern in patterns:
                matches = re.finditer(pattern, full_text)
                for match in matches:
                    try:
                        amount_str = match.group(1).replace(',', '')
                        amount = float(amount_str)
                        if amount > 0:
                            # 提高小写金额的优先级
                            if "小写" in match.group(0):
                                candidates.append((amount, 1.0))
                            else:
                                candidates.append((amount, 0.9 - priority * 0.1))
                    except ValueError:
                        continue
        
        # 方法2: 尝试通过税额计算价税合计
        numbers_with_positions = self._extract_numbers_with_positions(ocr_result)
        for i in range(len(numbers_with_positions)):
            amount, y1 = numbers_with_positions[i]
            # 查找相邻的可能是税额的数字
            for j in range(i + 1, len(numbers_with_positions)):
                tax_amount, y2 = numbers_with_positions[j]
                # 如果两个数字垂直位置接近
                if abs(y2 - y1) < 50:
                    # 检查是否符合增值税税率关系（3%、6%、9%、13%）
                    for tax_rate in [0.03, 0.06, 0.09, 0.13]:
                        expected_tax = round(amount * tax_rate, 2)
                        if abs(tax_amount - expected_tax) < 0.01:
                            total_amount = round(amount + tax_amount, 2)
                            candidates.append((total_amount, 0.85))
                            break
        
        if candidates:
            # 按优先级和金额大小排序
            candidates.sort(key=lambda x: (-x[1], -x[0]))
            
            # 选择优先级最高的金额
            highest_priority_amount = candidates[0][0]
            print(f"最终选择的金额: {highest_priority_amount} (优先级: {candidates[0][1]})")
            return highest_priority_amount
        
        print("未找到有效金额")
        return None
    
    def _determine_invoice_type(self, text: str) -> str:
        """
        根据文本内容确定发票类型
        
        Args:
            text: 提取的文本
            
        Returns:
            str: 发票类型
        """
        text = text.lower()
        
        for invoice_type, keywords in self.INVOICE_TYPES.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    print(f"根据关键词'{keyword}'确定发票类型为: {invoice_type}")
                    return invoice_type
        
        print("未找到匹配的发票类型，使用默认类型: other")
        return "other"  # 默认为其他类型
    
    def _extract_numbers_with_positions(self, ocr_result: List[Tuple[str, List[List[int]], float]]) -> List[Tuple[float, float]]:
        """提取数字及其位置"""
        numbers = []
        for text, position, _ in ocr_result:
            matches = re.findall(r"([0-9,]+\.?[0-9]*)", text)
            for match in matches:
                try:
                    number = float(match.replace(',', ''))
                    if number > 0:
                        center_y = (position[0][1] + position[2][1]) / 2
                        numbers.append((number, center_y))
                except ValueError:
                    continue
        return sorted(numbers, key=lambda x: x[1]) 