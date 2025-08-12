from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from services.service_mikrotik.mikrotik import MikroTikProfileCreator
from crud.package import get_unsynced_packages, sync_package
from  models import Package
from database import get_session
from schema.package import  PackageCreate, PackageReadSimple,PackageUpdate
from typing import Annotated, List
from fastapi import Query, HTTPException
from sqlmodel import select
from uuid import UUID

router = APIRouter(prefix="/packages", tags=["Packages"])

@router.post("/sync")
async def sync_all_packages(session: Session = Depends(get_session), package_id: UUID = Query(..., description="ID of the package to sync")):
    creator = MikroTikProfileCreator("192.168.88.1", "admin", "admin")
    unsynced = get_unsynced_packages(Depends(get_session), package_id)
    results = []

    for package in unsynced:
        success = sync_package(Depends(get_session), package, creator)
        results.append({package.name: "✅" if success else "❌"})

    return {"results": results}



@router.post("/add_package/", response_model=PackageReadSimple)
async def create_hero(package: PackageCreate, session: Session = Depends(get_session)):
    db_package = Package.model_validate(package)
    session.add(db_package)
    session.commit()
    session.refresh(db_package)
    return db_package



@router.get("/get_package/", response_model=list[PackageReadSimple])
async def read_heroes(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    packages = session.exec(select(Package).offset(offset).limit(limit)).all()
    return packages


# Code above omitted 👆

@router.get("/package/{package_id}", response_model=PackageReadSimple)
def read_package(package_id: UUID, session: Session = Depends(get_session)):
    package = session.get(Package, package_id)
    if not package:
        raise HTTPException(status_code=404, detail="package not found")
    return package



# Code above omitted 👆

@router.patch("/package/{package_id}", response_model= PackageReadSimple)
def update_hero(package_id: UUID, hero: PackageUpdate, session: Session = Depends(get_session)):
    package_db = session.get(Package, package_id)
    if not package_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    package_db.sqlmodel_update(hero_data)
    session.add(package_db)
    session.commit()
    session.refresh(package_db)
    return package_db



@router.delete("/package/{package_id}")
def delete_hero(package_id: UUID, session: Session = Depends(get_session)):
    package = session.get(Package, package_id)
    if not package:
        raise HTTPException(status_code=404, detail="package not found")
    session.delete(package)
    session.commit()
    return {"ok": True}   