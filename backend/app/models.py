from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class TrackIssue(BaseModel):
    issue_id: int
    label: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[datetime] = None


class Work(BaseModel):
    issue:TrackIssue

class user_model(BaseModel):
    id:int
    username: str
    name: str
    email: str
    avatar_url: str 
    id: int
    work: List[Work]

class issue_model(BaseModel):
    id:int
    title:str
    assignee_id:int | None
    author_id:int
    created_at:datetime
    updated_at:datetime
    project_id:int
    description:str | None
    milestone_id: int | None
    due_date: datetime| None
    url : str
    state: str




class project_model(BaseModel):
    id:int
    name:str
    description:str | None
    web_url:str
    homepage:str

class demo(BaseModel):
    id:int
    title:str|None = None

