from typing import Generic, TypeVar, Type, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc
from app.database import Base, SessionLocal
from datetime import datetime, timezone

ModelType = TypeVar("ModelType", bound=Base)


class RepositoryException(Exception):
    pass


class BaseRepository(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], db: SessionLocal):
        self.model = model
        self.db = db

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def create(self, **kwargs) -> ModelType:
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.flush() 
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to create {self.model.__name__}: {e}") from e

    def save(self, instance: ModelType) -> ModelType:
        """Stage an already-constructed instance."""
        try:
            self.db.add(instance)
            self.db.flush()
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to save {self.model.__name__}: {e}") from e
        
    def bulk_create(self, records: list[dict]) -> list[ModelType]:
        try:
            instances = [self.model(**r) for r in records]
            self.db.add_all(instances)
            self.db.commit()
            for instance in instances:
                self.db.refresh(instance)
            return instances
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to bulk create {self.model.__name__}: {e}") from e

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    def find_by_id(self, id: Any) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def find_one(self, **filters) -> ModelType | None:
        query = self.db.query(self.model)
        for field, value in filters.items():
            column = getattr(self.model, field, None)
            if column is None:
                raise RepositoryException(f"'{field}' is not a valid column on {self.model.__name__}")
            query = query.filter(column == value)
        return query.first()

    def find_all(
        self,
        filters: dict | None = None,
        order_by: str | None = None,
        order_dir: str = "asc",
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        search_fields: list[str] | None = None,
    ) -> list[ModelType]:
        from sqlalchemy import or_

        query = self.db.query(self.model)

        # Apply equality filters
        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field, None)
                if column is None:
                    raise RepositoryException(f"'{field}' is not a valid column")
                if value is None:
                    query = query.filter(column.is_(None))
                elif isinstance(value, list):
                    query = query.filter(column.in_(value))
                else:
                    query = query.filter(column == value)

        # Apply search across multiple fields with ILIKE (case-insensitive)
        if search and search_fields:
            valid_columns = [
                getattr(self.model, field)
                for field in search_fields
                if hasattr(self.model, field)
            ]

            if valid_columns:  # avoid empty OR()
                search_term = f"%{search}%"
                query = query.filter(
                    or_(*[col.ilike(search_term) for col in valid_columns])
                )

        # Apply ordering
        if order_by:
            column = getattr(self.model, order_by, None)
            if column is None:
                raise RepositoryException(f"Cannot order by '{order_by}'")
            query = query.order_by(desc(column) if order_dir.lower() == "desc" else asc(column))

        return query.offset(skip).limit(min(limit, 100)).all()


    def count(self, **filters) -> int:
        query = self.db.query(self.model)
        for field, value in filters.items():
            column = getattr(self.model, field, None)
            if column is not None:
                query = query.filter(column == value)
        return query.count()

    def exists(self, **filters) -> bool:
        return self.find_one(**filters) is not None

    def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict | None = None,
        order_by: str | None = None,
        order_dir: str = "asc",
        search: str | None = None,
        search_fields: list[str] | None = None,
    ) -> dict:
        page = max(1, page)
        page_size = min(page_size, 100)
        skip = (page - 1) * page_size

        items = self.find_all(
            filters=filters,
            order_by=order_by,
            order_dir=order_dir,
            skip=skip,
            limit=page_size,
            search=search,
            search_fields=search_fields,
        )
        total = self.count(filters=filters, search=search, search_fields=search_fields)
        total_pages = max(1, -(-total // page_size))

        return {
            "items":       items,
            "total":       total,
            "page":        page,
            "page_size":   page_size,
            "total_pages": total_pages,
            "has_next":    page < total_pages,
            "has_prev":    page > 1,
        }

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    def update(self, id: Any, **kwargs) -> ModelType | None:
        try:
            instance = self.find_by_id(id)
            if not instance:
                return None
            for field, value in kwargs.items():
                if hasattr(instance, field):
                    setattr(instance, field, value)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to update {self.model.__name__} {id}: {e}") from e

    def update_where(self, filters: dict, **kwargs) -> int:
        try:
            query = self.db.query(self.model)
            for field, value in filters.items():
                column = getattr(self.model, field, None)
                if column is not None:
                    query = query.filter(column == value)
            count = query.update(kwargs, synchronize_session="fetch")
            self.db.commit()
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to bulk update {self.model.__name__}: {e}") from e

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete(self, id: Any) -> bool:
        try:
            instance = self.find_by_id(id)
            if not instance:
                return False
            self.db.delete(instance)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to delete {self.model.__name__} {id}: {e}") from e

    def soft_delete(self, id: Any, deleted_field: str = "deleted_at") -> ModelType | None:
        if not hasattr(self.model, deleted_field):
            raise RepositoryException(
                f"{self.model.__name__} has no '{deleted_field}' column. Add it to enable soft deletes."
            )
        from datetime import datetime
        return self.update(id, **{deleted_field: datetime.now(timezone.utc)})