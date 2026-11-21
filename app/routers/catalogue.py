"""Router catalogue: /me, /levels, /subjects, /agents."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Level, Subject, Agent
from app.schemas import UserOut, LevelOut, SubjectOut, AgentOut

router = APIRouter(tags=["catalogue"])


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user


@router.get("/levels", response_model=list[LevelOut])
async def list_levels(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Level).order_by(Level.id))).scalars().all()


@router.get("/subjects", response_model=list[SubjectOut])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Subject).order_by(Subject.id))).scalars().all()


@router.get("/agents", response_model=list[AgentOut])
async def list_agents(
    level_id: int | None = Query(default=None),
    subject_slug: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    q = select(Agent).options(selectinload(Agent.level), selectinload(Agent.subject)).where(Agent.is_active == True)
    if level_id:
        q = q.where(Agent.level_id == level_id)
    if subject_slug:
        q = q.join(Subject).where(Subject.slug == subject_slug)
    q = q.order_by(Agent.agent_name)
    return (await db.execute(q)).scalars().all()
