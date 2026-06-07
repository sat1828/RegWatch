import type {
  AuditLog,
  DashboardStats,
  DocumentDetail,
  DocumentListResponse,
  PipelineRunResponse,
  PipelineStatus,
  PolicyDraft,
  RegulatorySource,
  SourceCreate,
  SourceUpdate,
} from '@/types'

const API_BASE = '/api/v1'
const API_KEY = import.meta.env.VITE_API_KEY || 'regwatch-dev-key-change-in-production'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
    ...(options.headers as Record<string, string> || {}),
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`API Error ${response.status}: ${error}`)
  }

  if (response.status === 204) return undefined as T
  return response.json()
}

export const api = {
  health: () => request<{ status: string }>('/health'),

  getDashboardStats: () => request<DashboardStats>('/dashboard/stats'),

  listSources: (skip = 0, limit = 50) =>
    request<RegulatorySource[]>(`/sources?skip=${skip}&limit=${limit}`),

  getSource: (id: string) => request<RegulatorySource>(`/sources/${id}`),

  createSource: (data: SourceCreate) =>
    request<RegulatorySource>('/sources', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateSource: (id: string, data: SourceUpdate) =>
    request<RegulatorySource>(`/sources/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteSource: (id: string) =>
    request<void>(`/sources/${id}`, { method: 'DELETE' }),

  listDocuments: (params?: { skip?: number; limit?: number; status?: string; source_id?: string }) => {
    const query = new URLSearchParams()
    if (params?.skip) query.set('skip', params.skip.toString())
    if (params?.limit) query.set('limit', params.limit.toString())
    if (params?.status) query.set('status', params.status)
    if (params?.source_id) query.set('source_id', params.source_id)
    return request<DocumentListResponse>(`/documents?${query}`)
  },

  getDocument: (id: string) => request<DocumentDetail>(`/documents/${id}`),

  transitionDocument: (id: string, status: string) =>
    request<{ status: string }>(`/documents/${id}/transition?target_status=${status}`, {
      method: 'POST',
    }),

  runPipeline: (mode: 'full' | 'watcher' = 'full') =>
    request<PipelineRunResponse>(`/pipeline/run?mode=${mode}`, { method: 'POST' }),

  getPipelineStatus: (id: string) => request<PipelineStatus>(`/pipeline/status/${id}`),

  listDrafts: (status?: string) => {
    const query = status ? `?status=${status}` : ''
    return request<PolicyDraft[]>(`/drafts${query}`)
  },

  createDraft: (data: { document_id: string; title: string; content: string; change_summary?: string }) =>
    request<PolicyDraft>('/drafts', { method: 'POST', body: JSON.stringify(data) }),

  reviewDraft: (id: string, data: { status: string; reviewed_by?: string; review_notes?: string }) =>
    request<PolicyDraft>(`/drafts/${id}/review`, { method: 'PUT', body: JSON.stringify(data) }),

  listAuditLogs: (limit = 50) => request<AuditLog[]>(`/audit-logs?limit=${limit}`),
}
