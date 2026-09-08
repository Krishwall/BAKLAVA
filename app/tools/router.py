from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.tools.model import Tool
from app.tools.schemas import ToolCreate, ToolResponse

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.post("", response_model=ToolResponse, status_code=201)
def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
    existing_tool = db.get(Tool, tool.tool_id)

    if existing_tool:
        raise HTTPException(
            status_code=409,
            detail="Tool already exists",
        )

    db_tool = Tool(**tool.model_dump())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)

    return db_tool


@router.get("/{tool_id}", response_model=ToolResponse)
def get_tool(tool_id: str, db: Session = Depends(get_db)):
    tool = db.get(Tool, tool_id)

    if not tool:
        raise HTTPException(
            status_code=404,
            detail="Tool not found",
        )

    return tool


@router.get("", response_model=list[ToolResponse])
def list_tools(db: Session = Depends(get_db)):
    return db.query(Tool).all()


@router.post("/{tool_id}/suspend")
def suspend_tool(
    tool_id: str,
    db: Session = Depends(get_db),
):
    tool = db.get(Tool, tool_id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found",
        )

    if tool.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot suspend tool with status '{tool.status}'",
        )

    tool.status = "suspended"
    db.commit()
    db.refresh(tool)

    return tool


@router.post("/{tool_id}/reactivate")
def reactivate_tool(
    tool_id: str,
    db: Session = Depends(get_db),
):
    tool = db.get(Tool, tool_id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found",
        )

    if tool.status != "suspended":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reactivate tool with status '{tool.status}'",
        )

    tool.status = "active"
    db.commit()
    db.refresh(tool)

    return tool


@router.post("/{tool_id}/deregister")
def deregister_tool(
    tool_id: str,
    db: Session = Depends(get_db),
):
    tool = db.get(Tool, tool_id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found",
        )

    if tool.status == "deregistered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool is already deregistered",
        )

    tool.status = "deregistered"
    db.commit()
    db.refresh(tool)

    return tool
