from fastapi import FastAPI, BackgroundTasks, Depends
import model
from config import SessionLocal, engine
import router
import asyncio
import crud
from schemas import RequestPrediction
from sqlalchemy.orm import Session

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

csv_file = '../data/data.csv'

# Populates DB
class BackgroundRunner():
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

    async def create_prediction(self, data, db):
        db.add(data)
        db.commit()
        db.refresh(data)
        db.close()

    async def run_main(self):
        with open(self.in_file) as file:
            for _ in range(1):
                next(file)
            for line in file:
                await asyncio.sleep(0.002)
                db = SessionLocal()
                data = self.parse_prediction(line)
                await self.create_prediction(data, db)
                print(data)
                print(f'Data creation successful for index: {self.count}')
                self.count += 1

runner = BackgroundRunner(csv_file)

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(runner.run_main())

@app.on_event("shutdown")
def shutdown_event():
    with open("log.txt", mode="a") as log:
        log.write(f'Application shutdown, with runner at: {runner.count}\n')
    model.Base.metadata.drop_all(bind=engine)
    print('Database is purged')

@app.get('/')
async def Home(background_tasks: BackgroundTasks):
    #background_tasks.add_task(populate_db, message="Test")
    #asyncio.create_task(runner.run_main())
    return f'Welcome Home, btw runner is at: {runner.count}'

app.include_router(router.router, prefix='/prediction', tags=['prediction'])
