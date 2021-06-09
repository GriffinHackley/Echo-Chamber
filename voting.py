
from typing import OrderedDict
from copy import deepcopy
import numpy

CAND = 0  # subscript of list which represents the candidate
SCORE = 1  # subscript of list which represents the score of the candidate
PLACE = 2  # subscript of list which represents the rankding, lowest is best

def print_connections(names, c, voters, candidates):
    print("CONNECTIONS")
    for i in range(voters):
        print("%10s" % (names[i]), end=" ")
        for j in range(voters):
            print(c[i][j], end=' ')
        print()

def print_rankings(names, r, voters, candidates, ordered):
    print("CANDIDATE Rankings")
    for i in range(voters):
        #print("First choice for {} is {}".format(names[i], ordered[i][CAND]), end=" ")
        print(names[i], end=" ")
        for j in range(candidates):
            print(r[i][j], end='')
        print(" ORDER ", ordered[i])

def create_voting(voters, candidates, printConnections):
    names = ["Alice ", "Bart  ", "Cindy ", "Darin ", "Elmer ", "Finn  ", "Greg  ", "Hank  ", "Ian   ", "Jim   ",
             "Kate  ", "Linc  ", "Mary  ", "Nancy ", "Owen  ", "Peter ", "Quinn ", "Ross  ", "Sandy ", "Tom   ",
             "Ursula", "Van   ", "Wendy ", "Xavier", "Yan   ", "Zach  "]

    connections = [[0 for i in range(voters)] for j in range(voters)]
    ordered = [[] for i in range(voters)]
    numpy.random.seed(1052)
    for i in range(voters):
        conn = round(numpy.random.uniform(0, voters / 2))
        for j in range(conn):
            connectTo = numpy.random.randint(0, voters)
            if (connectTo!=i):
                connections[i][connectTo] = 1
    if printConnections:
        print_connections(names, connections, voters, candidates)
    candidateRanking = [[list() for i in range(candidates)] for j in range(voters)]
    for i in range(voters):
        for j in range(candidates):
            candidateRanking[i][j] = [j + 1, round(numpy.random.uniform(0, 100)) / 10, 0]
        # print(candidateRanking[i])
        s = sorted(candidateRanking[i], reverse=True, key=lambda v: v[SCORE])
        ordered[i] = [s[i][CAND] for i in range(candidates)]
        for v in range(candidates):
            candidate = s[v][CAND] - 1  # which candidate has rank v+1
            candidateRanking[i][candidate][PLACE] = v + 1
    print_rankings(names, candidateRanking, voters, candidates, ordered)
    return (ordered, names, candidateRanking, connections)

def partOne(voters, candidates, tup):
    ordered = deepcopy(tup[0])
    names = tup[1]
    candidateRanking = tup[2]

    win = winner(voters, ordered, candidates, names, [])
    print("The winner is", win)
    ordered = deepcopy(tup[0])
    socialWelfare(win, ordered, candidates, names, candidateRanking)
    
def winner(voters, rankings, candidates, names, removed):
    rankings = deepcopy(rankings)
    #base case: if only one candidate left, return that candidate
    if candidates == 1:
        return rankings[0][0]

    count = []
    count = [0 for i in range(candidates+1+len(removed))]
    count[0] = voters+1

    #go through first choice of every voter
    for i in range(voters):
        #get first choice
        first = rankings[i][0]

        #count number of first choice votes per candidate
        count[first] = count[first] + 1
    
    #find candidate with least first choice votes
    min = 0
    for i in range(1,candidates+1+len(removed)):
        if not (i in removed):
            if count[i] < count[min]:
                min = i
    # print(count)

    #check if there is a tie for least wins
    tie = False
    if count.count(count[min]) > 1:
        indices = [i for i, x in enumerate(count) if x == count[min]]
        indices = [x for x in indices if x not in removed]
        tie = True
    
    #if there is a tie, then remove the one with most last place votes
    if tie:
        count = []
        count = [0 for i in range(len(indices))]

        #check last votes for only the ones that tied
        for i in range(voters):
            #find lowest ranked of tied
            j = candidates-1
            while not (rankings[i][j] in indices):
                j = j-1
            
            #update count
            for x in range(len(indices)):
                if indices[x] == rankings[i][j]:
                    count[x] = count[x]+1
        
        min = 0
        for i in range(len(count)):
            if count[i] < count[min]:
                min = i

        min = indices[min]

    #remove candidate with least first choices
    for i in range(voters):
        rankings[i].remove(min)
    removed.append(min)
    
    # printOrdered(names, rankings, voters)
    return winner(voters, rankings, candidates-1, names, removed)

def printOrdered(names, ordered, voters):
    print("")
    for i in range(voters):
        print(names[i], end=" ")
        print(ordered[i])

