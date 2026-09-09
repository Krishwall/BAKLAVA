from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.capabilities.model import Capability
from app.db.database import get_db
from app.db.tool_capability import ToolCapability
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


@router.post(
    "/{tool_id}/capabilities/{capability_id}", status_code=status.HTTP_201_CREATED
)
def assign_capability(
    tool_id: str,
    capability_id: str,
    db: Session = Depends(get_db),
):
    tool = db.get(Tool, tool_id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found",
        )

    capability = db.get(Capability, capability_id)

    if not capability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capability not found",
        )

    existing = db.get(
        ToolCapability,
        (tool_id, capability_id),
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Capability already assigned to agent",
        )

    assignment = ToolCapability(
        tool_id=tool_id,
        capability_id=capability_id,
    )

    db.add(assignment)
    db.commit()

    return {
        "tool_id": tool_id,
        "capability_id": capability_id,
    }


@router.get("/{tool_id}/capabilities")
def list_tool_capabilities(
    tool_id: str,
    db: Session = Depends(get_db),
):
    tool = db.get(Tool, tool_id)

    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found",
        )

    capabilities = (
        db.query(Capability)
        .join(
            ToolCapability,
            ToolCapability.capability_id == Capability.capability_id,
        )
        .filter(ToolCapability.tool_id == tool_id)
        .all()
    )

    return capabilities


@router.delete(
    "/{tool_id}/capabilities/{capability_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_capability(
    tool_id: str,
    capability_id: str,
    db: Session = Depends(get_db),
):
    assignment = db.get(
        ToolCapability,
        (tool_id, capability_id),
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capability assignment not found",
        )

    db.delete(assignment)
    db.commit()
