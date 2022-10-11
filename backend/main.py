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
import uvicorn
from collections import Counter
import numpy as np

model.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.DEBUG,
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
        self.done = False

    def parse_prediction(self, csv_line):
        params = csv_line.replace('\n','').split(',')
        id , lbl, *mdls  = params

        if lbl not in ['A','B']:
            raise Exception(f'Label out of scope for CSV entry: {id} with label: ' + lbl)

        mdls = [float(elm) for elm in mdls]

        #for mdl in mdsl:
        #    if mdl

        mdl1_A, mdl1_B, mdl2_A, mdl2_B, mdl3_A, mdl3_B = mdls

        prediction = model.Prediction(label = lbl,
                                      model1_A = mdl1_A,
                                      model1_B = mdl1_B,
                                      model2_A = mdl2_A,
                                      model2_B = mdl2_B,
                                      model3_A = mdl3_A,
                                      model3_B = mdl3_B)
        return prediction

    async def run_main(self, event):
        with open(self.in_file) as file:
            for _ in range(1):
                next(file)
            for line in file:
                await asyncio.sleep(np.random.exponential(0.002))
                data = self.parse_prediction(line)
                await push(data)
                self.count += 1
                logging.debug(f'Data creation successful for index: {self.count}')
                if self.count == 1000: # Change it to 1000
                    event.set()
        logger.debug(f'EOF')
        self.done = True

class ConfusionMatrix():
    def __init__(self):
        self.slider = 0
        self.cm_data = None

    def w_avg(self, values: [float,float,float]) -> float:
        weights = [0.5,0.6,0.7]
        avg = sum([a*b for a,b in zip(values,weights)])/sum(weights)
        return avg

    def predicted_label(self, pr : model.Prediction) -> (str,str):
        pr_a = [pr.model1_A, pr.model2_A, pr.model3_A]

        if pr_a == 0.5:
            raise Exception(f'Predictions are equal!')

        predicted = 'A' if self.w_avg(pr_a) >= 0.5 else 'B'

        return pr.label, predicted

    def counter2matrix(self) -> model.ConfusionMatrix:
        t_A, f_A, t_B, f_B = self.cm_data.values()

        cm = model.ConfusionMatrix(true_A = t_A,
                                   false_A = f_A,
                                   true_B = t_B,
                                   false_B = f_B)
        return cm

    def init_window(self, db:Session):
        window = crud.get_prediction(db, limit=1000) # Change limit to 1000
        db.close()
        initMatrixList = []
        for p in window:
            real, pred = self.predicted_label(p)
            initMatrixList.append((real,pred))
        c = Counter(initMatrixList)
        self.cm_data = c

    def slide_matrix(self, db: Session):
        exclude_pred = crud.get_prediction_by_id(db,self.slider)
        new_pred = crud.get_prediction_by_id(db,self.slider+1000)
        db.close()

        self.cm_data.subtract([self.predicted_label(exclude_pred)])
        self.cm_data.update([self.predicted_label(new_pred)])

    async def run_swindow(self):
        logging.debug('!!!Confusion matrix RUNNER is WORKING!!!')
        while True:
            if self.slider+999 != ds_runner.count: # Change this later
              db = SessionLocal()
              if self.slider == 0: # get rid of this later
                  self.init_window(db)
              else:
                  self.slide_matrix(db)
              cm = self.counter2matrix()
              await push(cm)
              self.slider += 1
              logging.debug(f'Confusion Matrix creation successful for index: {self.slider}')
            if stop_backgroundtask | (ds_runner.done & self.slider+999 == ds_runner.count):
              break

class BackgroundTasks(Thread):
    def run(self, *args, **kwargs):
        event.wait()
        asyncio.run(cm_runner.run_swindow())
        logging.debug('Worker closing down')

event = Event()
ds_runner = GrowingDataSource(csv_file)
cm_runner = ConfusionMatrix()
stop_backgroundtask = False

@app.on_event('startup')
async def app_startup():
    t = BackgroundTasks()
    t.start()
    asyncio.create_task(ds_runner.run_main(event))

@app.on_event("shutdown")
def shutdown_event():
    with open("log.txt", mode="a") as log:
        log.write(f'Application shutdown, with ds_runner at: {ds_runner.count} | slider at: {cm_runner.slider}\n')
    stop_backgroundtask = True
    model.Base.metadata.drop_all(bind=engine)
    print('Database is purged')

@app.get('/')
async def Home():
    return f'Welcome Home, btw ds_runner is at: {ds_runner.count}, slider is at: {cm_runner.slider}'

@app.get('/sliding_window')
async def Window(id:int,size=1000):
    db = SessionLocal()
    window = crud.get_prediction(db,skip=id, limit=size)
    db.close()
    return window

app.include_router(pr.router, prefix='/prediction', tags=['prediction'])
app.include_router(mr.router, prefix='/matrix', tags=['matrix'])

#if __name__ == '__main__':
#    uvicorn.run(app, host='0.0.0.0', port=8000, workers=2)
