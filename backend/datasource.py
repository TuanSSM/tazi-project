from config import SessionLocal,logconf
import asyncio
import numpy as np
import logging
from model import Prediction

class GrowingDataSource():
    def __init__(self, in_file):
        self.count = 0
        self.in_file = in_file

    def parse_prediction(self, csv_line) -> Prediction:
        params = csv_line.replace('\n','').split(',')
        id , lbl, *mdls  = params

        mdls = [float(elm) for elm in mdls]

        mdl1_A, mdl1_B, mdl2_A, mdl2_B, mdl3_A, mdl3_B = mdls

        prediction = Prediction(label = lbl,
                                model1_A = mdl1_A,
                                model1_B = mdl1_B,
                                model2_A = mdl2_A,
                                model2_B = mdl2_B,
                                model3_A = mdl3_A,
                                model3_B = mdl3_B)
        return prediction

    async def push(self, data):
        db = SessionLocal()
        db.add(data)
        db.commit()
        db.refresh(data)
        db.close()

    async def run_main(self):
        with open(self.in_file) as file:
            for _ in range(1):
                next(file)
            for line in file:
                await asyncio.sleep(np.random.exponential(0.002))
                data = self.parse_prediction(line)
                await self.push(data)
                self.count += 1
                logging.debug(f'Data creation successful for index: {self.count}')
        logger.debug(f'EOF the Data Source')
