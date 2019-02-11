import threading
import random
import time
from queue import Queue
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
        self.send_once = True
        self.timer = 0
        self.interval = random.randint(1,10)

    def send(self):
        self.timer+=self.interval
        global total_queue,ROUNDS
        if self.id != ROUNDS-1 and self.send_once:
            # print("sent RIGHT! THREAD: {} : {}".format(self.id,{"id":self.id,"value":self.valuer,"timer":self.timer}))
            total_queue[self.id]["right"].put({"id":self.id,"value":self.valuer,"timer":self.timer})
        if self.id != 0 and self.send_once :
            # print("sent LEFT! THREAD: {} : {} ".format(self.id,{"id":self.id,"value":self.valuel,"timer":self.timer}))
            total_queue[self.id]["left"].put({"id":self.id,"value":self.valuel,"timer":self.timer})
        self.send_once = False

    def compute(self):
        global total_queue
        self.timer+=self.interval
        if self.id != ROUNDS-1:
            # print("THREAD: {} ".format(self.id))
            if not total_queue[self.id+1]["left"].empty():
                self.temp = self.valuer
                curr = total_queue[self.id+1]["left"].get()
                # print("THREAD: {} checking {}. Current value {} and recieved {}".format(self.id,self.id+1,self.temp,curr))
                total_queue[self.id+1]["left"].task_done()
                if curr["value"] < self.valuer:
                    self.valuer = curr["value"]
                    # print("THREAD: {} checking {}. Current value {} and recieved {}".format(self.id,self.id+1,self.temp,curr))
                    if curr["timer"] > self.timer:
                        self.timer = curr["timer"]+1
                    self.LS.append((curr,{"prevr":self.valuer,"new":curr["value"],"from_id":self.id+1,"self_id":self.id,"timer":self.timer}))
                    if self.end:
                        self.area += 1
                        # if self.area<0:
                        #     self.area = -1
                        # if self.area>0:
                        #     self.area = 1
                self.send_once = True
                # self.round+=1self.round+=1

        if self.id  != 0:
            # print("THREAD: {} checking {}".format(self.id,self.id-1))
            if not total_queue[self.id-1]["right"].empty():
                self.temp = self.valuel
                curr = total_queue[self.id-1]["right"].get()
                # print("THREAD: {} checking {}. Current value {} and recieved {}".format(self.id,self.id-1,self.temp,curr))
                total_queue[self.id-1]["right"].task_done()
                if self.valuel < curr["value"]:
                    self.valuel = curr["value"]
                    # print("THREAD: {} checking {}. Current value {} and recieved {}".format(self.id,self.id-1,self.temp,curr))
                    if curr["timer"] > self.timer:
                        self.timer = curr["timer"]+1
                    self.LS.append((curr,{"prevl":self.valuel,"new":curr["value"],"from_id":self.id-1,"timer":self.timer}))
                    if self.end:
                        self.area-=1
                        # if self.area<0:
                        #     self.area = -1
                        # if self.area>0:
                        #     self.area = 1
                self.send_once = True
                # self.round+=1
        if self.valuer < self.valuel:
            self.temp = self.valuel
            self.valuel = self.valuer
            self.valuer = self.temp
            # self.round+=1

    def receive(self):
        global total_queue
        self.timer+=self.interval
        self.compute()

    def run(self):
        global ROUNDS,total_queue
        # self.send()
        while self.round<=ROUNDS-1:
            time.sleep(0.001)
            self.receive()
            self.send()
            # if self.round % 5:
            #     print("Thread: {} - L:{} R:{} Timer:{}".format(self.id,self.valuel,self.valuer,self.timer))
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
        # h = int(input("input NO: {} ".format(i)))
        original.append(random.randint(1,10000))
        threads_queue.append(Process(i,original[-1],end))
        total_queue.append({"left": Queue(),"right":Queue()})
    # print("Original array:",original)
    for thread_obj in threads_queue:
        thread_obj.start()

    for thread_obj in threads_queue:
        thread_obj.join()

    print("Threads finished")
    output = []
    for thread_obj in threads_queue:
        if thread_obj.area <0:
            output.append(thread_obj.valuer)
        else:
            output.append(thread_obj.valuel)
    print("Original: {}".format(original))
    print("Sorted: {}".format(output))
    if set(output) != set(original):
        print("ERROR")
