import sys
import heapq
import time
class Node:
    def __init__(self, label, weight, heuristic, parent):
        self.label = label
        self.weight = weight
        self.heuristic = heuristic
        self.parent = parent
        self.neighbours = []

    def getLabel(self):
        return self.label

    def getWeight(self):
        return self.weight

    def setWeight(self, weight):
        self.weight = weight

    def getHeuristic(self):
        return self.heuristic

    def getParent(self):
        return self.parent

    def __hash__(self):
        return hash((self.getLabel(), self.getWeight()))

    def __eq__(self, other):
        return self.label == other.label

    def __lt__(self, other):
        if self.getHeuristic() is not None and other.getHeuristic() is not None:
            if self.getHeuristic() == other.getHeuristic():
                return self.getLabel() < other.getLabel()
            else:
                return self.getHeuristic() < other.getHeuristic()
        else:
            if self.getWeight() == other.getWeight():
                return self.getLabel() < other.getLabel()
            else:
                return self.getWeight() < other.getWeight()

def expand_bfs(current, succ, visited):
    new = []
    neighbours = succ.get(current.getLabel())
    for neighbour in neighbours.items():
        if neighbour[0] not in visited:
            new.append(Node(neighbour[0], neighbour[1] + current.getWeight(), None, current))
    new.sort(key=lambda x: x.getLabel())
    return new

def bfs(s0, succ, goal):
    open = []
    visited = set()
    open.append(Node(s0, 0, None, None))

    while len(open) !=0:

        current = open.pop(0)
        label = current.getLabel()
        visited.add(label)

        if label in goal:
            print('[FOUND_SOLUTION]: yes')
            print('[STATES_VISITED]:', len(visited))
            path = []
            total_cost = current.getWeight()
            while current is not None:
                path.insert(0, current.getLabel())
                current = current.getParent()

            print('[PATH_LENGTH]:', len(path))
            print('[TOTAL_COST]:', total_cost)
            print('[PATH]:', ' => '.join(path))
            return

        open.extend(expand_bfs(current, succ, visited))
    print('[FOUND_SOLUTION]: no')
    return

def expand_ucs(current, succ, visited, open):
    neighbours = succ.get(current.getLabel())
    for neighbour in neighbours.items():
        if neighbour[0] not in visited:
            heapq.heappush(open, Node(neighbour[0], neighbour[1] + current.getWeight(), None, current))
    return

def ucs(s0, succ, goal, optimistic):
    open = []
    heapq.heapify(open)
    visited = set()
    heapq.heappush(open, Node(s0, 0, None, None))

    while len(open) != 0:
        current = heapq.heappop(open)
        label = current.getLabel()
        visited.add(label)

        if label in goal:
            if optimistic == False:
                print('[FOUND_SOLUTION]: yes')
                print('[STATES_VISITED]:', len(visited))
                path = []
                total_cost = current.getWeight()
                while current is not None:
                    path.insert(0, current.getLabel())
                    current = current.getParent()

                print('[PATH_LENGTH]:', len(path))
                print('[TOTAL_COST]:', total_cost)
                print('[PATH]:', ' => '.join(path))
                return
            else:
                return current.getWeight()

        expand_ucs(current, succ, visited, open)
    print('[FOUND_SOLUTION]: no')
    return


def astar(s0, succ, goal, h):
    open = []
    heapq.heapify(open)
    visited = set()
    heapq.heappush(open, Node(s0, 0, h[s0], None))
    while len(open) != 0:
        current = heapq.heappop(open)
        label = current.getLabel()
        visited.add(current)

        if label in goal and h[label] == 0:
            print('[FOUND_SOLUTION]: yes')
            print('[STATES_VISITED]:', len(visited))
            path = []
            total_cost = current.getWeight()
            while current is not None:
                path.insert(0, current.getLabel())
                current = current.getParent()

            print('[PATH_LENGTH]:', len(path))
            print('[TOTAL_COST]:', total_cost)
            print('[PATH]:', ' => '.join(path))
            return
        #ako ga ne returnas u proslom ifu onda..
        neighbours = succ.get(current.getLabel())
        for neighbour in neighbours.keys():
            new_node = Node(neighbour, current.getWeight() + neighbours[neighbour],
                            current.getWeight() + neighbours[neighbour] + h[neighbour], current)
            if new_node in open:
                idx = open.index(new_node)
                old = open[idx]
                if old.getWeight() >= new_node.getWeight():
                    open.remove(old)
                else:
                    continue
            elif new_node in visited:## mozda probat samo dohvatit index pa ako uspije onda dalje, dal moram probavat u visited ako ga nadem u open
                l = list(visited)
                #idx = visited.index(new_node)
                idx = l.index(new_node)
                if l[idx].getWeight() >= new_node.getWeight():
                    visited.remove(new_node)
                else:
                    continue
            heapq.heappush(open, new_node)

    print('[FOUND_SOLUTION]: no')
    return


