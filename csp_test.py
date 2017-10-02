# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 13:44:58 2017

@author: n.soungadoy
"""
import sys
from itertools import product
import string
from collections import OrderedDict
from multiprocessing import freeze_support
from concurrent.futures import ProcessPoolExecutor
from concurrent import futures
import time

import logging
from driver_3 import ConstraintGenerator, backtracking_search, aggregate, create_graph

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] - %(asctime)s - %(message)s')
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

MAX_WORKER = None

def run(board, solution, i):
    solution = solution.strip()
    graph = create_graph(board)
    s = time.clock()
    result = backtracking_search(graph)
    duration = time.clock() - s
    logging.info("problem:\n{}\n{}".format(solution, board))
    solved = aggregate(graph) == solution
    logging.info("Successful: {} in {} seconds".format(result, duration))
    logging.info("SOLVED: {}".format(solved))
    return solved, duration, i

def main(i):
    with open("sudokus_start.txt", "r") as f:
        boards = f.readlines()

    with open("sudokus_finish.txt", "r") as f:
        solutions = f.readlines()

    n = len(boards)
    count = 0

    i = min(i, n) if i else n
    duration = 0
    failed = []
    with ProcessPoolExecutor(max_workers=MAX_WORKER) as executor:
        fq = []
        for i, (board, solution) in enumerate(zip(boards[:i], solutions[:i])):
             fq.append(executor.submit(run,board, solution, i))

        for future in futures.as_completed(fq):
            result, d, i = future.result()
            duration += d
            if result:
                count += 1
            else:
                failed.append(i)
        logging.info("score: {} / {}, runtime: {:.4f} sec, failed: {}".format(count, n, duration, sorted(failed)))
#    argv = sys.argv

#    print(argv)

if __name__=="__main__":
    i = int(sys.argv[1]) if len(sys.argv) > 1 else None
    freeze_support()
    main(i)