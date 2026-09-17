export type Role = 'ADMIN' | 'SETTER' | 'REVIEWER' | 'CANDIDATE' | 'EXAM_OFFICER' | 'AUTHOR' | 'SECURITY_AUDITOR';
export type Difficulty = 'EASY' | 'MEDIUM' | 'HARD';
export type QuestionStatus = 'SUBMITTED' | 'IN_REVIEW' | 'APPROVED' | 'REJECTED' | 'RETIRED_EXPOSURE' | 'COMPROMISED';
export type ExposureStatus = 'ACTIVE' | 'WARNING' | 'HIGH_EXPOSURE' | 'COMPROMISED' | 'RETIRED_EXPOSURE';
export type ExamStatus = 'SCHEDULED' | 'RELEASED' | 'COMPLETED' | 'CANCELLED';
export type SessionStatus = 'ACTIVE' | 'COMPLETED' | 'TERMINATED';
export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AlertStatus = 'OPEN' | 'RESOLVED' | 'DISMISSED';

export interface ExposureOut {
  question_id: number;
  exposure_count: number;
  exposure_status: ExposureStatus;
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: Role;
}

export interface Question {
  id: number;
  content: string;
  subject: string;
  topic: string;
  difficulty: Difficulty;
  created_by: number;
  reviewer_id?: number | null;
  status: QuestionStatus;
  content_hash: string;
  crypto_version: string;
  exposure_count?: number;
  exposure_status?: ExposureStatus;
}

export interface BlueprintRule {
  topic: string;
  difficulty: Difficulty;
  count: number;
}

export interface Exam {
  id: number;
  name: string;
  subject: string;
  starts_at: string;
  ends_at: string;
  blueprint: BlueprintRule[];
  status: ExamStatus;
}

export interface ReleaseApproval {
  id: number;
  exam_id: number;
  officer_id: number;
  approved_at: string;
}

export interface ReleaseStatus {
  exam_id: number;
  status: string;
  release_window_open: boolean;
  required_approvals: number;
  approval_count: number;
  approver_ids: number[];
  released: boolean;
}

export interface CandidateQuestion {
  position: number;
  question_id: number;
  content: string;
  subject: string;
  topic: string;
  difficulty: Difficulty;
}

export interface ExamSession {
  session_id: number;
  exam_id: number;
  status: SessionStatus;
  question_count: number;
  started_at: string;
  session_token?: string | null;
  device_bound: boolean;
}

export interface SecurityEvent {
  id: number;
  event_type: string;
  risk_score: number;
  created_at: string;
}

export interface SecurityAlert {
  id: number;
  exam_id?: number | null;
  session_id?: number | null;
  candidate_id?: number | null;
  risk_score: number;
  severity: Severity;
  reasons: string[];
  status: AlertStatus;
  created_at: string;
}

export interface ExamCentre {
  id: number;
  code: string;
  name: string;
  status: string;
}

export interface CentreDevice {
  device_id: number;
  device_code: string;
  device_token?: string;
  warning?: string;
}

export interface CandidateAssignment {
  id: number;
  exam_id: number;
  candidate_id: number;
  centre_id: number;
  seat_number?: string | null;
  identity_status: 'PENDING' | 'VERIFIED' | 'REJECTED';
  verified_at?: string | null;
}

export interface PaperValidationReport {
  exam_id: number;
  status: 'PASS' | 'WARNING' | 'BLOCKED';
  syllabus_coverage: string;
  difficulty_balance: string;
  duplicate_detection: string;
  exposed_questions: string;
  compromised_questions: string;
  approval_status: string;
  details: string[];
}

export interface FingerprintMatch {
  match: boolean;
  question_id?: number | null;
  exam_id?: string | null;
  confidence: number;
  canonical_hash?: string | null;
  matched_subject?: string | null;
  matched_topic?: string | null;
}

export interface InvestigationResult {
  suspected_text_snippet: string;
  matches_found: number;
  top_match?: {
    question_id: number;
    confidence: number;
    exact_hash_match: boolean;
    fingerprint: string;
    subject: string;
    topic: string;
    difficulty: Difficulty;
    created_by?: { id: number; name: string; email: string } | null;
    reviewed_by?: { id: number; name: string; email: string } | null;
    status: QuestionStatus;
    exposure_count: number;
    associated_exam_ids: number[];
    sessions_received_count: number;
    security_events_count: number;
    blockchain_audit_events_count: number;
  } | null;
  all_candidate_matches: any[];
}

export interface DashboardSummary {
  totals: {
    users: number;
    questions: number;
    approved_questions: number;
    exposed_questions: number;
    exams: number;
    active_sessions: number;
    open_alerts: number;
  };
  question_status: Record<string, number>;
  exposure_status: Record<string, number>;
  role_counts: Record<string, number>;
  exam_status: Record<string, number>;
  session_status: Record<string, number>;
  alert_status: Record<string, number>;
  chain: {
    verification: { valid: boolean; blocks?: number; last_hash?: string };
    recent: any[];
  };
  exposure_ranking: {
    id: number;
    subject: string;
    topic: string;
    difficulty: string;
    exposure_count: number;
    exposure_status: string;
  }[];
  recent_alerts: {
    id: number;
    risk_score: number;
    severity: Severity;
    status: AlertStatus;
    candidate_id?: number | null;
    exam_id?: number | null;
    reasons: string[];
    created_at?: string | null;
  }[];
}
