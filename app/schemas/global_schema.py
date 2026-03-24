from pydantic import BaseModel
from typing import Optional

class PaginationParams(BaseModel):
    page:      int = 1
    page_size: int = 10
    order_by:  Optional[str] = None
    order_dir: Optional[str] = "asc"
    search:    Optional[str] = None
    def to_paginate_kwargs(
            self, 
            search_fields: list[str] | None = None,
        ) -> dict:
        """Convert pagination params to kwargs ready for repo.paginate()"""
        return {
            "page":          self.page,
            "page_size":     self.page_size,
            "order_by":      self.order_by,
            "order_dir":     self.order_dir or "asc",
            "search":        self.search,
            "search_fields": search_fields,
        }