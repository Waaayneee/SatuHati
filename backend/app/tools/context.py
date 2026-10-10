from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.auth.actor import Actor
from app.models import Mission


@dataclass
class ToolContext:
    """Everything a tool function may use. Tools never commit; the executor does."""

    db: Session
    actor: Actor
    mission: Mission
