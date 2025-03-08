export const API_BASE_URL = 'http://localhost:8000';

export const API_ENDPOINTS = {
    UPLOAD: `${API_BASE_URL}/api/upload`,
    EXPORT_OVERTIME: `${API_BASE_URL}/api/export/overtime`,
    EXPORT_LEAVE: `${API_BASE_URL}/api/export/leave`,
    EXPORT_ATTENDANCE: `${API_BASE_URL}/api/export/attendance`,
    DELETE_FILE: (fileId: string) => `${API_BASE_URL}/api/file/${fileId}`,
}; 