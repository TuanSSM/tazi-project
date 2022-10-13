from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class PredictionSchema(BaseModel):
    id: Optional[int] = None
    label: Optional[str] = None
    model1_A: Optional[float] = None
    model1_B: Optional[float] = None
    model2_A: Optional[float] = None
    model2_B: Optional[float] = None
    model3_A: Optional[float] = None
    model3_B: Optional[float] = None

    class Config:
        orm_mode = True

class RequestPrediction(BaseModel):
    parameter: PredictionSchema = Field(...)

class Response(GenericModel, Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]

class ConfusionMatrixSchema(BaseModel):

    id: Optional[int] = None
    true_A: Optional[int] = None
    false_A: Optional[int] = None
    true_B: Optional[int] = None
    false_B: Optional[int] = None

    class Config:
        orm_mode = True

class RequestConfusionMatrix(BaseModel):
    parameter: ConfusionMatrixSchema = Field(...)
