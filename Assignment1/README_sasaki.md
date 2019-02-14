# SASAKI Sorting Algorithm

## Modules Used
- Threading
- Queues

## Installation
0. Ensure you have Python3 installed

## Usage
```bash
$ python3 sasaki.py
Number of Elements
5
Threads finished
Time taken:0.007102251052856445 sec
Original: [62677, 17967, 98478, 80596, 78790]
Sorted: [17967, 62677, 78790, 80596, 98478]


# Directly with number
$ python3 sasaki.py -num 10
Threads finished
Time taken:0.012189865112304688 sec
Original: [64207, 55092, 4596, 20092, 5364, 6917, 29209, 77224, 28823, 34806]
Sorted: [4596, 5364, 6917, 20092, 28823, 29209, 34806, 55092, 64207, 77224]

# with intermediate states
$ python3 sasaki.py -v
Number of Elements
5
Thread ID: 0 values:(None, 65815) round:0
Thread ID: 1 values:(86327, 86327) round:0
.
.
Thread ID: 3 values:(52989, 52989) round:0
Thread ID: 4 values:(65324, None) round:0
Threads finished
Time taken:0.008449316024780273 sec
Original: [65815, 86327, 23977, 52989, 65324]
Sorted: [23977, 52989, 65324, 65815, 86327]

# description of the classes
$ python3 sasaki.py -d
Help on class Process in module __main__:

class Process(threading.Thread)
 |  Class Process:
 |  Basic process block which simulates the distributed system for the sasaki so
rting.
 |  The pipes are simulated by queues which are threadsafe. All the queues are s
tored in `total_queue` variable
 |  
 |  Attributes:
 |      id (int): Thread ID
 |      round (int): Indicates the round the thread is currently in.
 |      valuel,valuer (int or None): values present in left and right sides in t
he process. One of the sides is `None` if the the value is in the extremes
 |      markedl,markedr (boolean): boolean values indicating the marked
 |      area (int): flag variable used in sasaki
 |  
 |  Internal components:
 |      temp (int): Used to store temp values
 |      sendonce (boolean): Ensures one message is send on a queue
 |      gotfromr (boolean): Ensures one message recieved from `right` queue
 |      gotfroml (boolean): Ensures one message recieved from `left` queue
 |      end (int): Indicates extremes of procedure
:
```
