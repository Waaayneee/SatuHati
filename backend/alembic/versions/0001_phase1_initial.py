"""phase 1 initial schema: missions, access control, approvals, audit log

Revision ID: 0001_phase1
Revises:
Create Date: 2026-10-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_phase1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = [
    "approval_policies",
    "audit_log",
    "evidence_sources",
    "users",
    "missions",
    "role_assignments",
    "stakeholders",
    "approvals",
    "negotiations",
    "quotations",
    "messages",
    "outcomes",
]


def upgrade() -> None:
    op.execute("CREATE SEQUENCE mission_code_seq START WITH 1")

    op.create_table('approval_policies',
    sa.Column('action_type', sa.Text(), nullable=False),
    sa.Column('tier', sa.SmallInteger(), nullable=False),
    sa.Column('eligible_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('is_external', sa.Boolean(), nullable=False),
    sa.Column('ttl_hours', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('tier >= 0 AND tier <= 3', name=op.f('ck_approval_policies_tier_range')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_approval_policies')),
    sa.UniqueConstraint('action_type', name=op.f('uq_approval_policies_action_type'))
    )
    op.create_table('audit_log',
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('at', sa.DateTime(timezone=True), server_default=sa.text('clock_timestamp()'), nullable=False),
    sa.Column('actor', sa.Text(), nullable=False),
    sa.Column('actor_role', sa.Text(), nullable=True),
    sa.Column('mission_id', sa.Uuid(), nullable=True),
    sa.Column('event_type', sa.Text(), nullable=False),
    sa.Column('tool_name', sa.Text(), nullable=True),
    sa.Column('input_ref', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('result_ref', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('status', sa.Text(), server_default='ok', nullable=False),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_log'))
    )
    op.create_index('ix_audit_log_mission_id_at', 'audit_log', ['mission_id', 'at'], unique=False)
    op.create_table('evidence_sources',
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('retrieved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('claim', sa.Text(), nullable=True),
    sa.Column('confidence', sa.Numeric(precision=3, scale=2), nullable=True),
    sa.Column('caveat', sa.Text(), nullable=True),
    sa.Column('is_simulated', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('confidence >= 0 AND confidence <= 1', name=op.f('ck_evidence_sources_confidence_range')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_evidence_sources'))
    )
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('status', sa.Text(), server_default='active', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('active', 'disabled')", name=op.f('ck_users_status')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    op.create_table('missions',
    sa.Column('code', sa.Text(), nullable=False),
    sa.Column('owner_id', sa.Uuid(), nullable=False),
    sa.Column('goal_text', sa.Text(), nullable=False),
    sa.Column('product', sa.Text(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('target_total_myr', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('hard_budget_myr', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('minimum_quality', sa.Numeric(precision=3, scale=1), nullable=True),
    sa.Column('delivery_deadline', sa.Date(), nullable=True),
    sa.Column('max_rounds', sa.Integer(), server_default='3', nullable=False),
    sa.Column('approval_policy', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('status', sa.Text(), server_default='draft', nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('limits_confirmed_by', sa.Uuid(), nullable=True),
    sa.Column('limits_confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('draft', 'awaiting_hod_confirmation', 'active', 'completed', 'cancelled')", name=op.f('ck_missions_status')),
    sa.CheckConstraint('hard_budget_myr > 0', name=op.f('ck_missions_hard_budget_positive')),
    sa.CheckConstraint('max_rounds >= 1 AND max_rounds <= 10', name=op.f('ck_missions_max_rounds_range')),
    sa.CheckConstraint('minimum_quality >= 0 AND minimum_quality <= 5', name=op.f('ck_missions_minimum_quality_range')),
    sa.CheckConstraint('quantity > 0', name=op.f('ck_missions_quantity_positive')),
    sa.CheckConstraint('target_total_myr <= hard_budget_myr', name=op.f('ck_missions_target_within_budget')),
    sa.CheckConstraint('target_total_myr >= 0', name=op.f('ck_missions_target_non_negative')),
    sa.ForeignKeyConstraint(['limits_confirmed_by'], ['users.id'], name=op.f('fk_missions_limits_confirmed_by_users')),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('fk_missions_owner_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_missions')),
    sa.UniqueConstraint('code', name=op.f('uq_missions_code'))
    )
    op.create_index(op.f('ix_missions_owner_id'), 'missions', ['owner_id'], unique=False)
    op.create_table('role_assignments',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('role', sa.Text(), nullable=False),
    sa.Column('org_scope', sa.Text(), server_default='default', nullable=False),
    sa.Column('assigned_by', sa.Text(), nullable=False),
    sa.Column('assigned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("role IN ('committee_member', 'hod')", name=op.f('ck_role_assignments_role')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_role_assignments_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_role_assignments')),
    sa.UniqueConstraint('user_id', 'role', 'org_scope', name='uq_role_assignments_user_role_scope')
    )
    op.create_index(op.f('ix_role_assignments_user_id'), 'role_assignments', ['user_id'], unique=False)
    op.create_table('stakeholders',
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('org_type', sa.Text(), nullable=True),
    sa.Column('contact_channel', sa.Text(), nullable=True),
    sa.Column('contact_value', sa.Text(), nullable=True),
    sa.Column('contact_verified', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('opted_out', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('source_id', sa.Uuid(), nullable=True),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['evidence_sources.id'], name=op.f('fk_stakeholders_source_id_evidence_sources')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_stakeholders'))
    )
    op.create_table('approvals',
    sa.Column('mission_id', sa.Uuid(), nullable=True),
    sa.Column('action_type', sa.Text(), nullable=False),
    sa.Column('tier', sa.SmallInteger(), nullable=False),
    sa.Column('requested_by', sa.Text(), nullable=False),
    sa.Column('requested_on_behalf_of', sa.Uuid(), nullable=True),
    sa.Column('eligible_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.Text(), server_default='pending', nullable=False),
    sa.Column('approver_id', sa.Uuid(), nullable=True),
    sa.Column('approver_role', sa.Text(), nullable=True),
    sa.Column('decision_reason', sa.Text(), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('content_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('content_hash', sa.Text(), nullable=False),
    sa.Column('token_hash', sa.Text(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('hard_budget_at_request', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('execution_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('pending', 'approved', 'rejected', 'expired', 'executed', 'failed')", name=op.f('ck_approvals_status')),
    sa.CheckConstraint('tier >= 1 AND tier <= 3', name=op.f('ck_approvals_tier_range')),
    sa.ForeignKeyConstraint(['approver_id'], ['users.id'], name=op.f('fk_approvals_approver_id_users')),
    sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name=op.f('fk_approvals_mission_id_missions')),
    sa.ForeignKeyConstraint(['requested_on_behalf_of'], ['users.id'], name=op.f('fk_approvals_requested_on_behalf_of_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_approvals'))
    )
    op.create_index(op.f('ix_approvals_mission_id'), 'approvals', ['mission_id'], unique=False)
    op.create_table('negotiations',
    sa.Column('mission_id', sa.Uuid(), nullable=False),
    sa.Column('stakeholder_id', sa.Uuid(), nullable=False),
    sa.Column('round_number', sa.Integer(), nullable=False),
    sa.Column('offer_total', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('response', sa.Text(), nullable=True),
    sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("status IN ('proposed', 'sent', 'accepted', 'rejected', 'countered', 'withdrawn')", name=op.f('ck_negotiations_status')),
    sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name=op.f('fk_negotiations_mission_id_missions')),
    sa.ForeignKeyConstraint(['stakeholder_id'], ['stakeholders.id'], name=op.f('fk_negotiations_stakeholder_id_stakeholders')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_negotiations')),
    sa.UniqueConstraint('mission_id', 'stakeholder_id', 'round_number', name='uq_negotiations_round')
    )
    op.create_index(op.f('ix_negotiations_mission_id'), 'negotiations', ['mission_id'], unique=False)
    op.create_table('quotations',
    sa.Column('mission_id', sa.Uuid(), nullable=False),
    sa.Column('stakeholder_id', sa.Uuid(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('total_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('currency', sa.Text(), server_default='MYR', nullable=False),
    sa.Column('delivery_cost', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('tax_fees', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('lead_days', sa.Integer(), nullable=True),
    sa.Column('valid_until', sa.Date(), nullable=True),
    sa.Column('source_id', sa.Uuid(), nullable=True),
    sa.Column('verification_state', sa.Enum('research_result', 'estimate', 'draft_awaiting_approval', 'message_sent', 'reply_received', 'offer_proposed', 'offer_accepted_details_pending', 'terms_verified', 'user_approved_commitment', name='verification_state'), server_default='research_result', nullable=False),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name=op.f('fk_quotations_mission_id_missions')),
    sa.ForeignKeyConstraint(['source_id'], ['evidence_sources.id'], name=op.f('fk_quotations_source_id_evidence_sources')),
    sa.ForeignKeyConstraint(['stakeholder_id'], ['stakeholders.id'], name=op.f('fk_quotations_stakeholder_id_stakeholders')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_quotations'))
    )
    op.create_index(op.f('ix_quotations_mission_id'), 'quotations', ['mission_id'], unique=False)
    op.create_table('messages',
    sa.Column('mission_id', sa.Uuid(), nullable=False),
    sa.Column('stakeholder_id', sa.Uuid(), nullable=True),
    sa.Column('direction', sa.Text(), nullable=False),
    sa.Column('kind', sa.Text(), nullable=False),
    sa.Column('channel', sa.Text(), server_default='email', nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('proposed_total_myr', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('status', sa.Text(), nullable=False),
    sa.Column('is_simulated', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('approval_id', sa.Uuid(), nullable=True),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("direction IN ('outbound', 'inbound')", name=op.f('ck_messages_direction')),
    sa.CheckConstraint("kind IN ('enquiry', 'clarification', 'follow_up', 'counteroffer', 'terms')", name=op.f('ck_messages_kind')),
    sa.CheckConstraint("status IN ('draft', 'pending_approval', 'sent', 'received', 'refused')", name=op.f('ck_messages_status')),
    sa.ForeignKeyConstraint(['approval_id'], ['approvals.id'], name=op.f('fk_messages_approval_id_approvals')),
    sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name=op.f('fk_messages_mission_id_missions')),
    sa.ForeignKeyConstraint(['stakeholder_id'], ['stakeholders.id'], name=op.f('fk_messages_stakeholder_id_stakeholders')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_messages'))
    )
    op.create_index(op.f('ix_messages_approval_id'), 'messages', ['approval_id'], unique=False)
    op.create_index(op.f('ix_messages_mission_id'), 'messages', ['mission_id'], unique=False)
    op.create_table('outcomes',
    sa.Column('mission_id', sa.Uuid(), nullable=False),
    sa.Column('selected_quotation_id', sa.Uuid(), nullable=True),
    sa.Column('terms_verified', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('approval_status', sa.Text(), nullable=True),
    sa.Column('savings_myr', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('caveats', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['mission_id'], ['missions.id'], name=op.f('fk_outcomes_mission_id_missions')),
    sa.ForeignKeyConstraint(['selected_quotation_id'], ['quotations.id'], name=op.f('fk_outcomes_selected_quotation_id_quotations')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_outcomes'))
    )
    op.create_index(op.f('ix_outcomes_mission_id'), 'outcomes', ['mission_id'], unique=False)

    # audit_log is append-only: block UPDATE, DELETE and TRUNCATE.
    op.execute(
        """
        CREATE FUNCTION audit_log_block_mutation() RETURNS trigger
        LANGUAGE plpgsql
        SET search_path = ''
        AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log is append-only: % is not allowed', TG_OP;
        END;
        $$
        """
    )
    op.execute(
        "CREATE TRIGGER audit_log_no_update_delete BEFORE UPDATE OR DELETE ON audit_log "
        "FOR EACH ROW EXECUTE FUNCTION audit_log_block_mutation()"
    )
    op.execute(
        "CREATE TRIGGER audit_log_no_truncate BEFORE TRUNCATE ON audit_log "
        "FOR EACH STATEMENT EXECUTE FUNCTION audit_log_block_mutation()"
    )

    # Row Level Security with no policies: the public Supabase API can neither read
    # nor write these tables. The backend connects as the table owner and is the
    # only access path.
    for table in [*TABLES, "alembic_version"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    for table in reversed(TABLES):
        op.drop_table(table)
    op.execute("DROP FUNCTION IF EXISTS audit_log_block_mutation()")
    op.execute("DROP TYPE IF EXISTS verification_state")
    op.execute("DROP SEQUENCE IF EXISTS mission_code_seq")
