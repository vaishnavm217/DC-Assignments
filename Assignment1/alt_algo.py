from __future__ import print_function
import threading
import random
import time
import sys
if sys.version_info[0] == 3:
    from queue import Queue
else:
    # print("MIGHT NOT BE ACCURATE or NOT WORK. Please run it on python3")
    from Queue import Queue
total_queue = []
ROUNDS = -1
threads_queue = []
import argparse

class Process(threading.Thread):
    """
    Class Process:
    Basic process block which simulates the distributed system for the n-1 sorting crudly based on paper (https://www.researchgate.net/publication/224145793_An_alternative_time_-_Optimal_distributed_sorting_algorithm_on_a_line_network).
    The pipes are simulated by Queues which are threadsafe. All the queues are stored in `total_queue` variable

    Attributes:
        id (int): Thread ID
        round (int): Indicates the round the thread is currently in.
        value (int): value present in the process.
        flag (int): flag variable used in the algorithm

    Internal components:
        templ,tempr (int): Used to store temp values
        edge (boolean): used to check if flag = 1 value exists in the extremes

    Key points
    - Corners sometimes have no element to swap with, thus get their flag and rounds incremented
    - flag = 1 is considered as center, and the computation is performed there. The message received from that node is blindly applied
    - the above boolean values ensures proper and smooth flow of message
    """
    quiet = False
    def __init__(self,id,value):
        """
        Constructor
        - Attributes are asssigned here
        @Params:
            id: int, ID of the thread
            value: int, Initial value given to Thread
        """
        threading.Thread.__init__(self)
        self.id = id
        self.value = value
        self.templ = -1
        self.tempr = -1
        self.round = 0
        self.sendonce = True
        self.flag = id%3
        self.edge = False
        self.doneround = set()

    @staticmethod
    def print_threads():
        """
        Print function
        - Static function which prints status of 5 intermediate processes
        """
        global threads_queue,ROUNDS
        displ = ""
        temp = ROUNDS/5
        if temp == 0:
            temp = 1
        for threadobj in threads_queue:
            if threadobj.id % temp == 0:
                displ+="Thread ID: {} values:{} round:{} flag:{}\n".format(threadobj.id,(threadobj.value),threadobj.round,threadobj.flag)
        sys.stdout.write("%s" % displ)
        sys.stdout.flush()
        time.sleep(0.1)

    def send(self,valuel=None,valuer=None):
        """
        Send function
        - Sends the messages in the queues
        @Param:
            end (boolean): Tweak used to keep thread running so that idle thread can still send for previous processes
        """
        global total_queue
        if self.id!=ROUNDS-1:
            if self.flag == 0 and total_queue[self.id]["right"].empty():
                    total_queue[self.id]["right"].put({"value":self.value,"round":self.round,"id":self.id,"flag":self.flag})
        if self.id!=0:
            if self.flag == 2 and total_queue[self.id]["left"].empty():
                total_queue[self.id]["left"].put({"value":self.value,"round":self.round,"id":self.id,"flag":self.flag})
        if self.flag == 1:
            if self.id!=0 and valuel!=None:
                total_queue[self.id]["left"].put({"value":valuel,"round":self.round,"id":self.id,"flag":self.flag})
            if self.id!=ROUNDS-1 and valuer!=None:
                total_queue[self.id]["right"].put({"value":valuer,"round":self.round,"id":self.id,"flag":self.flag})
        self.sendonce = False


    def receive(self):
        """
        Receive function
        - receives the messages in the queues
        """
        global total_queue,ROUNDS
        pl = None
        pr = None
        if self.flag == 1:
            self.edge  = False
            while True:
                if self.id!=ROUNDS-1:
                    if not total_queue[self.id+1]["left"].empty():
                        pr = total_queue[self.id+1]["left"].get()
                        total_queue[self.id+1]["left"].task_done()
                        if pr["round"] != self.round:
                            pr = None
                        self.sendonce = True
                        if self.id == 0:
                            self.edge  = True
                if self.id!=0:
                    if not total_queue[self.id-1]["right"].empty():
                        pl = total_queue[self.id-1]["right"].get()
                        total_queue[self.id-1]["right"].task_done()
                        if pl["round"] != self.round:
                            pl = None
                        self.sendonce = True
                        if self.id == ROUNDS-1:
                            self.edge = True
                if self.edge :
                    self.edge = False
                    break
                if pr!=None and pl!=None:
                    break
            self.compute(pr,pl)
        else:
            if self.id!=ROUNDS-1:
                if not total_queue[self.id+1]["left"].empty():
                    pr = total_queue[self.id+1]["left"].get()
                    total_queue[self.id+1]["left"].task_done()
                    if pr["flag"]==1:
                        self.sendonce = True
                        self.value = pr["value"]
            if self.id!=0:
                if not total_queue[self.id-1]["right"].empty():
                    pl = total_queue[self.id-1]["right"].get()
                    total_queue[self.id-1]["right"].task_done()
                    if pl["flag"]==1:
                        self.sendonce = True
                        self.value = pl["value"]
        if self.flag!=1 and self.sendonce:
            self.round+=1
            self.flag = (self.flag+1)%3



    def compute(self,pktr,pktl):
        """
        Compute function
        - local computation for swapping elements
        @Param:
            pktr,pktl (dict or None): Message from receive function
        """
        if self.flag!=1:
            return
        if pktl != None and pktr != None:
            t = sorted([pktl,{"value":self.value},pktr],key=lambda x:x["value"])
            self.templ = t[0]["value"]
            self.tempr = t[2]["value"]
            self.value = t[1]["value"]
            self.send(self.templ,self.tempr)
            self.round+=1
            self.flag = (self.flag+1)%3
        elif pktl != None:
            t = sorted([pktl,{"value":self.value}],key=lambda x:x["value"])
            self.templ = t[0]["value"]
            self.value = t[1]["value"]
            self.send(self.templ,None)
            self.round+=1
            self.flag = (self.flag+1)%3
        elif pktr != None:
            t = sorted([pktr,{"value":self.value}],key=lambda x:x["value"])
            self.tempr = t[1]["value"]
            self.value = t[0]["value"]
            self.send(None,self.tempr)
            self.round+=1
            self.flag = (self.flag+1)%3

    def run(self):
        """
        Run function
        - main function equivalent in the process
        - here the conditions for rounds are checked. Final loop is for idle message passing
        """
        global ROUNDS
        while self.round<ROUNDS-1:
            if self.flag!=1:
                if (self.id==0 and self.flag==2 ) or (self.id==ROUNDS-1 and self.flag==0):
                    self.round+=1
                    self.flag = (self.flag+1)%3
                    self.sendonce = True
                    continue
                self.send()
                self.receive()
            else:
                self.receive()
                self.send()
            if (self.round not in self.doneround) and not Process.quiet:
                if self.round % 5 == 0:
                    Process.print_threads()
                self.doneround.add(self.round)
            time.sleep(0.0001)


