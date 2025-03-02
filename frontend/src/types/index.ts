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
    type: string
    width: number
}

export interface ExcelPreview {
    headers: ColumnHeader[]
    sample_data: Record<string, any>[]
    total_rows: number
    file_id: string
}

export interface ProcessingResponse {
    success: boolean
    message: string
    data?: any
} 