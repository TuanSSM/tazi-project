from sqlalchemy import Column, Integer, Float, String
from .config import Base

class Prediction(Base):
    __tablename__ = 'prediction'

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String)
    model1_A = Column(Float)
    model1_B = Column(Float)
    model2_A = Column(Float)
    model2_B = Column(Float)
    model3_A = Column(Float)
    model3_B = Column(Float)

class ConfusionMatrix(Base):
    __tablename__ = 'confusion_matrix'

    id = Column(Integer, primary_key=True, index=True)
    true_A = Column(Integer)
    false_A = Column(Integer)
    true_B = Column(Integer)
    false_B = Column(Integer)
