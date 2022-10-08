#import resource as r

#csv_file = '../data/data.csv'

class BackgroundRunner():
    # Make this function to populate db
    def __init__(self, in_file):
        self.count = 1
        self.in_file = in_file

    def post_line(self, line):
        index, label, m1_A, m1_B, m2_A, m2_B, m3_A, m3_B = line.split(,)

    async def run_main(self):
    #def run_main(self):
        #while True:
            #await asyncio.sleep(0.1)
        with open(self.in_file) as file:
            for _ in range(1):
                next(file)
            for line in file:
                print(line)
                self.count += 1
                if self.count > 10:
                    break
                pass

#runner = BackgroundRunner(csv_file)

#runner.run_main()

#print(f'Peak Memory Usage ={r.getrusage(r.RUSAGE_SELF).ru_maxrss}')
#print(f'User Mode Time ={r.getrusage(r.RUSAGE_SELF).ru_utime}')
#print(f'System Memory Usage ={r.getrusage(r.RUSAGE_SELF).ru_stime}')
#
#print(f'Runner count: {runner.count}')