def load_heuristic(path_heuristic):
    data = open(path_heuristic, "r", encoding="utf8").readlines()
    h = {}
    for line in data:
        line = line.split(':')
        h[line[0].strip()] = float(line[1].strip())
    return h


def main():
    arguments = []
    for s in sys.argv:
        arguments.append(s)
    arguments = arguments[1:]
    alg = ''
    path_states = ''
    path_heuristic = ''
    check_optimistic = False
    check_consistent = False
    for i in range(len(arguments)):##PROVIJERI DAL RADI ZA BILOKAKAV REDOSLIJED ARGUMENATA!!!
        if arguments[i] == '--alg':
            alg = arguments[i+1]
        elif arguments[i] == '--ss':
            path_states = arguments[i+1]
        elif arguments[i] == '--h':
            path_heuristic = arguments[i+1]
        elif arguments[i] == '--check-optimistic':
            check_optimistic = True
        elif arguments[i] == '--check-consistent':
            check_consistent = True

    ##UCITAJ PODATKE O STANJIMA
    data = open(path_states, "r", encoding="utf8").readlines()
    for redak in data:
        if redak.startswith('#'):
            data.remove(redak)

    s0 = data[0].strip()
    goal = data[1].strip().split()
    data = data[2:]
    succ = {}
    for redak in data:
        redak = redak.strip()
        redak = redak.split(':')
        lista_susjeda = redak[1].split()
        lista_susjeda = sorted(lista_susjeda)
        susjedi = {}
        for element in lista_susjeda:
            podaci = element.split(',')
            susjedi[podaci[0]] = float(podaci[1])
        succ[redak[0]] = susjedi

    ##ODLUCI KOJI ALGORITAM
    if alg != '':
        if alg == 'bfs':
            print('# BFS')
            bfs(s0, succ, goal)
        elif alg == 'ucs':
            print('# UCS')
            ucs(s0, succ, goal, False)
        elif alg == 'astar':
            h = load_heuristic(path_heuristic)
            #t0 = time.time()
            print('# A-STAR {}'.format(path_heuristic))
            #print(time.time() - t0)
            astar(s0, succ, goal, h)

    else:
        h = load_heuristic(path_heuristic)
        if check_optimistic: ##sta ako nema ciljnog cvora??
            opti = True
            print('# HEURISTIC-OPTIMISTIC {}'.format(path_heuristic))
            for s in succ.keys():
                real_cost = float(ucs(s, succ, goal, True))
                heuristic_cost = h[s]
                if heuristic_cost > real_cost:
                    opti = False
                    print('[CONDITION]: [ERR] h({}) <= h*: {} <= {}'.format(s, heuristic_cost, real_cost))
                else:
                    print('[CONDITION]: [OK] h({}) <= h*: {} <= {}'.format(s, heuristic_cost, real_cost))

            if opti:
                print('[CONCLUSION]: Heuristic is optimistic.')
            else:
                print('[CONCLUSION]: Heuristic is not optimistic.')

        elif check_consistent:
            consistent = True
            print('# HEURISTIC-CONSISTENT {}'.format(path_heuristic))
            for s0 in succ.keys():
                distances = succ[s0]
                for neighbour in distances.keys():
                    h0 = h[s0]
                    h1 = h[neighbour]
                    if h0 > h1 + distances[neighbour]:
                        consistent = False
                        print('[CONDITION]: [ERR] h({}) <= h({}) + c: {} <= {} + {}'.format(s0, neighbour, h0, h1, distances[neighbour]))
                    else:
                        print('[CONDITION]: [OK] h({}) <= h({}) + c: {} <= {} + {}'.format(s0, neighbour, h0, h1, distances[neighbour]))

            if consistent:
                print('[CONCLUSION]: Heuristic is consistent.')
            else:
                print('[CONCLUSION]: Heuristic is not consistent.')

    return
main()

