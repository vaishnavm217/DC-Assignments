import threading
import random
import time
total_queue = []
ROUNDS = -1
class Process(threading.Thread):
    def __init__(self,id,value,end=0):
        threading.Thread.__init__(self)
        self.id = id
        self.round = 0
        self.valuer = value
        self.valuel = value
        self.LS = []
        self.end = end
        self.area = 0
        self.temp = -1

    def send(self):
        global total_queue
        if self.valuer < self.valuel:
            self.temp = self.valuel
            self.valuel = self.valuer
            self.valuer = self.temp
        if not self.end == 1:
            total_queue[self.id]["right"].append({"id":self.id,"value":self.valuer})
        if not self.end == -1:
            total_queue[self.id]["left"].append({"id":self.id,"value":self.valuel})

    def receive(self):
        global total_queue
        if not self.end == 1:
            if len(total_queue[self.id+1]["left"]):
                curr = total_queue[self.id+1]["left"].pop()
                if curr["value"] < self.valuer:
                    self.LS.append({"prevr":self.valuer,"new":curr["value"],"from_id":self.id+1,})
                    if self.end:
                        self.area += 1
                        if self.area<0:
                            self.area = -1
                        if self.area>0:
                            self.area = 1
                    self.valuer = curr["value"]

        if not self.end == -1:
            if len(total_queue[self.id-1]["right"]):
                curr = total_queue[self.id-1]["right"].pop()
                if self.valuel < curr["value"]:
                    self.LS.append({"prevl":self.valuel,"new":curr["value"],"from_id":self.id-1})
                    if self.end:
                        self.area-=1
                        if self.area<0:
                            self.area = -1
                        if self.area>0:
                            self.area = 1
                    self.valuel = curr["value"]
        if self.valuer < self.valuel:
            self.temp = self.valuel
            self.valuel = self.valuer
            self.valuer = self.temp
    def run(self):
        global ROUNDS
        while self.round<ROUNDS-1:
            self.receive()
            self.send()
            time.sleep(0.01)
            self.round+=1


if __name__ == '__main__':
    n = int(input("Number of Elements\n"))
    threads_queue = []
    end = -1
    original = []
    ROUNDS = n
    for i in range(n):
        if i >0:
            end = 0
        if i == n-1:
            end = 1
        original.append(random.randint(0,10000))
        threads_queue.append(Process(i,original[-1],end))
        total_queue.append({"left":[],"right":[]})
    print("Original array:",original)
    for thread_obj in threads_queue:
        thread_obj.start()

    for thread_obj in threads_queue:
        thread_obj.join()

    print("Threads finished")
    for thread_obj in threads_queue:
        # print(thread_obj.LS)
        if thread_obj.area ==-1:
            print(thread_obj.valuer)
        else:
            print(thread_obj.valuel)
