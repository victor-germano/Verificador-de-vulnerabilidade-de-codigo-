export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type Confidence = "high" | "medium" | "low";
export type Language =
  | "python"
  | "javascript"
  | "typescript"
  | "java"
  | "php"
  | "go"
  | "rust"
  | "csharp";
export type ScanStatus = "pending" | "running" | "completed" | "failed";
export type ScanTargetType = "file" | "folder" | "project" | "git_repository";
export type ReportFormat = "json" | "markdown" | "html" | "pdf";
export type ProjectRole = "editor" | "viewer";

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  created_at: string;
}

export interface Collaborator {
  user_id: string;
  email: string;
  full_name: string;
  role: ProjectRole;
  added_at: string;
}

export interface Scan {
  id: string;
  project_id: string;
  target_type: ScanTargetType;
  target_reference: string;
  status: ScanStatus;
  files_scanned: number;
  security_score: number | null;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number | null;
  error_message: string | null;
  created_at: string;
}

export interface Finding {
  id: string;
  scan_id: string;
  rule_id: string;
  rule_name: string;
  category: string;
  severity: Severity;
  confidence: Confidence;
  language: Language;
  owasp: string | null;
  cwe: string | null;
  cvss: number | null;
  file_path: string;
  line_start: number;
  line_end: number;
  code_snippet: string;
  description: string;
  explanation: string;
  impact: string;
  recommendation: string;
  secure_example: string;
  references: string[];
  created_at: string;
}

export interface DashboardSummary {
  total_projects: number;
  total_scans: number;
  last_scan_at: string | null;
  average_security_score: number | null;
  total_findings: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  info_count: number;
}

export interface SeverityTrendPoint {
  date: string;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface TopItem {
  label: string;
  count: number;
}

export interface FindingFilters {
  project_id: string;
  scan_id?: string;
  severity?: Severity;
  language?: Language;
  category?: string;
  file_path?: string;
  created_after?: string;
}
