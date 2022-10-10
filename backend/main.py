from fastapi import FastAPI
import model
from config import SessionLocal, engine
import router
import asyncio
import crud
from schemas import RequestPrediction
from sqlalchemy.orm import Session
from threading import Thread, Event
import logging
import uvicorn

model.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)

app = FastAPI()

csv_file = '../data/data.csv'

class GrowingDataSource():
    def __init__(self, in_file):
        self.count = 0
        self.in_file = in_file

    def parse_prediction(self, csv_line):
        params = csv_line.replace('\n','').split(',')
        _ , lbl, *mdls  = params

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

    async def commit_prediction(self, data):
        db = SessionLocal()
        db.add(data)
        db.commit()
        db.refresh(data)
        db.close()

    async def run_main(self, event):
        with open(self.in_file) as file:
            for _ in range(1):
                next(file)
            for line in file:
                await asyncio.sleep(0.002)
                data = self.parse_prediction(line)
                await self.commit_prediction(data)
                self.count += 1
                logging.debug(str(data))
                logging.debug(f'Data creation successful for index: {self.count}')
                if self.count == 10: # Change it to 1000
                    event.set()

class ConfusionMatrix():
    def __init__(self):
        self.count = 1
        self.matrix_tmp = { 'id' : 0,
                            'true_A' : 0,
                            'false_A' : 0,
                            'true_B' : 0,
                            'false_B' : 0 }

    def w_avg(self, values: [float,float,float]) -> float:
        weights = [0.5,0.6,0.7]
        avg = sum([a*b for a,b in zip(values,weights)])/sum(weights)
        return avg

    def predicted_label(self, pr : model.Prediction):
        pr_a = [pr.model1_A, pr.model2_A, pr.model3_A]
        pr_b = [pr.model1_B, pr.model2_B, pr.model3_B]
        predicted = 'A' if self.w_avg(pr_a) > self.w_avg(pr_b) else 'B'
        return pr.label, predicted

    def create_matrix(self, predictions : [model.Prediction]) -> model.ConfusionMatrix:
        for prediction in predictions:
            pass

    def slide_matrix(self, pr : model.Prediction):
        label, predicted = self.predicted_label(pr)

    async def post_matrix(self, predictions : model.ConfusionMatrix) -> None:
        pass

    async def init_matrix(self):

    async def run_swindow(self):#, event):
        logging.debug('!!!Confusion matrix RUNNER is WORKING!!!')
        for i in range(50): #Change this later
            await asyncio.sleep(0.02)
            db = SessionLocal()
            if self.matrix_tmp['id'] == 0: # get rid of this later
                window = crud.get_prediction(db,skip=i+1, limit=10) # Change limit to 1000
                db.close()
                initMatrixList = []
                for p in window:
                    real, pred = self.predicted_label(p)
                    logging.debug('Real: ' + real + ' | Predicted: ' + pred)
                    initMatrixList.append((real,pred))
                    # Create first matrix
                    # Remove first item from matrix and store it in self.matrixtmp
            else:
                window = crud.get_prediction_by_id(db,self.matrix_tmp['id']+1000)
                # Do relative calc for sliding window
                pass

class BackgroundTasks(Thread):
    def run(self, *args, **kwargs):
        event.wait()
        cm_runner = ConfusionMatrix()
        asyncio.run(cm_runner.run_swindow())
        logging.debug('Worker closing down')

event = Event()
ds_runner = GrowingDataSource(csv_file)

@app.on_event('startup')
async def app_startup():
    t = BackgroundTasks()
    #t2 = BackgroundTasks()
    t.start()
    #t2.start()
    asyncio.create_task(ds_runner.run_main(event))

@app.on_event("shutdown")
def shutdown_event():
    with open("log.txt", mode="a") as log:
        log.write(f'Application shutdown, with ds_runner at: {ds_runner.count}\n')
    model.Base.metadata.drop_all(bind=engine)
    print('Database is purged')

@app.get('/')
async def Home():
    return f'Welcome Home, btw ds_runner is at: {ds_runner.count}'

@app.get('/sliding_window')
async def Window(id:int,size=1000):
    db = SessionLocal()
    window = crud.get_prediction(db,skip=id, limit=size)
    db.close()
    return window

app.include_router(router.router, prefix='/prediction', tags=['prediction'])

#if __name__ == '__main__':
#    uvicorn.run(app, host='0.0.0.0', port=8000, workers=2)
