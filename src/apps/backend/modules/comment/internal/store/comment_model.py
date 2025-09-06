from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class CommentModel(BaseModel):
    task_id: str
    account_id: str
    content: str
    active: bool = True
    created_at: Optional[datetime] = datetime.now()
    id: Optional[ObjectId | str] = None
    updated_at: Optional[datetime] = datetime.now()

    @classmethod
    def get_collection_name(cls) -> str:
        return "comments"

    @classmethod
    def from_bson(cls, bson_data: dict) -> "CommentModel":
        return cls(
            task_id=bson_data.get("task_id", ""),
            account_id=bson_data.get("account_id", ""),
            content=bson_data.get("content", ""),
            active=bson_data.get("active", True),
            created_at=bson_data.get("created_at"),
            updated_at=bson_data.get("updated_at"),
            id=bson_data.get("_id"),
        )

    def get_create_model_params(self) -> dict:
        return {
            "task_id": self.task_id,
            "account_id": self.account_id,
            "content": self.content,
            "active": self.active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def get_update_model_params(self) -> dict:
        return {"content": self.content, "updated_at": datetime.now()}
