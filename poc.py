# author: sanqiushu
# date: 2021/11/8
import random
import time
from queue import Queue
import requests


def run():
    pass


def poc(target_queue: Queue, result_queue: Queue):
    try:
        while True:
            if target_queue.empty():
                time.sleep(0.1)
            else:
                target = target_queue.get()
                req = requests.get(target)
                a_int = random.randint(5, 10)
                time.sleep(a_int)
                if req.status_code == 200:
                    result_queue.put({"target": target, "is_vuln": "true"})
                else:
                    result_queue.put({"target": target, "is_vuln": "false"})
    except Exception as e:
        print(e)
        result_queue.put({"target": "Error", "is_vuln": "error"})
        pass
