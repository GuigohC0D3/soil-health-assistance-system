from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.property import Property
from app.models.user import User
from app.schemas.property import PropertyCreate, PropertyResponse, PropertyUpdate

router = APIRouter()


def _get_property_or_404(prop_id: int, db: Session, user: User) -> Property:
    prop = db.query(Property).filter(
        Property.id == prop_id, Property.proprietario_id == user.id
    ).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Propriedade não encontrada")
    return prop


@router.get("/", response_model=List[PropertyResponse])
def list_properties(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Property)
        .filter(Property.proprietario_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = Property(**payload.model_dump(), proprietario_id=current_user.id)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("/{prop_id}", response_model=PropertyResponse)
def get_property(
    prop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _get_property_or_404(prop_id, db, current_user)


@router.put("/{prop_id}", response_model=PropertyResponse)
def update_property(
    prop_id: int,
    payload: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = _get_property_or_404(prop_id, db, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/{prop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    prop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prop = _get_property_or_404(prop_id, db, current_user)
    db.delete(prop)
    db.commit()
