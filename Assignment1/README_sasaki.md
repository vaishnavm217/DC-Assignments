<!-- Readme is written in Markdown. Please refer to PDF folder for rendered ones -->
# Sasaki Sorting Algorithm

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

# Help
$ python3 sasaki.py -h
usage: sasaki.py [-h] [-d] [-v] [-num NUM]

Sasaki sorting algorithm

optional arguments:
  -h, --help     show this help message and exit
  -d, --details  Shows detailed description of classes
  -v, --verbose  prints the intermediate stages. Can take time to print
  -num NUM       Total number of elements
```

## Explanation
![Sasaki algorithm](data/saski.png)

- Each process, except extremes have 2 values in each side (or boxes)
- The area is used to track the movement of marked element, thus is changed only when marked element moves
- In the given code, Whenever the marked element moves from left to right, area is decreased, and increased when the opposite happens.
- When the process finishes, the process having `area < 0` will have their `right_value` taken, rest cases left.
- Note that its not necessary to have both the elements same in the process at the end of the sort.

## References
- [Paper](https://dl.acm.org/citation.cfm?id=585575)
- [Threading](https://docs.python.org/3/library/threading.html)
