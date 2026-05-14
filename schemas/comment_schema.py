from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CommentCreate(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    replies: List["CommentResponse"] = []

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

    @classmethod
    def model_validate(cls, obj, **kwargs):
        data = {
            "id": obj.id,
            "content": obj.content,
            "post_id": obj.post_id,
            "user_id": obj.user_id,
            "parent_id": obj.parent_id,
            "created_at": obj.created_at,
            "replies": [cls.model_validate(r) for r in obj.replies] if obj.replies else []
        }
        return cls(**data)

CommentResponse.model_rebuild()