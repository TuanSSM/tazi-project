from fastapi import APIRouter, HTTPException, Path, Depends
from .config import SessionLocal
from sqlalchemy.orm import Session
from .schemas import ConfusionMatrixSchema,RequestConfusionMatrix,Response
from .crud import *

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/create')
async def create(request: RequestConfusionMatrix, db:Session=Depends(get_db)):
    create_matrix(db,
                       matrix = request.parameter)
    return Response(code=200,
                    status='OK',
                    message='ConfusionMatrix created successfully').dict(exclude_none=True)

@router.get('/')
async def get(db:Session = Depends(get_db)):
    _matrix = get_matrix(db,
                              0,
                              1000)
    return Response(code=200,
                    status='OK',
                    message='Success Fetch all data',
                    result=_matrix).dict(exclude_none=True)

@router.get('/{id}')
async def get_by_id(id:int, db:Session = Depends(get_db)):
    _matrix = get_matrix_by_id(db, id)
    return Response(code=200,
                    status='OK',
                    message=f'Success Fetch matrix: {id}',
                    result=_matrix).dict(exclude_none=True)
