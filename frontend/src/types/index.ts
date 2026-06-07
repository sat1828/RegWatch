export interface DashboardStats {
  total_sources: number
  total_documents: number
  total_obligations: number
  critical_obligations: number
  high_risk_items: number
  pending_reviews: number
  total_gaps: number
}

export interface RegulatorySource {
  id: string
  name: string
  url: string
  source_type: string
  jurisdiction: string
  regulator: string
  is_active: boolean
  last_scraped_at: string | null
  created_at: string
  updated_at: string
}

export interface SourceCreate {
  name: string
  url: string
  source_type?: string
  jurisdiction?: string
  regulator?: string
  is_active?: boolean
}

export interface SourceUpdate {
  name?: string
  url?: string
  is_active?: boolean
  scrape_interval_minutes?: number
}

export interface DocumentListItem {
  id: string
  title: string
  source_name: string
  document_type: string
  status: string
  risk_score: number | null
  obligation_count: number
  published_date: string | null
  created_at: string
  updated_at: string
}

export interface DocumentListResponse {
  items: DocumentListItem[]
  total: number
}

export interface DocumentDetail {
  id: string
  title: string
  url: string
  source_name: string
  document_type: string
  status: string
  raw_text: string | null
  delta_text: string | null
  published_date: string | null
  effective_date: string | null
  is_amendment: boolean
  obligations: ObligationItem[]
  risk_scores: RiskScoreItem[]
  gaps: GapItem[]
  drafts: DraftItem[]
  created_at: string
  updated_at: string
}

export interface ObligationItem {
  id: string
  obligation_text: string
  obligation_category: string
  severity: string
  deadline: string | null
  regulation_reference: string | null
  is_mandatory: boolean
}

export interface RiskScoreItem {
  id: string
  overall_score: number
  penalty_score: number
  deadline_score: number
  enforcement_score: number
  priority_rank: number
  risk_category: string
  reasoning: string | null
}

export interface GapItem {
  id: string
  gap_type: string
  gap_description: string
  severity: string
  confidence_score: number
  recommendation: string | null
}

export interface DraftItem {
  id: string
  title: string
  content: string
  status: string
  change_summary: string | null
  created_at: string
}

export interface PolicyDraft {
  id: string
  document_id: string
  title: string
  content: string
  status: string
  change_summary: string | null
  reviewed_by: string | null
  reviewed_at: string | null
  review_notes: string | null
  created_at: string
  updated_at: string
}

export interface PipelineRunResponse {
  pipeline_id: string
  status: string
}

export interface PipelineStatus {
  pipeline_id: string
  status: string
  started_at: string | null
  completed_at: string | null
  error: string | null
}

export interface AuditLog {
  id: string
  action: string
  entity_type: string
  entity_id: string | null
  actor: string | null
  details: string | null
  created_at: string
}

export type ThemeMode = 'light' | 'dark'
