from pydantic import BaseModel
from typing import Optional


class UserInput(BaseModel):
    message: str


class ExtractedInfo(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    state: Optional[str] = None
    income: Optional[int] = None


class SchemeMetadata(BaseModel):
    schemeShortTitle: Optional[str] = None
    schemeName: Optional[str] = None
    schemeCategory: Optional[str] = None
    schemeFor: Optional[str] = None
    level: Optional[str] = None
    ministry: Optional[str] = None
    description: Optional[str] = None
    beneficiaryState: Optional[str] = None
    categories: Optional[str] = None
    tags: Optional[str] = None
    states: Optional[str] = None


class SchemeResult(BaseModel):
    id: str
    text: str
    metadata: SchemeMetadata


class ChatResponse(BaseModel):
    status: str
    user_profile: ExtractedInfo
    schemes: list[SchemeResult]
    response: str


class VectorizeResponse(BaseModel):
    status: str
    count: int
