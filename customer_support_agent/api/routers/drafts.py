from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException

from customer_support_agent.api.dependencies import (
    get_copilot,
    get_draft_service,
    get_drafts_repository,
    get_tickets_repository,
)
from customer_support_agent.repositories.sqlite.drafts import DraftsRepository
from customer_support_agent.repositories.sqlite.tickets import TicketsRepository
from customer_support_agent.schemas.api import DraftResponse, DraftUpdateRequest
from customer_support_agent.services.draft_service import DraftService
from loguru import logger

router = APIRouter()

@router.get("/api/drafts/{ticket_id}", response_model=DraftResponse)
def get_draft_route(
    ticket_id: int,
    drafts_repo: DraftsRepository = Depends(get_drafts_repository),
    draft_service: DraftService = Depends(get_draft_service),
) -> dict:
    draft = drafts_repo.get_latest_for_ticket(ticket_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft_service.serialize_draft(draft)


@router.patch("/api/drafts/{draft_id}", response_model=DraftResponse)
def update_draft_route(
    draft_id: int,
    payload: DraftUpdateRequest,
    drafts_repo: DraftsRepository = Depends(get_drafts_repository),
    tickets_repo: TicketsRepository = Depends(get_tickets_repository),
    draft_service: DraftService = Depends(get_draft_service),
) -> dict:
    existing = drafts_repo.get_by_id(draft_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Draft not found")
    logger.info(f"Updating draft_id update_draft_route: {draft_id}")
    updated = drafts_repo.update(draft_id=draft_id, content=payload.content, status=payload.status)
    logger.info(f"Draft updated: {updated}")
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update draft")

    if payload.status == "accepted":
        relation = drafts_repo.get_ticket_and_customer_by_draft(draft_id)
        if relation:
            tickets_repo.set_status(relation["ticket_id"], "resolved")
            try:
                context_used = draft_service.parse_context_used(updated.get("context_used"))
                get_copilot().save_accepted_resolution(
                    customer_email=relation["customer_email"],
                    customer_company=relation.get("customer_company"),
                    ticket_subject=relation["subject"],
                    ticket_description=relation["description"],
                    draft_content=updated["content"],
                    context_used=context_used,
                )
                query = f"{relation['subject']} {relation.get('priority', '')}".strip()
                fresh_hits = get_copilot()._search_memory_scopes(
                query=query,
                customer_email=relation["customer_email"],
                customer_company=relation.get("customer_company"),
                limit=8)
                logger.info(f"Memory hits for accepted draft: {fresh_hits}")
                context_used["memory_hits"] = fresh_hits
                context_used.setdefault("signals", {})["memory_hit_count"] = len(fresh_hits)
                logger.info(f"Updating draft context_used with memory hits: {context_used}")
                updated["context_used"] = json.dumps(context_used)
                logger.info(f"Updating draft in database with new context_used: {updated['context_used']}")
            except Exception as exc:
              logger.exception("save_accepted_resolution / context_used update failed: %s", exc)

    return draft_service.serialize_draft(updated)