from enum import StrEnum


class Role(StrEnum):
    COMMITTEE_MEMBER = "committee_member"
    HOD = "hod"


class UserStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


class MissionStatus(StrEnum):
    DRAFT = "draft"
    AWAITING_HOD_CONFIRMATION = "awaiting_hod_confirmation"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MessageDirection(StrEnum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"


class MessageKind(StrEnum):
    ENQUIRY = "enquiry"
    CLARIFICATION = "clarification"
    FOLLOW_UP = "follow_up"
    COUNTEROFFER = "counteroffer"
    TERMS = "terms"


class MessageStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    SENT = "sent"
    RECEIVED = "received"
    REFUSED = "refused"


class NegotiationStatus(StrEnum):
    PROPOSED = "proposed"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTERED = "countered"
    WITHDRAWN = "withdrawn"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"
    FAILED = "failed"


class VerificationState(StrEnum):
    """The nine verified-result states (blueprint Section 11)."""

    RESEARCH_RESULT = "research_result"
    ESTIMATE = "estimate"
    DRAFT_AWAITING_APPROVAL = "draft_awaiting_approval"
    MESSAGE_SENT = "message_sent"
    REPLY_RECEIVED = "reply_received"
    OFFER_PROPOSED = "offer_proposed"
    OFFER_ACCEPTED_DETAILS_PENDING = "offer_accepted_details_pending"
    TERMS_VERIFIED = "terms_verified"
    USER_APPROVED_COMMITMENT = "user_approved_commitment"


def sql_in(enum_cls: type[StrEnum]) -> str:
    """`'a', 'b', 'c'` for CHECK constraints."""
    return ", ".join(f"'{member.value}'" for member in enum_cls)
