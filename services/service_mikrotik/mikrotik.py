from routeros_api import RouterOsApiPool, exceptions
from models import Package
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class MikroTikProfileCreator:
    def __init__(self, host, username, password, port=8728):
        try:
            self.api_pool = RouterOsApiPool(
                host=host,
                username=username,
                password=password, 
                port=port
            )
            self.api = self.api_pool.get_api()
            self.profile_resource = self.api.get_resource('/tool/user-manager/profile')
        except Exception as e:
            logger.error(f"Connexion MikroTik échouée : {e}")
            raise HTTPException(status_code=500, detail="Erreur de connexion à MikroTik API")
        

    def create_profile_from_package(self, package: Package) -> str | None:
        try:
            self.profile_resource.add(
                name=package.mikrotik_profile_name,
                validity=f"{package.validity_hours}h",
                rate_limit=package.speed_limit or "1M/1M",
                price=str(package.price)
            )
            return package.mikrotik_profile_name
        except exceptions.RouterOsApiCommunicationError as e:
            logger.error(f"Erreur API MikroTik : {e}")
            raise HTTPException(status_code=500, detail="Erreur de communication avec MikroTik API")
        except exceptions.RouterOsApiError as e:
            logger.error(f"Erreur lors de la création du profil : {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la création du profil MikroTik")
        return None
