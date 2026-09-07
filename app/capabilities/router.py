from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.capabilities.model import Capability
from app.capabilities.schemas import CapabilityCreate, CapabilityResponse
from app.db.database import get_db

router = APIRouter(
    prefix="/capabilities",
    tags=["Capabilities"],
)


@router.post(
    "",
    response_model=CapabilityResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_capability(
    capability: CapabilityCreate,
    db: Session = Depends(get_db),
) -> Capability:
    existing_capability = db.get(Capability, capability.capability_id)

    if existing_capability:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Capability already registered",
        )

    db_capability = Capability(**capability.model_dump())

    db.add(db_capability)
    db.commit()
    db.refresh(db_capability)

    return db_capability


@router.get("", response_model=list[CapabilityResponse])
def list_capabilities(
    db: Session = Depends(get_db),
) -> list[Capability]:
    return db.query(Capability).all()


@router.get("/{capability_id}", response_model=CapabilityResponse)
def get_capability(
    capability_id: str,
    db: Session = Depends(get_db),
) -> Capability:
    capability = db.get(Capability, capability_id)

    if not capability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Capability not found",
        )

    return capability
