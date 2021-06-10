
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
    socialWelfare(win, ordered, candidateRanking)
    
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

    #remove candidate
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

def socialWelfare(win, ordered, candidateRanking):
    ordinal = []
    cardinal = []

    for i in range(voters):
        #get where the winner ranked in this persons order
        rank = ordered[i].index(win)

        ordinal.append(-pow((rank),2))

        pref = round(-pow(candidateRanking[i][ordered[i][0]-1][1] - candidateRanking[i][win-1][1],2),2)
        cardinal.append(pref)

    # print("Ordinal Social Welfare:",sum(ordinal))
    # print("Cardinal Social Welfare:",sum(cardinal))
    # print("")
    return (sum(ordinal), sum(cardinal))

def partTwo(voters, candidates, tup):
    ordered = deepcopy(tup[0])
    names = tup[1]
    rankings = tup[2]
    connections = deepcopy(tup[3])

    #get initial first choices
    votes = []
    for x in ordered:
        votes.append(x[0])

    print_connections(names, connections, voters, candidates)
    print("")

    print("-----REAL RESULTS-----")
    orig = getWinner(votes.copy())
    print("The winner of the real election is:", orig)
    origWelfare = 0
    for wins in orig:
        origWelfare = origWelfare + socialWelfare(wins, deepcopy(tup[0]), rankings)[0]
    origWelfare = origWelfare/len(orig)
    

    print("")
    print("-----DISHONEST RESULTS-----")

    printOrdered(names, ordered, voters)
    print()

    changedMinds = -1
    while not changedMinds == 0:
        me = 0
        lastMinds = changedMinds
        changedMinds = 0
        for voter in connections:
            #get decision for this round
            tuple = getDecision(votes, [names[me], ordered[me].copy()], orig, votes[me])
            changedMinds = changedMinds + tuple[1]
            if tuple[1] == 1:
                print(names[me], "changed their mind from", votes[me], "to", tuple[0])
            votes[me] = tuple[0]
            me = me+1
        print("Number of Minds Changed:", changedMinds)
        print("Round ended")
        print()
        if changedMinds <= lastMinds-1:
            break
        win = getWinner(votes)
    
    win = getWinner(votes)
    print("The dishonest winners are:", win)

    welfare = 0
    for wins in win:
        welfare = welfare + socialWelfare(wins, deepcopy(tup[0]), rankings)[0]
    welfare = welfare/len(win)

    print("The social welfare of the original winner is", origWelfare)
    print("The social welfare of the dishonest vote is", welfare)

def getDecision(votes, me, orig, myVote):
    #get winner
    orig = getWinner(votes.copy())
    temp = 0
    for x in orig:
        temp = temp + welfare(x, me[1])
    bestWel = temp/len(orig)

    #if prefered candidate will win anyways, just vote for them
    if myVote in orig:
        return (myVote,0)

    
    bestVote = myVote
    for i in range(1,len(me[1])-1):
        # find winners if this person votes for every different person 
        # (except their first and last choices)
        temp = votes.copy()
        temp.append(me[1][i])
        winners = getWinner(temp)

        #check if the winners change
        if not winners == orig:
            #get welfare of new winners
            temp = 0
            for x in winners:
                temp = temp + welfare(x, me[1])
            newWel = temp/len(winners)
            

            #check if new welfare is better than old welfare
            if newWel > bestWel:
                bestVote = me[1][i]
                bestWel = newWel
    
    if bestVote == myVote:
        return bestVote,0
    else:
        return bestVote,1

def getWinner(votes):
    #count number of votes
    count = [0 for x in range(candidates+1)] 
    for i in votes:
        count[i-1] = count[i-1]+1
    
    #find winner
    max = 0
    counter = 0
    winners = []
    for x in count:
        if x > max:
            max = x
            winners = []
            winners.append(counter+1)
        elif x == max:
            winners.append(counter+1)
        counter = counter + 1
    return winners

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
    voters = 5
    candidates = 3
    tup = create_voting(voters, candidates, False)
    print("")
    # partOne(voters, candidates, tup)
    partTwo(voters, candidates, tup)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

# Python code to demonstrate namedtuple()
