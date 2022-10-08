from fastapi import FastAPI, BackgroundTasks
import model
from config import engine
import router
import asyncio

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

class BackgroundRunner:
    # Make this function to populate db
    def __init__(self):
        self.value = 0

    async def run_main(self):
        while True:
            await asyncio.sleep(0.1)
            self.value += 1

runner = BackgroundRunner()

@app.on_event('startup')
async def app_startup():
    asyncio.create_task(runner.run_main())

@app.on_event("shutdown")
def shutdown_event():
    with open("log.txt", mode="a") as log:
        # Purge database
        log.write(f'Application shutdown, with runner at: {runner.value}\n')

#def populate_db(message):
#    print('Populating db: ', message)

@app.get('/')
async def Home(background_tasks: BackgroundTasks):
    #background_tasks.add_task(populate_db, message="Test")
    return f'Welcome Home, btw runner is: {runner.value}'

app.include_router(router.router, prefix='/prediction', tags=['prediction'])

