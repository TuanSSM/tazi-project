from fastapi import APIRouter, HTTPException, Path, Depends
from config import SessionLocal
from sqlalchemy.orm import Session
from schemas import PredictionSchema,RequestPrediction,Response
import crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post('/create')
async def create(request: RequestPrediction, db:Session=Depends(get_db)):
    crud.create_prediction(db,
                           prediction = request.parameter)
    return Response(code=200,
                    status='OK',
                    message='Prediction created successfully').dict(exclude_none=True)

@router.get('/')
async def get(db:Session = Depends(get_db)):
    _prediction = crud.get_prediction(db,
                                      1,
                                      1000)
    return Response(code=200,
                    status='OK',
                    message='Success Fetch all data',
                    result=_prediction).dict(exclude_none=True)

@router.get('/{id}')
async def get_by_id(id:int, db:Session = Depends(get_db)):
    _prediction = crud.get_prediction_by_id(db, id)
    return Response(code=200,
                    status='OK',
                    message=f'Success Fetch prediction: {id}',
                    result=_prediction).dict(exclude_none=True)