def socialWelfare(win, ordered, candidates, names, candidateRanking):
    ordinal = []
    cardinal = []

    # print(candidateRanking)

    for i in range(voters):
        #get where the winner ranked in this persons order
        rank = ordered[i].index(win)

        ordinal.append(-pow((rank),2))

        pref = round(-pow(candidateRanking[i][ordered[i][0]-1][1] - candidateRanking[i][win-1][1],2),2)
        cardinal.append(pref)

    print("Ordinal Social Welfare:",sum(ordinal))
    print("Cardinal Social Welfare:",sum(cardinal))
    print("")

def partTwo(voters, candidates, tup):
    ordered = deepcopy(tup[0])
    names = tup[1]
    connections = deepcopy(tup[3])

    print_connections(names, connections, voters, candidates)
    print("")

    print("-----REAL RESULTS-----")
    print("The winner of the real election is:", winner(voters, ordered, candidates, names, []))

    print("")
    print("-----DISHONEST RESULTS-----")

    printOrdered(names, ordered, voters)

    tup = singleElimination(voters, ordered, candidates, names, [])
    ordered = tup[0]
    removed = tup[1]
    candidates = candidates - 1 

    #generate model of echo chamber
    me = 0
    votes = []
    changedMinds = 0
    for voter in connections:
        echoName = []
        echoVote = []
        count = 0
        for i in voter:
            if i == 1:
                echoName.append(names[count])
                echoVote.append(ordered[count].copy())
            count = count+1
        tup = getDecision(echoName, echoVote, candidates, [names[me],ordered[me].copy()])
        if tup[1]:
            changedMinds = changedMinds + 1
        votes.append(tup[0])
        me = me+1

    for vote in votes:
        print(vote)

def getDecision(names, ordered, candidates, me):
    current = deepcopy(ordered)
    names.append(me[0])
    current.append(me[1].copy())
    # for x in range(len(names)):
    #     print(names[x],":",current[x])
    orig = winner(len(names), current, candidates, names, [])
    best = me[1]
    changedMind = False    

    #try permutations where any candidate ranked higher than the winner is put in first place
    if not orig == me[1][0]:
        # print("Original Winner:", orig)
        # print("Original Welfare:", welfare(orig, me[1]))
        for i in range (1,candidates):
            others = deepcopy(ordered)

            # add new permutation
            test = me[1].copy()
            if test[i] == orig:
                break
            test.insert(0, test.pop(i))

            others.append(test)

            #find welfare of this permutation
            current = winner(len(names), others, candidates, names, [])
            others = deepcopy(ordered)
            others.append(best)
            toBeat = winner(len(names), others, candidates, names, [])
            if not current == orig:
                if welfare(current, me[1]) > welfare(toBeat, me[1]):
                    best = test
                    changedMind = True
                    # print("HERE-----------------------------------------")
                    # print(test)
                    # print("New Winner:", current)
                    # print("New Welfare:", welfare(current, me[1]))
    # else:
    #     print("It matched")
    # print("")
    return (best,changedMind)

def singleElimination(voters, rankings, candidates, names, removed):
    rankings = deepcopy(rankings)

    count = []
    count = [0 for i in range(candidates+1+len(removed))]
    count[0] = voters+1

    #go through first choice of every voter
    for i in range(voters):
        #get first choice
        first = rankings[i][0]

        #count number of first choice votes per candidate
        count[first] = count[first] + 1
    
    #find candidate with least first choice votes
    min = 0
    for i in range(1,candidates+1+len(removed)):
        if not (i in removed):
            if count[i] < count[min]:
                min = i

    #check if there is a tie for least wins
    tie = False
    if count.count(count[min]) > 1:
        indices = [i for i, x in enumerate(count) if x == count[min]]
        indices = [x for x in indices if x not in removed]
        tie = True
    
    #if there is a tie, then remove the one with most last place votes
    if tie:
        count = []
        count = [0 for i in range(len(indices))]

        #check last votes for only the ones that tied
        for i in range(voters):
            #find lowest ranked of tied
            j = candidates-1
            while not (rankings[i][j] in indices):
                j = j-1
            
            #update count
            for x in range(len(indices)):
                if indices[x] == rankings[i][j]:
                    count[x] = count[x]+1
        
        min = 0
        for i in range(len(count)):
            if count[i] < count[min]:
                min = i

        min = indices[min]

    #remove candidate with least first choices
    for i in range(voters):
        rankings[i].remove(min)
    removed.append(min)
    
    printOrdered(names, rankings, voters)
    return (rankings, removed)

def welfare(winner, order):
    rank = order.index(winner)
    welfare = -pow((rank),2)
    return welfare

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    voters = 7
    candidates = 4
    tup = create_voting(voters, candidates, False)
    print("")
    # partOne(voters, candidates, tup)
    partTwo(voters, candidates, tup)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Python code to demonstrate namedtuple()
