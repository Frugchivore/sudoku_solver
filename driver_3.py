# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 17:19:08 2017

@author: n.soungadoy
"""
import sys
import string

from itertools import product

from collections import OrderedDict, deque

class ConstraintGenerator:
    def __init__(self):
        self.constraints = {}
    def clear(self):
        self.constraints.clear()

    def create_constraints_set(self, item):
        constraints = set()
        constraints.update(self._create_row_constraints(item))
        constraints.update(self._create_column_constraints(item))
        constraints.update(self._create_box_constraints(item))
        return constraints

    def _create_row_constraints(self, item):
        iterator = product(item[0], range(1,10))
        c = []
        for other in iterator:
            other = "{}{}".format(*other)
            if item != other:
                c.append(self.get_constraint(item, other))
        return set(c)

    def _create_column_constraints(self, item):
        iterator = product(string.ascii_uppercase[:9], item[1])
        c = []
        for other in iterator:
            other = "{}{}".format(*other)
            if item != other:
                c.append(self.get_constraint(item, other))
        return set(c)

    def _create_box_constraints(self, item):
        rows = ['ABC', 'DEF', 'GHI']
        cols = ['123','456','789']
        blocks = product(rows, cols)
        for block in blocks:
            if item[0] in block[0] and item[1] in block[1]:
                iterator = product(*block)
                c = []
                for other in iterator:
                    other = "{}{}".format(*other)
                    if item != other:
                        c.append(self.get_constraint(item, other))
                return set(c)

    def get_constraint(self, x, y):
        arc = frozenset((x, y))
        constraint = self.constraints.get(arc)
        if constraint is None:
            constraint = BinaryConstraint(arc)
            self.constraints[arc] = constraint
        return constraint


class BinaryConstraint:
    def __init__(self, arc):
        self.arc = arc

    def __hash__(self):
        return hash((self.arc))

    def __repr__(self):
        return str("constraint({}, {})".format(*self.arc))

    def __contains__(self, item):
        return item in self.arc

    def other(self, x):
        a, b = self.arc
        if x == a:
            return b
        else:
            return a

    @staticmethod
    def check_domain(v, y, graph):
        domain = graph[y]['domain']
        satisfied = domain.intersection({v}) != domain
        return satisfied

    def check_value(self, graph):
        x, y = self.arc
        satisfied = graph[x]['value'] != graph[y]['value']
        return satisfied


def revise(csp, i, j, c):
    revised = False
    removed = set()
    for v in csp[i]['domain']:
        if not c.check_domain(v, j, csp):
            removed.add(v)
            revised = True
    csp[i]['domain'].difference_update(removed)

    return revised


def ac3(csp):
    q = deque()
    for key, node in csp.items():
        q.extend(node['constraints'])
    count = 0
    while q:
        count += 1
        c = q.pop()
        i, j = c.arc

        if revise(csp, i, j, c):
            if len(csp[i]['domain']) == 0:
                return False
            q.extend( csp[i]['constraints'].difference({c}))

        if revise(csp, j, i, c):
            if len(csp[j]['domain']) == 0:
                return False
            q.extend( csp[j]['constraints'].difference({c}))
    return True


def inference(assignments, key, csp):
    """
    Implement forward checking heuristic
    """

#    return True

    _, a = assignments[key]
    for c in csp[key]['constraints']:
        other = c.other(key)
        if a in csp[other]['domain']:
            if csp[other]['domain'].difference({a}):
                csp[other]['domain'].remove(a)
            else:
                return False
            assignments[other] = (csp[other]['value'], a)
    return True


def order_domain_value(key, csp):
    """
    no heuristic is used, returns the iterator over the domain
    """
    return ( {key : (0, d)} for d in csp[key]['domain'])


def is_complete(csp):
    return 0 not in (n['value'] for n in csp.values() if n['value'] == 0)


def select_unassigned_variables(csp):
    """
    Use MRV, returns the key of a node.
    """
    _, key = min((len(n['domain']), key) for key, n in csp.items() if n['value'] == 0)
    return key


def remove(assignments, csp):
    for key, value in assignments.items():
        csp[key]['value'] = value[0]
        csp[key]['domain'].add(value[1])


def is_consistent(assignments, key, csp):
    old = csp[key]['value']
    csp[key]['value'] = assignments[key][1]
    for c in csp[key]['constraints']:
        if not c.check_value(csp):
            csp[key]['value'] = old
            return False
    return True


def is_consistent2(assignments, key, csp):
    old = csp[key]['value']
    csp[key]['value'] = assignments[key][1]
    for c in csp[key]['constraints']:
        if not c.check_value(csp):
            csp[key]['value'] = old
            return False
    csp[key]['domain'].remove(assignments[key][1])
    return True


def backtrack(csp):
    if is_complete(csp):
        return True

    key = select_unassigned_variables(csp)
    for assignments in order_domain_value(key, csp):
        if is_consistent(assignments, key, csp):
            if inference(assignments, key, csp):
                result = backtrack(csp)
                if result:
                    return result

        remove(assignments, csp)

    return False


def backtracking_search(csp):
    if ac3(csp):
        result = backtrack(csp)
    else:
        result = False
    return result


def aggregate(graph):
    return ''.join(str(n['value']) for n in graph.values())


def create_graph(board):
    iterator = product(string.ascii_uppercase, range(1,10))
    cg = ConstraintGenerator()
    graph = OrderedDict()
    for i, v in zip(iterator, board.strip()):
        key = "{}{}".format(*i)
        v = int(v)
        node = {}
        node['value'] = v
        node['domain'] = set(i for i in range(1,10)) if v == 0 else {v}
        node['constraints'] = cg.create_constraints_set(key)
        graph[key] = node
    cg.clear()
    return graph


def output(fname, solution):
    with open(fname, 'w') as f:
        f.write(solution)


if __name__=="__main__":
    board = sys.argv[1]
    iterator = product(string.ascii_uppercase, range(1,10))
    graph = create_graph(board)
    solved = backtracking_search(graph)
    solution = aggregate(graph)
    output("output.txt", solution)
#    argv = sys.argv

#    print(argv)