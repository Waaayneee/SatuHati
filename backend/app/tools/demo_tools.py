"""Demo tools on simulated data (blueprint Section 17). Phase 3 replaces search_suppliers."""

import re
import uuid
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.models import EvidenceSource, Message, Quotation, Stakeholder
from app.models.enums import MessageDirection, MessageKind, MessageStatus, VerificationState
from app.services.errors import InvalidInput
from app.tools.context import ToolContext
from app.tools.registry import tool

# Demo data. Replace with live supplier APIs later (Phase 3).
DEMO_SUPPLIERS: list[dict[str, Any]] = [
    {"name": "Supplier A", "price": 1800, "rating": 4.6},
    {"name": "Supplier B", "price": 1450, "rating": 4.2},
    {"name": "Supplier C", "price": 1600, "rating": 4.8},
]
DEMO_CAVEAT = "Simulated demo data. Not a real supplier or a real quote."


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _demo_stakeholder(ctx: ToolContext, supplier: dict[str, Any]) -> tuple[Stakeholder, EvidenceSource]:
    """Find or create the simulated supplier and its evidence record."""
    db = ctx.db
    slug = _slug(supplier["name"])
    contact = f"sales@{slug}.demo.test"
    stakeholder = db.scalars(
        select(Stakeholder).where(Stakeholder.name == supplier["name"], Stakeholder.contact_value == contact)
    ).first()
    if stakeholder is not None and stakeholder.source_id is not None:
        source = db.get(EvidenceSource, stakeholder.source_id)
        if source is not None:
            return stakeholder, source
    source = EvidenceSource(
        url=f"demo://suppliers/{slug}",
        claim=f"Simulated total price RM{supplier['price']:,} with rating {supplier['rating']}",
        confidence=Decimal("0.50"),
        caveat=DEMO_CAVEAT,
        is_simulated=True,
    )
    db.add(source)
    db.flush()
    if stakeholder is None:
        stakeholder = Stakeholder(
            name=supplier["name"],
            org_type="supplier",
            contact_channel="email",
            contact_value=contact,
            contact_verified=False,
            source_id=source.id,
        )
        db.add(stakeholder)
    else:
        stakeholder.source_id = source.id
    db.flush()
    return stakeholder, source


# ---------------------------------------------------------------------------
# search_suppliers
# ---------------------------------------------------------------------------


class SearchSuppliersIn(StrictModel):
    product: str = Field(min_length=1, max_length=200, description="What to buy, e.g. custom tote bags.")
    budget: float = Field(gt=0, description="Budget in MYR to compare against, normally the mission hard budget.")


class SupplierResult(BaseModel):
    stakeholder_id: str
    name: str
    price: float
    rating: float
    within_budget: bool
    data_source: Literal["demo"] = "demo"


class SearchSuppliersOut(BaseModel):
    product: str
    budget: float
    suppliers: list[SupplierResult]
    data_source: Literal["demo"] = "demo"
    caveat: str = DEMO_CAVEAT


@tool(
    name="search_suppliers",
    description=(
        "Find candidate suppliers for the mission product and compare their total price against a budget. "
        "Phase 1 returns simulated demo suppliers only (data_source: demo). Each result has a stakeholder_id "
        "to use with prepare_counteroffer and send_approved_message. Call this before contacting anyone."
    ),
    action_type="search_suppliers",
    input_model=SearchSuppliersIn,
    output_model=SearchSuppliersOut,
)
def search_suppliers(ctx: ToolContext, args: SearchSuppliersIn) -> SearchSuppliersOut:
    db, mission = ctx.db, ctx.mission
    results = []
    for supplier in sorted(DEMO_SUPPLIERS, key=lambda s: s["price"]):
        stakeholder, source = _demo_stakeholder(ctx, supplier)
        has_quote = db.scalars(
            select(Quotation.id).where(Quotation.mission_id == mission.id, Quotation.stakeholder_id == stakeholder.id)
        ).first()
        if has_quote is None:
            total = Decimal(supplier["price"])
            unit = (total / mission.quantity).quantize(Decimal("0.01"), ROUND_HALF_UP) if mission.quantity else None
            db.add(
                Quotation(
                    mission_id=mission.id,
                    stakeholder_id=stakeholder.id,
                    total_price=total,
                    unit_price=unit,
                    currency="MYR",
                    source_id=source.id,
                    verification_state=VerificationState.RESEARCH_RESULT,
                )
            )
        results.append(
            SupplierResult(
                stakeholder_id=str(stakeholder.id),
                name=supplier["name"],
                price=supplier["price"],
                rating=supplier["rating"],
                within_budget=supplier["price"] <= args.budget,
            )
        )
    db.flush()
    return SearchSuppliersOut(product=args.product, budget=args.budget, suppliers=results)


# ---------------------------------------------------------------------------
# prepare_counteroffer
# ---------------------------------------------------------------------------


class PrepareCounterofferIn(StrictModel):
    supplier_name: str = Field(min_length=1, max_length=200)
    quoted_price: float = Field(description="The supplier's quoted total in MYR.")
    target_price: float = Field(description="The total you want to propose in MYR.")
    stakeholder_id: uuid.UUID | None = Field(None, description="Optional. Found by supplier_name if left out.")


class PrepareCounterofferOut(BaseModel):
    supplier: str
    stakeholder_id: str
    proposed_price: float
    message: str
    status: Literal["awaiting_user_approval"] = "awaiting_user_approval"
    sent: Literal[False] = False
    message_id: str
    within_hard_budget: bool


@tool(
    name="prepare_counteroffer",
    description=(
        "Draft a counteroffer message for a supplier. It is saved as a draft and never sent. To send it, "
        "pass the same text to send_approved_message with kind counteroffer and proposed_total_myr."
    ),
    action_type="prepare_counteroffer",
    input_model=PrepareCounterofferIn,
    output_model=PrepareCounterofferOut,
)
def prepare_counteroffer(ctx: ToolContext, args: PrepareCounterofferIn) -> PrepareCounterofferOut:
    if args.target_price <= 0 or args.quoted_price <= 0:
        raise InvalidInput("Prices must be positive")
    db, mission = ctx.db, ctx.mission
    if args.stakeholder_id is not None:
        stakeholder = db.get(Stakeholder, args.stakeholder_id)
    else:
        stakeholder = db.scalars(select(Stakeholder).where(Stakeholder.name == args.supplier_name)).first()
    if stakeholder is None:
        raise InvalidInput("Unknown supplier. Run search_suppliers first")

    quoted = Decimal(str(args.quoted_price))
    target = Decimal(str(args.target_price))
    body = (
        f"Thank you for your quotation of RM{quoted:.2f}. "
        f"Would you consider RM{target:.2f}? "
        "We would be happy to discuss mutually "
        "beneficial terms."
    )
    draft = Message(
        mission_id=mission.id,
        stakeholder_id=stakeholder.id,
        direction=MessageDirection.OUTBOUND.value,
        kind=MessageKind.COUNTEROFFER.value,
        channel=stakeholder.contact_channel or "email",
        body=body,
        proposed_total_myr=target,
        status=MessageStatus.DRAFT.value,
        is_simulated=True,
    )
    db.add(draft)
    db.flush()
    return PrepareCounterofferOut(
        supplier=stakeholder.name,
        stakeholder_id=str(stakeholder.id),
        proposed_price=float(target),
        message=body,
        message_id=str(draft.id),
        within_hard_budget=mission.hard_budget_myr is not None and target <= mission.hard_budget_myr,
    )
