from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.denuncia import Denuncia
from app.repositories.base import BaseRepository
from app.schemas.denuncia import Denuncia as DenunciaSchema


class DenunciaRepository(BaseRepository[Denuncia]):
    def __init__(self, db: Session):
        super().__init__(db, Denuncia)

    def get_by_hash(self, hash_dados: str) -> Optional[Denuncia]:
        """
        Get denuncia by its hash_dados field.
        """
        return self.db.query(self.model).filter(self.model.hash_dados == hash_dados).first()

    def get_all_by_categoria(self, categoria: str) -> List[Denuncia]:
        """
        Get all denuncias by categoria.
        """
        return self.db.query(self.model).filter(self.model.categoria == categoria).all()

    def create_from_schema(self, denuncia: DenunciaSchema, hash_dados: str) -> Denuncia:
        """
        Create denuncia from schema and hash_dados.
        """
        nova_denuncia = Denuncia(
            descricao=denuncia.descricao,
            categoria=denuncia.categoria,
            latitude=denuncia.latitude,
            longitude=denuncia.longitude,
            hash_dados=hash_dados,
            datetime=denuncia.datetime
        )
        self.db.add(nova_denuncia)
        self.db.commit()
        self.db.refresh(nova_denuncia)
        return nova_denuncia
