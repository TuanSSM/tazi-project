from sqlalchemy.orm import Session
from .model import Prediction, ConfusionMatrix
from .schemas import PredictionSchema, ConfusionMatrixSchema

def get_prediction(db:Session,skip:int=1,limit:int=10000):
    return db.query(Prediction).offset(skip-1).limit(limit).all()

def get_prediction_by_id(db:Session,prediction_id: int):
    return db.query(Prediction).filter(Prediction.id == prediction_id).first()

def get_prediction_count(db:Session):
    return db.query(Prediction).count()

def create_prediction(db:Session, prediction: PredictionSchema):
    _prediction = Prediction(label = prediction.label,
                             model1_A = prediction.model1_A,
                             model1_B = prediction.model1_B,
                             model2_A = prediction.model2_A,
                             model2_B = prediction.model2_B,
                             model3_A = prediction.model3_A,
                             model3_B = prediction.model3_B)
    db.add(_prediction)
    db.commit()
    db.refresh(_prediction)
    return _prediction

def get_matrix(db:Session,skip:int=0,limit:int=100):
    return db.query(ConfusionMatrix).offset(skip).limit(limit).all()

def get_matrix_by_id(db:Session,matrix_id: int):
    return db.query(ConfusionMatrix).filter(ConfusionMatrix.id == matrix_id).first()

def create_matrix(db:Session, matrix: ConfusionMatrixSchema):
    _matrix = Prediction(true_A = matrix.true_A,
                         false_A = matrix.false_A,
                         true_B = matrix.true_B,
                         false_B = matrix.false_B)
    db.add(_matrix)
    db.commit()
    db.refresh(_matrix)
    return _matrix
