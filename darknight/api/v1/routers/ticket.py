from fastapi import APIRouter, Depends, HTTPException, Query

from darknight.db import Session, crud, get_db
from darknight.models.admin import Admin
from darknight.models.portal_auth import PortalUser
from darknight.models.ticket import (
    AdminTicketListItem,
    TicketAdminModify,
    TicketCreate,
    TicketDetail,
    TicketListItem,
    TicketReplyCreate,
    TicketReplyResponse,
    TicketStatus,
    TicketUserModify,
)
from darknight.utils import responses

router = APIRouter(tags=["Ticket"], responses={401: responses._401})


def _get_db_user(portal_user: PortalUser, db: Session):
    dbuser = crud.get_user(db, portal_user.username)
    if not dbuser:
        raise HTTPException(status_code=404, detail="User not found")
    return dbuser


def _ticket_detail(ticket) -> TicketDetail:
    return TicketDetail(
        id=ticket.id,
        subject=ticket.subject,
        priority=ticket.priority,
        status=ticket.status,
        created_at=ticket.created_at,
        last_reply_at=ticket.last_reply_at,
        replies=[TicketReplyResponse.model_validate(r) for r in ticket.replies],
    )


def _get_user_ticket(ticket_id: int, portal_user: PortalUser, db: Session):
    dbuser = _get_db_user(portal_user, db)
    ticket = crud.get_ticket_with_replies(db, ticket_id)
    if not ticket or ticket.user_id != dbuser.id:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket, dbuser


def _get_admin_ticket(ticket_id: int, db: Session):
    ticket = crud.get_ticket_with_replies(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/tickets", response_model=list[TicketListItem])
def list_tickets(
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    return crud.list_tickets_for_user(db, dbuser.id)


@router.post("/tickets", response_model=TicketDetail)
def create_ticket(
    body: TicketCreate,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    dbuser = _get_db_user(portal_user, db)
    ticket = crud.create_ticket(db, dbuser.id, body)
    ticket = crud.get_ticket_with_replies(db, ticket.id)
    return _ticket_detail(ticket)


@router.get("/tickets/{ticket_id}", response_model=TicketDetail)
def get_ticket(
    ticket_id: int,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    ticket, _ = _get_user_ticket(ticket_id, portal_user, db)
    return _ticket_detail(ticket)


@router.post("/tickets/{ticket_id}/replies", response_model=TicketDetail)
def reply_ticket(
    ticket_id: int,
    body: TicketReplyCreate,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    ticket, dbuser = _get_user_ticket(ticket_id, portal_user, db)
    try:
        crud.add_user_ticket_reply(db, ticket, dbuser.id, body.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    ticket = crud.get_ticket_with_replies(db, ticket_id)
    return _ticket_detail(ticket)


@router.patch("/tickets/{ticket_id}", response_model=TicketDetail)
def modify_ticket(
    ticket_id: int,
    body: TicketUserModify,
    portal_user: PortalUser = Depends(PortalUser.get_current),
    db: Session = Depends(get_db),
):
    ticket, _ = _get_user_ticket(ticket_id, portal_user, db)
    if body.status is None:
        raise HTTPException(status_code=400, detail="status is required")
    if body.status not in (TicketStatus.resolved, TicketStatus.closed):
        raise HTTPException(status_code=400, detail="Invalid status")
    try:
        crud.update_ticket_user_status(db, ticket, body.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    ticket = crud.get_ticket_with_replies(db, ticket_id)
    return _ticket_detail(ticket)


@router.get("/admin/tickets", response_model=list[AdminTicketListItem])
def admin_list_tickets(
    status: TicketStatus | None = None,
    priority: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: Admin = Depends(Admin.get_current),
):
    from darknight.models.ticket import TicketPriority

    priority_enum = TicketPriority(priority) if priority else None
    rows = crud.list_admin_tickets(
        db, status=status, priority=priority_enum, offset=offset, limit=limit
    )
    return [
        AdminTicketListItem(
            id=ticket.id,
            subject=ticket.subject,
            priority=ticket.priority,
            status=ticket.status,
            created_at=ticket.created_at,
            last_reply_at=ticket.last_reply_at,
            username=ticket.user.username if ticket.user else "",
        )
        for ticket in rows
    ]


@router.get("/admin/tickets/{ticket_id}", response_model=TicketDetail)
def admin_get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(Admin.get_current),
):
    ticket = _get_admin_ticket(ticket_id, db)
    return _ticket_detail(ticket)


@router.patch("/admin/tickets/{ticket_id}", response_model=TicketDetail)
def admin_modify_ticket(
    ticket_id: int,
    body: TicketAdminModify,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    ticket = _get_admin_ticket(ticket_id, db)
    crud.update_ticket_admin(db, ticket, status=body.status, priority=body.priority)
    ticket = crud.get_ticket_with_replies(db, ticket_id)
    return _ticket_detail(ticket)


@router.post("/admin/tickets/{ticket_id}/replies", response_model=TicketDetail)
def admin_reply_ticket(
    ticket_id: int,
    body: TicketReplyCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(Admin.get_current),
):
    ticket = _get_admin_ticket(ticket_id, db)
    try:
        crud.add_admin_ticket_reply(db, ticket, admin.id, body.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    ticket = crud.get_ticket_with_replies(db, ticket_id)
    return _ticket_detail(ticket)
