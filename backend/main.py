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
        self.count = 1
        self.in_file = in_file

    def parse_prediction(self, csv_line):
        params = csv_line.split(',')
        id, lbl, mdl1_A, mdl1_B, mdl2_A, mdl2_B, mdl3_A, mdl3_B = params

        prediction = model.Prediction(label = lbl,
                                model1_A = float(mdl1_A),
                                model1_B = float(mdl1_B),
                                model2_A = float(mdl2_A),
                                model2_B = float(mdl2_B),
                                model3_A = float(mdl3_A),
                                model3_B = float(mdl3_B[:-2]))
        return prediction

    async def create_prediction(self, data):
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
                await asyncio.sleep(0.02)
                data = self.parse_prediction(line)
                await self.create_prediction(data)
                logging.debug(str(data))
                logging.debug(f'Data creation successful for index: {self.count}')
                if self.count == 50:
                    event.set()
                    logging.debug('Event is set'*10)
                self.count += 1

class ConfusionMatrix():
    def __init__(self):
        self.count = 1

    def predicted_label(self, prediction):
        pass

    async def create_matrix(self, predictions):
        pass

    async def run_matrices(self):#, event):
        print('Background task started')
        for _ in range(50):
            await asyncio.sleep(0.02)
            logging.debug('!!!Confusion MATRIX RUNNER IS WORKING!!!')

class BackgroundTasks(Thread):
    def run(sef, *args, **kwargs):
        event.wait()
        asyncio.run(cm_runner.run_matrices())
        logging.debug('Worker closing down')

event = Event()
ds_runner = GrowingDataSource(csv_file)
cm_runner = ConfusionMatrix()

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
