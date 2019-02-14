from __future__ import print_function
import threading
import random
import time
import sys
if sys.version_info[0] == 3:
    from queue import Queue
else:
    print("MIGHT NOT BE ACCURATE or NOT WORK. Please run it on python3")
    from Queue import Queue
total_queue = []
ROUNDS = -1
threads_queue = []
import argparse

class Process(threading.Thread):
    """
    Class Process:
    Basic process block which simulates the distributed system for the sasaki sorting.
    The pipes are simulated by queues which are threadsafe. All the queues are stored in `total_queue` variable

    Attributes:
        id (int): Thread ID
        round (int): Indicates the round the thread is currently in.
        valuel,valuer (int or None): values present in left and right sides in the process. One of the sides is `None` if the the value is in the extremes
        markedl,markedr (boolean): boolean values indicating the marked
        area (int): flag variable used in sasaki

    Internal components:
        temp (int): Used to store temp values
        sendonce (boolean): Ensures one message is send on a queue
        gotfromr (boolean): Ensures one message received from `right` queue
        gotfroml (boolean): Ensures one message received from `left` queue
        end (int): Indicates extremes of procedure

    Key points:
    - as mentioned in paper, first send happens then receive.
    - A round is said to be completed iff the process receives message from both sides
    - value is only changed when the order is followed and the message sent is in the **same round**
    - the above boolean values ensures proper and smooth flow of message
    """
    quiet = False
    def __init__(self,id,value,end=0):
        """
        Constructor
        - Attributes are asssigned here
        @Params:
            id: int, ID of the thread
            value: int, Initial value given to Thread
            end: int, variable indicating extremes in the distributed computation
        """
        threading.Thread.__init__(self)
        self.id = id
        self.round = 0
        self.valuer = None if end == 1 else value
        self.valuel = None if end == -1 else value
        self.end = end
        self.area = self.end if end!=1 else 0
        self.temp = -1
        self.markedr = False
        self.markedl = False
        if self.end == -1:
            self.markedr = True
        if self.end == 1:
            self.markedl = True
        self.sendonce = True
        self.gotfromr = False
        self.gotfroml = False
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
                displ+="Thread ID: {} values:{} round:{}\n".format(threadobj.id,(threadobj.valuel,threadobj.valuer),threadobj.round)
        sys.stdout.write("%s" % displ)
        sys.stdout.flush()

    def send(self,end=False):
        """
        Send function
        - Sends the messages in the queues
        @Param:
            end (boolean): Tweak used to keep thread running so that idle thread can still send for previous processes
        """
        global total_queue
        if self.valuer!=None and total_queue[self.id]["right"].empty():
            if end:
                total_queue[self.id]["right"].put({"id":self.id,"marked":self.markedr,"value":self.valuer,"round":self.round-1})
            else:
                total_queue[self.id]["right"].put({"id":self.id,"marked":self.markedr,"value":self.valuer,"round":self.round})
        if self.valuel!=None and total_queue[self.id]["left"].empty():
            if end:
                total_queue[self.id]["left"].put({"id":self.id,"marked":self.markedl,"value":self.valuel,"round":self.round-1})
            else:
                total_queue[self.id]["left"].put({"id":self.id,"marked":self.markedl,"value":self.valuel,"round":self.round})
        self.sendonce = False

    def receive(self,end=False):
        """
        Receive function
        - receives the messages in the queues
        @Param:
            end (boolean): Tweak used to keep thread running so that idle thread can still send for previous processes
        returns:
            boolean: indicating if the packet was received
        """
        global total_queue
        pl = None
        pr = None
        if self.valuer != None:
            if end:
                if not total_queue[self.id+1]["left"].empty():
                    pr = total_queue[self.id+1]["left"].get()
                    if pr["round"] < self.round:
                        self.send(True)
                        return False
                    else:
                        return True

            if not total_queue[self.id+1]["left"].empty():
                pr = total_queue[self.id+1]["left"].get()
                total_queue[self.id+1]["left"].task_done()
                if pr["round"] != self.round:
                    pr = None
                else:
                    self.gotfromr = True

        if self.valuel != None :
            if end:
                if not total_queue[self.id-1]["right"].empty():
                    pl = total_queue[self.id-1]["right"].get()
                    total_queue[self.id-1]["right"].task_done()
                    if pl["round"] != self.round:
                        self.send(True)
                        return False
                    else:
                        return True

            if not total_queue[self.id-1]["right"].empty():
                pl = total_queue[self.id-1]["right"].get()
                total_queue[self.id-1]["right"].task_done()
                if pl["round"] != self.round:
                    pl = None
                else:
                    self.gotfroml = True

        self.compute(pr,pl)


    def compute(self,pktr,pktl):
        """
        Compute function
        - local computation for swapping elements
        @Param:
            pktr,pktl (dict or None): Message from receive function
        """
        if pktl != None:
            if self.valuel < pktl["value"]:
                self.valuel = pktl["value"]
                if pktl["marked"]:
                    self.area-=1
                if self.markedl:
                    self.area+=1
                self.markedl = pktl["marked"]
        if pktr != None:
            if self.valuer > pktr["value"]:
                self.valuer = pktr["value"]
                self.markedr = pktr["marked"]


    def run(self):
        """
        Run function
        - main function equivalent in the process
        - here the conditions for rounds are checked. Final loop is for idle message passing
        """
        global ROUNDS,total_queue
        while self.round<ROUNDS-1:
            self.send()
            self.receive()
            if (self.round not in self.doneround) and not Process.quiet:
                if self.round % 5 == 0:
                    Process.print_threads()
                self.doneround.add(self.round)
            if self.gotfroml and self.gotfromr:
                self.sendonce = True
                self.gotfromr = False
                self.gotfroml = False
            elif self.gotfromr and self.valuel == None:
                self.round+=1
                self.sendonce = True
                self.gotfromr = False
            elif self.gotfroml and self.valuer == None:
                self.round+=1
                self.sendonce = True
                self.gotfroml = False
            if self.valuel!= None and  self.valuer!= None and self.sendonce:
                if self.valuel > self.valuer:
                    self.temp = self.valuel
                    self.valuel =self.valuer
                    self.valuer = self.temp
                    self.temp = self.markedl
                    self.markedl = self.markedr
                    self.markedr = self.temp
                self.round+=1
            time.sleep(0.0001)

        k = True
        while k:
            k = self.receive(True)





if __name__ == '__main__':

    # Argument parser
    parser = argparse.ArgumentParser(description="Sasaki sorting algorithm")
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
    end = -1
    original = []
    ROUNDS = n
    for i in range(n):
        if i >0:
            end = 0
        if i == n-1:
            end = 1
        original.append(random.randint(1,100000))
        threads_queue.append(Process(i,original[-1],end))
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
        if thread_obj.area <0:
            output.append(thread_obj.valuer)
        else:
            output.append(thread_obj.valuel)

    print("Original: {}\n".format(original))
    print("Sorted: {}".format(output))

    # Sanity check
    if sorted(original) != output:
        print("ERROR")
