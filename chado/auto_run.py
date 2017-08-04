from rectangle_solver import *
from manager import *
from submit_solution import *
from datetime import datetime
import time

def update_problems():
    update_snapshot_data("")
    latest_problems("")

def everyhour_task():
    update_problems()
    rs = RectangleSolver()
    rs.solve_updated_problems()
    submit_updated_solutions()

def timer(last_hour):
    dt = datetime.now()
    day = dt.day
    hour = dt.hour + 24*day
    if last_hour < hour:
        print("go", flush = True)
        everyhour_task()
        return hour
    print("wait", flush = True)
    return last_hour

if __name__ == '__main__':
    last_hour = 188
    print("a", flush=True)
    while True:
        print("b", flush=True)
        try:
            last_hour =timer(last_hour)
        except Exception:
            print("error")
        time.sleep(300)
