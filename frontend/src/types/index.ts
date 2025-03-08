export interface ColumnMapping {
    source: string
    target: string
    type: 'text' | 'number' | 'date'
}

export interface FilterCondition {
    column: string
    operator: 'eq' | 'gt' | 'lt' | 'contains'
    value: any
}

export interface ProcessingConfig {
    column_mappings: ColumnMapping[]
    date_columns: string[]
    numeric_columns: string[]
    category_column?: string
    filters?: FilterCondition[]
}

export interface ColumnHeader {
    key: string
    label: string
    width: number
    type: 'text' | 'number' | 'datetime'
}

export interface ExcelPreview {
    file_id: string
    total_rows: number
    sample_data: any[]
    headers: ColumnHeader[]
}

export interface ProcessingResponse {
    success: boolean
    message: string
    data?: any
}

export interface FileInfo {
    id: string
    name: string
    type: 'overtime' | 'leave'  // 文件类型：加班或请假
    preview: ExcelPreview
    currentData: any[]
    headers: ColumnHeader[]
    currentPage: number
    pageSize: number
}

export interface PaginationParams {
    page: number
    size: number
} 