import sys

def bfs(parents, pair):
    open = []
    visited = dict()
    open.append(pair[0])
    open.append(pair[1])
    while len(open) != 0:
        current = open.pop(0)
        p1_p2 = parents.get(frozenset(current))
        if p1_p2 is None:
            continue
        visited[frozenset(current)] = p1_p2
        open.append(p1_p2[0])
        open.append(p1_p2[1])
    return visited

def plResolution(f, g):
    i = 1
    for klauzula in f:
        print(str(i) + '.', end=" ")
        print(' v '.join(klauzula))
        i += 1
    for atom in g:
        print(str(i) + '.', end=" ")
        print("".join(atom))
        i += 1
    print('===============')

    parents = {}
    clauses = []
    clauses.extend(f)
    clauses.extend(g)
    idx = len(clauses)

    while True:
        new = []
        for pair in selectClauses(clauses, f):
            resolvent = plResolve(pair)
            if resolvent == -1:
                res = dict(reversed(list(bfs(parents, pair).items())))
                for key in res.keys():
                    idx += 1
                    p1 = " v ".join(res[key][0])
                    p2 = " v ".join(res[key][1])
                    print("{}. {} {}".format(idx, " v ".join(key), "(" + p1 + " ," + p2 + ")"))

                return True
            if len(resolvent) != 0 and resolvent not in new:
                new.append(resolvent)
                parents[frozenset(resolvent)] = pair

        flag = 0
        if (all(x in clauses for x in new)):
            flag = 1
        if flag:
            return False
        else:
            clauses = clauses + new


def plResolve(pair):
    klauzula1 = pair[0]
    klauzula2 = pair[1]
    resolvent = set()
    contra = ''
    nadeno = False
    ##pronadi dal ima kontradiktornih
    for atom1 in klauzula1: ##tu moze doc da spojis nesto sto je nevaljano uvijek(di to onda maknes??)
        if nadeno == True:
            break
        for atom2 in klauzula2:
            if ("~" + atom1) == atom2:
                nadeno = True
                contra = atom1
                break
            elif atom1 == ("~" + atom2):
                nadeno = True
                contra = atom2
                break
    if nadeno:##ovo moze brze!!
        for atom in klauzula1:
            if atom != contra and atom != ('~' + contra):
                resolvent.add(atom)
        for atom in klauzula2:
            if atom != contra and atom != ('~' + contra):
                resolvent.add(atom)

        if len(resolvent) == 0:
            return -1

    return resolvent

def selectClauses(clauses, f):
    strategijaPojednostavljenja(clauses)
    selected = []
    for klauzula1 in clauses:
        for klauzula2 in clauses:
            if klauzula1 != klauzula2:
                if klauzula1 not in f or klauzula2 not in f:
                    if (klauzula1, klauzula2) not in selected and (klauzula2, klauzula1) not in selected:
                        selected.append((klauzula1, klauzula2))
    return selected


def strategijaPojednostavljenja(clauses):##provjeri dal ovo dobro radi
    # uklanjanje redundantnih
    for klauzula1 in clauses:
        for klauzula2 in clauses:
            if clauses.index(klauzula1) != clauses.index(klauzula2):
                if klauzula1.issubset(klauzula2):
                    clauses.remove(klauzula2)

    #uklanjanje nevaznih
    for klauzula in clauses:
        for atom in klauzula:
            if not atom.startswith('~'):
                neg_atom = '~' + atom
                if neg_atom in klauzula:
                    clauses.remove(klauzula)
                    break
    return


def main():
    arguments = []
    for s in sys.argv:
        arguments.append(s)

    alg = arguments[1]
    if alg == "resolution":
        clauses_path = arguments[2]
        f = open(clauses_path, "r", encoding="utf8")
        clauses = []
        while True:
            line = f.readline()
            if not line:
                break

            if line.startswith("#"):
                continue

            clause = set()
            for atom in line.split():
                if atom == 'v' or atom == 'V':
                    continue
                clause.add(atom.lower())
            clauses.append(clause)

        goal = clauses[-1]
        g = [] ##moras negirat za postupak
        for atom in goal:
            if atom.startswith('~'):
                atom = atom[1:]
            else:
                atom = '~' + atom
            g.append({atom})

        clauses = clauses[:-1]

        if plResolution(clauses, g):
            print('[CONCLUSION]: {} is true'.format(' v '.join(goal)))
        else:
            print('[CONCLUSION]: {} is unknown'.format(' v '.join(goal)))


    elif alg == "cooking": ##ovaj dio treba ic unutar drugog while True??
        clauses_path = arguments[2]
        instructions_path = arguments[3]
        f2 = open(instructions_path, "r", encoding="utf8")
        while True:
            line = f2.readline()
            line = line.strip()
            if not line:
                break
            if line.startswith("#"):
                continue

            print('User’s command: {}'.format(line))##mozda ce trebat lower za autograder
            instruction = line.split()
            znak = instruction[-1]
            instruction = instruction[:-1]
            input_elements = []
            for el in instruction:
                if el.lower() != "v":
                    input_elements.append(el)
            if znak == '?':
                f1 = open(clauses_path, "r", encoding="utf8")
                clauses = []
                while True:
                    line = f1.readline()
                    if not line:
                        break

                    if line.startswith("#"):
                        continue

                    clause = set()
                    for atom in line.split():
                        if atom == 'v' or atom == 'V':
                            continue
                        clause.add(atom.lower())
                    clauses.append(clause)
                f1.close()

                g = []
                for atom in input_elements:
                    if atom.startswith('~'):
                        atom = atom[1:]
                    else:
                        atom = '~' + atom
                    atom = atom.lower()
                    g.append({atom})

                if plResolution(clauses, g):
                    print('[CONCLUSION]: {} is true'.format(' v '.join(input_elements)))
                else:
                    print('[CONCLUSION]: {} is unknown'.format(' v '.join(input_elements)))

            elif znak == '+': ## provjeri dal treba provjeravat duple???
                element_add = " v ".join(input_elements)
                f1 = open(clauses_path, "a", encoding="utf8")
                f1.write(element_add + '\n')
                f1.close()
                print('Added {}'.format(element_add))

            elif znak == '-':
                element_delete = " v ".join(input_elements)
                f1 = open(clauses_path, "r", encoding="utf8")
                data = f1.readlines()
                f1.close()
                f1 = open(clauses_path, "w", encoding="utf8")
                for l in data:
                    if l.strip() != element_delete and l.strip() != element_delete.lower():
                        f1.write(l)
                f1.close()
                print('removed {}'.format(element_delete))

    return
main()