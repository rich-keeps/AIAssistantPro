import json
import os
from pathlib import Path
from typing import Dict, Any
from models.schemas import SystemSettings

class SettingsService:
    """系统设置服务"""
    
    def __init__(self):
        """初始化系统设置服务"""
        self.data_dir = "data"
        self.settings_file = os.path.join(self.data_dir, "system_settings.json")
        self.ensure_data_dir()
        self.default_settings = SystemSettings().dict()
        self._load_settings()
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_settings(self):
        """加载系统设置"""
        if not os.path.exists(self.settings_file):
            # 如果设置文件不存在，创建默认设置
            self.settings = self.default_settings
            self._save_settings()
        else:
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"加载系统设置失败: {str(e)}")
                self.settings = self.default_settings
                self._save_settings()
    
    def _save_settings(self):
        """保存系统设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存系统设置失败: {str(e)}")
    
    def get_settings(self) -> Dict[str, Any]:
        """获取系统设置"""
        return self.settings
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """更新系统设置"""
        # 只更新提供的设置项
        for key, value in settings.items():
            if key in self.settings and value is not None:
                self.settings[key] = value
        
        self._save_settings()
        return self.settings
    
    def get_max_files(self) -> int:
        """获取最大文件数量设置"""
        return self.settings.get("max_files", 100)

# 创建单例实例
settings_service = SettingsService() 