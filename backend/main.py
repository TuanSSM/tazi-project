from fastapi import FastAPI
import model
from config import SessionLocal, engine
import router.prediction as pr #prediction router
import router.matrix as mr #matrix router
import asyncio
import crud
from schemas import RequestPrediction
from sqlalchemy.orm import Session
from threading import Thread, Event
import logging
from collections import Counter
import asyncio
import numpy as np
import logging

model.Base.metadata.create_all(bind=engine)

logconf = logging.basicConfig(level=logging.INFO,
                              format='(%(threadName)-9s) %(message)s',)

app = FastAPI()

csv_file = '../data/data.csv'

async def push(data):
    db = SessionLocal()
    db.add(data)
    db.commit()
    db.refresh(data)
    db.close()

class GrowingDataSource():
    def __init__(self, in_file):
        self.count = 0
        self.in_file = in_file

    def parse_prediction(self, csv_line) -> model.Prediction:
        params = csv_line.replace('\n','').split(',')
        id , lbl, *mdls  = params

        mdls = [float(elm) for elm in mdls]

        mdl1_A, mdl1_B, mdl2_A, mdl2_B, mdl3_A, mdl3_B = mdls

        prediction = model.Prediction(label = lbl,
                                model1_A = mdl1_A,
                                model1_B = mdl1_B,
                                model2_A = mdl2_A,
                                model2_B = mdl2_B,
                                model3_A = mdl3_A,
                                model3_B = mdl3_B)
        return prediction

    async def run_main(self):
        with open(self.in_file) as file:
            for _ in range(1):
                next(file)
            for line in file:
                await asyncio.sleep(np.random.exponential(0.002))
                data = self.parse_prediction(line)
                await push(data)
                self.count += 1
                logging.debug(f'Data creation successful for index: {self.count}')
        logger.debug(f'EOF the Data Source')

class ConfusionMatrix():
    def __init__(self):
        self.p_count = 0
        self.iterator = 1
        self.window = []
        self.cm = None

    def w_avg(self, values: [float,float,float]) -> float:
        weights = [0.5,0.6,0.7]
        avg = sum([a*b for a,b in zip(values,weights)])/sum(weights)
        return avg

    def predicted_label(self, pr : model.Prediction) -> (str,str):
        pr_a = [pr.model1_A, pr.model2_A, pr.model3_A]

        if pr_a == 0.5:
            logging.log(f'Predictions are equal for item: pr.id')

        predicted = 'A' if self.w_avg(pr_a) >= 0.5 else 'B'
        res = pr.label + predicted

        return res

    def window2matrix(self) -> model.ConfusionMatrix:
        results = Counter(self.window)

        cm = model.ConfusionMatrix(true_A = results['AA'],
                                   false_A = results['BA'],
                                   true_B = results['BB'],
                                   false_B = results['AB'])

        self.cm = cm

    async def init_window(self):
        while self.iterator < 1001:
            await self.updatePredictionCount()
            if self.p_count > self.iterator:
              db = SessionLocal()
              raw = crud.get_prediction_by_id(db, prediction_id=self.iterator)
              db.close()
              self.window.append(self.predicted_label(raw))
              logging.debug(f'Sliding Window Iterator: {self.iterator}')
              self.iterator += 1
        self.window2matrix()

    async def slide_matrix(self):
        exclude_pred = self.window.pop(0)
        db = SessionLocal()
        logging.debug(f'Getting item: {self.iterator}')

        new = crud.get_prediction_by_id(db,prediction_id=self.iterator)
        new_res = self.predicted_label(new)
        db.close()
        self.window.append(new_res)
        self.window2matrix()

        self.iterator += 1

    async def updatePredictionCount(self):
        db = SessionLocal()
        self.p_count = crud.get_prediction_count(db)
        db.close()

    async def run_swindow(self):#, event):
        while True:
            await self.updatePredictionCount()
            if self.p_count >= self.iterator:
                if self.cm is None:
                  await self.init_window()
                else:
                  await self.slide_matrix()
                await push(self.cm)
                logging.debug(f'Confusion Matrix creation successful for index: {self.iterator}')
            if stop_task:
                break

class BackgroundTasks(Thread):
    def run(self, *args, **kwargs):
        asyncio.run(cm_runner.run_swindow())#event))
        logging.debug('Worker closing down')

#event = Event()
ds_runner = GrowingDataSource(csv_file)
cm_runner = ConfusionMatrix()
stop_task = False

@app.on_event('startup')
async def app_startup():
    t = BackgroundTasks()
    t.start()
    asyncio.create_task(ds_runner.run_main())#event))

@app.on_event("shutdown")
def shutdown_event():
    with open("logs/log.txt", mode="a") as log:
        log.write(f'Application shutdown, with ds_runner at: {ds_runner.count} | slider at: {cm_runner.iterator}\n')
    stop_task = True
    model.Base.metadata.drop_all(bind=engine)
    print('Database is purged')

@app.get('/')
async def Home():
    return f'Welcome Home, btw ds_runner is at: {ds_runner.count}, slider is at: {cm_runner.iterator}'

@app.get('/sliding_window')
async def Window(id:int,size=1000):
    db = SessionLocal()
    window = crud.get_prediction(db,skip=id, limit=size)
    db.close()
    return window

@app.get('/predict')
async def Calculate(id:int):
    db = SessionLocal()
    pred = crud.get_prediction_by_id(db,id)
    db.close()
    result = cm_runner.predicted_label(pred)
    return result

app.include_router(pr.router, prefix='/prediction', tags=['prediction'])
app.include_router(mr.router, prefix='/matrix', tags=['matrix'])
