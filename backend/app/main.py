from fastapi import FastAPI
from .model import Prediction, ConfusionMatrix
from .config import SessionLocal, engine, Base
from .prediction_router import router as pr #prediction router
from .prediction_router import push
from .matrix_router import router as mr #matrix router
import asyncio
from .crud import *
from .schemas import RequestPrediction
from sqlalchemy.orm import Session
from threading import Thread
from collections import Counter
from .datasource import GrowingDataSource

Base.metadata.create_all(bind=engine)

app = FastAPI()

csv_file = 'data.csv'


class ConfusionMatrixRunner():
    def __init__(self):
        self.p_count = 0
        self.iterator = 1
        self.window = []
        self.cm = None

    def w_avg(self, values: [float,float,float]) -> float:
        weights = [0.5,0.6,0.7]
        avg = sum([a*b for a,b in zip(values,weights)])/sum(weights)
        return avg

    def predicted_label(self, pr : Prediction) -> (str,str):
        pr_a = [pr.model1_A, pr.model2_A, pr.model3_A]

        predicted = 'A' if self.w_avg(pr_a) >= 0.5 else 'B'
        res = pr.label + predicted

        return res

    def window2matrix(self) -> ConfusionMatrix:
        results = Counter(self.window)

        cm = ConfusionMatrix(true_A = results['AA'],
                             false_A = results['BA'],
                             true_B = results['BB'],
                             false_B = results['AB'])

        self.cm = cm

    async def init_window(self):
        while self.iterator < 1001:
            await self.updatePredictionCount()
            if self.p_count > self.iterator:
              db = SessionLocal()
              raw = get_prediction_by_id(db, prediction_id=self.iterator)
              db.close()
              self.window.append(self.predicted_label(raw))
              self.iterator += 1
        self.window2matrix()

    async def slide_matrix(self):
        exclude_pred = self.window.pop(0)
        db = SessionLocal()

        new = get_prediction_by_id(db,prediction_id=self.iterator)
        new_res = self.predicted_label(new)
        db.close()
        self.window.append(new_res)
        self.window2matrix()

        self.iterator += 1

    async def updatePredictionCount(self):
        db = SessionLocal()
        self.p_count = get_prediction_count(db)
        db.close()

    async def run_swindow(self):
        while True:
            await self.updatePredictionCount()
            if self.p_count >= self.iterator:
                if self.cm is None:
                  await self.init_window()
                else:
                  await self.slide_matrix()
                await push(self.cm)
            if stop_task:
                break

class BackgroundTasks(Thread):
    def run(self, *args, **kwargs):
        asyncio.run(cm_runner.run_swindow())

ds_runner = GrowingDataSource(csv_file)
cm_runner = ConfusionMatrixRunner()
stop_task = False

@app.on_event('startup')
async def app_startup():
    t = BackgroundTasks()
    t.start()
    asyncio.create_task(ds_runner.run_main())

@app.on_event("shutdown")
def shutdown_event():
    with open("logs/log.txt", mode="a") as log:
        log.write(f'Application shutdown, with ds_runner at: {ds_runner.count} | slider at: {cm_runner.iterator}\n')
    stop_task = True
    Base.metadata.drop_all(bind=engine)
    print('Database is purged')

@app.get('/')
async def Home():
    return f'Welcome Home, btw ds_runner is at: {ds_runner.count}, slider is at: {cm_runner.iterator}'

@app.get('/sliding_window')
async def Window(id:int,size=1000):
    db = SessionLocal()
    window = get_prediction(db,skip=id, limit=size)
    db.close()
    return window

@app.get('/predict')
async def Calculate(id:int):
    db = SessionLocal()
    pred = get_prediction_by_id(db,id)
    db.close()
    result = cm_runner.predicted_label(pred)
    return result

app.include_router(pr, prefix='/prediction', tags=['prediction'])
app.include_router(mr, prefix='/matrix', tags=['matrix'])
