from abc import ABC
from typing import Generic, TypeVar, List, Optional, Type, Any

from sqlalchemy.orm import Session

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """
    Base repository interface with common CRUD operations.
    """

    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    def get_by_id(self, id: Any) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[T]:
        return self.db.query(self.model).all()

    def create(self, obj_in: Any) -> T:
        db_obj = self.model(
            **obj_in if isinstance(obj_in, dict) else obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: T, obj_in: Any) -> T:
        obj_data = obj_in if isinstance(
            obj_in, dict) else obj_in.dict(exclude_unset=True)

        for key, value in obj_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        obj = self.db.query(self.model).get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
