import subprocess
import os
import threading
import queue

lock = threading.Lock()

with open("hosts.txt", "r") as hosts:
    IPS = [x.rstrip("\n") for x in hosts]

results = open("results.txt", "w")


def check(n):
    with open(os.devnull, "wb") as limbo:
        ip = n
        result = subprocess.Popen(["ping", "-n", "2", "-w", "300", ip], stdout=limbo, stderr=limbo).wait()
        with lock:
            if not result:
                results.write(f"{ip}, active\n")
            else:
                results.write(f"{ip}, Inactive\n")


def threader():
    while True:
        workers = q.get()
        check(workers)
        q.task_done()


q = queue.Queue()


for x in range(255):
    t = threading.Thread(target=threader)
    t.daemon = True
    t.start()

for worker in IPS:
    q.put(worker)

q.join()

results.close()
