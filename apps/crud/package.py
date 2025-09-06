from sqlmodel import Session, select
from apps.models.models import Package
from services.service_mikrotik.mikrotik import MikroTikProfileCreator
from fastapi import HTTPException
from database import get_session
from uuid import UUID


def get_unsynced_packages(session: Session, package_id :UUID ):
    return session.exec(select(Package).where(Package.is_synced == False and Package.id ==package_id and Package.statut !="delete")).all()


def sync_package(session: Session, package: Package, creator: MikroTikProfileCreator):
    profile_name = creator.create_profile_from_package(package)
    if profile_name and package.statut != "delete":
        package.is_synced = True
        package.mikrotik_profile_name = profile_name
        session.add(package)
        session.commit()
        return True
    return False

def get_package_by_id(session:Session, pakage_id:UUID):
    package = session.get(Package, pakage_id)
    if not package or package.statut == "delete":
        raise HTTPException(status_code=404, detail="Package not found")
    return package
