"""CLI entry for the Claude orchestrator.

Usage (from backend/):
  python -m app.agent.run --mission MISSION-001 "Find suppliers for 300 tote bags under RM1,500 and send an enquiry to the cheapest one"
  python -m app.agent.run --mission MISSION-001 --as chrispr@sunwaytechclub.com "..."

`--as` records which person the run is for, so that person cannot approve its Tier 1 requests.
"""

import argparse
import sys

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agent.claude_orchestrator import AgentConfigError, ClaudeOrchestrator
from app.db import get_engine
from app.models import User
from app.services.errors import DomainError
from app.services.mission_service import resolve_mission


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the KawTeam agent on one mission.")
    parser.add_argument("--mission", required=True, help="Mission code (MISSION-001) or ID")
    parser.add_argument("--as", dest="as_email", help="Email of the person this run is for")
    parser.add_argument("prompt", help="What the agent should do")
    args = parser.parse_args()

    with Session(get_engine()) as db:
        try:
            mission = resolve_mission(db, args.mission)
        except DomainError as exc:
            print(exc.message)
            return 1
        on_behalf_of = None
        if args.as_email:
            user = db.scalars(select(User).where(func.lower(User.email) == args.as_email.lower())).one_or_none()
            if user is None:
                print(f"No KawTeam user with email {args.as_email}")
                return 1
            on_behalf_of = user.id
        try:
            orchestrator = ClaudeOrchestrator(db)
        except AgentConfigError as exc:
            print(f"Agent not configured: {exc}")
            return 1
        result = orchestrator.run(mission, args.prompt, on_behalf_of=on_behalf_of)

    print(f"status: {result.status}  (model {result.model}, {result.iterations} model calls)")
    for call in result.tool_calls:
        extra = f"  approval {call.approval_id} Tier {call.tier}" if call.approval_id else ""
        reason = f"  ({call.reason})" if call.reason else ""
        print(f"  - {call.name}: {call.status}{extra}{reason}")
    if result.final_text:
        print("\n" + result.final_text)
    return 0 if result.status in ("completed", "approval_required") else 1


if __name__ == "__main__":
    sys.exit(main())
