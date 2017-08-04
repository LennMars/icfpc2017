import os.path
import os
import sys
sys.path.append(os.getcwd()+"/API")
from request_sender import *
import traceback

def submit_updated_solutions():
    answer_path = "answer"
    lst_answers = []

    for item in os.listdir(answer_path):
        item = str(item)
        if item.find("."):
            id, ext = os.path.splitext(item)
            if ext == ".rectangle3":
                print(str(id))
                lst_answers.append(int(id))
        else:
            continue

    log_submit_solution = open("log_submit_solution.txt", "r+")
    log_submit_backup = open("log_submit_backup.txt", "w")
    lst_log = []
    for line in log_submit_solution:
        lst_log.append(line.rstrip().split(","))
    print(lst_log)
    #lst_log = lst_log[:-1]
    lst_log = [[int(item[0]), float(item[1])] for item in lst_log]
    lst_log_id = [item[0] for item in lst_log]

    lst_answers.sort()
    lst_submit = [id for id in lst_answers if id not in lst_log_id]
    print("answer", len(lst_answers))
    print("log", len(lst_log))
    print("submit", len(lst_submit))
    log_submit_solution.seek(0)
    log_submit_backup.seek(0)
    for item in lst_log:
        msg = str(item[0]) + "," + str(item[1]) + "\n"
        log_submit_solution.write(msg)
        log_submit_backup.write(msg)

    r_sender = RequestSender()

    print(lst_submit)
    for id in lst_submit:
        print(id)

        try:
            solution_path = answer_path+"/"+str(id)+".rectangle3"
            solution_resp = r_sender.solution_submission(probrem_id=str(id), solution_spec=solution_path)
            if (solution_resp.status_code == 200):
                solution = solution_resp.json()
                print(solution)
                resemblance = solution['resemblance']
                msg = str(id) + "," + str(resemblance)+"\n"
                print(msg)
                log_submit_solution.write(msg)
                log_submit_backup.write(msg)
            time.sleep(1)
            print("===")
        except Exception as e:
            traceback.print_exc()
            continue
    log_submit_solution.truncate()
    log_submit_solution.close()
    log_submit_backup.close()