if __name__ == '__main__':

    # Argument parser
    parser = argparse.ArgumentParser(description="Alternate n-1 sorting algorithm")
    parser.add_argument("-d","--details",action='store_true',help="Shows detailed description of classes")
    parser.add_argument("-v","--verbose",action='store_false',help="prints the intermediate stages. Can take time to print")
    parser.add_argument("-num",type=int,help="Total number of elements")
    args=parser.parse_args()
    Process.quiet = args.verbose
    if args.details:
        help(Process)
        sys.exit(0)
    if args.num == None:
        n = int(input("Number of Elements\n"))
    else:
        n = args.num

    # Initialisations
    threads_queue = []
    original = []
    ROUNDS = n
    end = -1
    for i in range(n):
        original.append(random.randint(1,100000))
        threads_queue.append(Process(i,original[-1]))
        if i == 0:
            total_queue.append({"right":Queue()})
        elif i == n-1:
            total_queue.append({"left":Queue()})
        else:
            total_queue.append({"left":Queue(),"right":Queue()})
    start = time.time()

    #Process starts
    for thread_obj in threads_queue:
        thread_obj.start()

    # to keep them running until they terminate
    for thread_obj in threads_queue:
        thread_obj.join()

    print("Threads finished")
    print("Time taken:{} sec".format(time.time()-start))
    output = []

    # Printing the final output using area flag
    for thread_obj in threads_queue:
            output.append(thread_obj.value)

    print("Original: {}\n".format(original))
    print("Sorted: {}".format(output))

    # Sanity check
    if sorted(original) != output:
        print("ERROR")
