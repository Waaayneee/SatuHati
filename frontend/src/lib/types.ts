export type Role = "hod" | "committee_member";

export interface Me {
  id: string;
  email: string;
  name: string | null;
  roles: Role[];
  primary_role: Role;
}

export interface Mission {
  id: string;
  code: string;
  owner_id: string;
  owner_email: string | null;
  goal_text: string;
  product: string | null;
  quantity: number | null;
  target_total_myr: number | null;
  hard_budget_myr: number | null;
  minimum_quality: number | null;
  delivery_deadline: string | null;
  max_rounds: number;
  status: "draft" | "awaiting_hod_confirmation" | "active" | "completed" | "cancelled";
  notes: string | null;
  limits_confirmed_at: string | null;
  created_at: string;
}

export interface ApprovalSummary {
  id: string;
  mission_id: string | null;
  mission_code: string | null;
  action_type: string;
  tier: number;
  status: "pending" | "approved" | "rejected" | "expired" | "executed" | "failed";
  requested_by: string;
  requester_label: string;
  eligible_roles: string[];
  expires_at: string;
  created_at: string;
  decided_at: string | null;
  approver_role: string | null;
  recipient_name: string | null;
  kind: string | null;
  proposed_total_myr: number | null;
  hard_budget_myr: number | null;
  target_total_myr: number | null;
  preview: string | null;
}

export interface ApprovalDetail extends ApprovalSummary {
  content_snapshot: Record<string, unknown>;
  content_hash: string;
  decision_reason: string | null;
  approver_email: string | null;
  used_at: string | null;
  execution_result: Record<string, unknown> | null;
  budget: {
    hard_budget_myr: number | null;
    hard_budget_at_request: number | null;
    target_total_myr: number | null;
    proposed_total_myr: number | null;
    within_budget: boolean | null;
    difference_from_target_myr: number | null;
  };
  can_decide: boolean;
  cannot_decide_reason: string | null;
}

export interface MessageRow {
  id: string;
  stakeholder_id: string | null;
  supplier: string | null;
  recipient: string | null;
  direction: string;
  kind: string;
  body: string;
  proposed_total_myr: number | null;
  status: string;
  is_simulated: boolean;
  approval_id: string | null;
  sent_at: string | null;
  created_at: string;
}

export interface QuotationRow {
  id: string;
  supplier: string;
  total_price: number | null;
  unit_price: number | null;
  verification_state: string;
  is_simulated: boolean;
}

export interface MissionDetail {
  mission: Mission;
  approvals: ApprovalSummary[];
  messages: MessageRow[];
  quotations: QuotationRow[];
}

export interface AuditRow {
  id: string;
  at: string;
  actor: string;
  actor_label: string;
  actor_role: string | null;
  mission_code: string | null;
  event_type: string;
  tool_name: string | null;
  status: string;
  error: string | null;
}

export interface UserRow {
  id: string;
  email: string;
  name: string | null;
  status: string;
  roles: Role[];
}

export interface AgentRun {
  status: "completed" | "approval_required" | "max_iterations" | "refused" | "incomplete" | "error";
  final_text: string;
  iterations: number;
  model: string;
  tool_calls: { name: string; status: string; approval_id: string | null; tier: number | null; reason: string | null }[];
  approvals: { approval_id: string; tier: number; action_type: string | null }[];
}
