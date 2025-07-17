from typing import Generic, TypeVar, List, Optional
from urllib.parse import urlencode
from fastapi import Request
from pydantic import BaseModel, AnyHttpUrl

T = TypeVar('T', bound=BaseModel)

class PaginatedResult(Generic[T]):
    def __init__(
        self,
        items: List[T],
        request: Request,
        route_name: str,
        total: int,
        offset: int = 0,
        limit: int = 10,
    ):
        self.items = items
        self.total = total
        self.offset = offset
        self.limit = limit
        self.request = request
        self.route_name = route_name

    def to_dict(self) -> dict:   
        base_url = str(self.request.url_for(self.route_name))
        query_params = dict(self.request.query_params)
  
        next_url = None
        if (int(self.offset) + int(self.limit)) < int(self.total):
            next_params = query_params.copy()
            next_params.update({
                "offset": int(self.offset) + int(self.limit),
                "limit": self.limit
            })
            next_url = f"{base_url}?{urlencode(next_params)}"

        previous_url = None
        if int(self.offset) > 0:
            prev_params = query_params.copy()
            prev_offset = max(0, int(self.offset) - int(self.limit))
            prev_params.update({
                "offset": prev_offset,
                "limit": self.limit
            })
            previous_url = f"{base_url}?{urlencode(prev_params)}"
        
        return {
            "count": self.total,
            "next": next_url,
            "previous": previous_url,
            "results": [item.dict() if isinstance(item, BaseModel) else item for item in self.items]
        }