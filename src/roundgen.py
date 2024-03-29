from collections import defaultdict

from game import Game

def getGenerator(mode='single'):
    if mode == 'single':
        return SingleEliminationGenerator()
    elif mode == 'double':
        return DoubleEliminationGenerator()
    elif mode == 'roundrobin':
        return RoundRobinGenerator()
    elif mode == 'swiss':
        return SwissGenerator()
    else:
        raise ValueError(f'Tournament type {mode} not recognized')

class SingleEliminationGenerator(object):
    def __init__(self):
        self.rounds = [] # list of list of functions to get participants
        self.roundNum = 0

        self.previousRound = []
        self.eliminated = []

    def generateRound(self, trn):
        if self.roundNum == 0:
            self._createRounds(trn)

        
        for g in self.previousRound:
            if g.getLoser():
                self.eliminated.append((self.roundNum, g.getLoser()))
        if self.roundNum >= len(self.rounds):
            self.eliminated.append((self.roundNum+1,
                self.rounds[-1][0][0].getWinner()))
            return None
        games = []
        for game, f1, f2 in self.rounds[self.roundNum]:
            game.teams = (f1(), f2())
            if not game.isNull():
                games.append(game)
        self.roundNum += 1
        self.previousRound = games

        return games

    def getRanking(self):
        return _getRanking(self.eliminated)

    def _createRounds(self, trn):
        teams = trn.getTeams()

        self.rounds = _generateSingleElimBracket(teams)


class DoubleEliminationGenerator(object):
    def __init__(self):
        self.rounds = [] # list of list of functions to get participants
        self.lastFinal = None
        self.roundNum = 0

        self.previousRound = []
        self.eliminated = []
        self.losses = defaultdict(int)

    def generateRound(self, trn):
        if self.roundNum == 0:
            self._createRounds(trn)
        while True:
            for g in self.previousRound:
                l = g.getLoser()
                if l:
                    self.losses[l] += 1
                    if self.losses[l] == 2:
                        self.eliminated.append((self.roundNum, g.getLoser()))

            if self.roundNum == len(self.rounds):
                lastGame = self.rounds[-1][0][0]
                if lastGame.getWinner() == lastGame.teams[0]:
                    self.eliminated.append((self.roundNum + 1, lastGame.getWinner()))
                    return None
                else:
                    self.lastFinal = Game(lastGame.teams[0], lastGame.teams[1])
                    self.roundNum += 1
                    self.previousRound = [self.lastFinal]
                    return self.previousRound
            elif self.roundNum == len(self.rounds) + 1:
                self.eliminated.append((self.roundNum + 1, self.lastFinal.getWinner()))
                return None

            games = []
            for game, f1, f2 in self.rounds[self.roundNum]:
                game.teams = (f1(), f2())
                if not game.isBye():
                    games.append(game)
            self.roundNum += 1
            if games:
                self.previousRound = games
                return games

    def getRanking(self):
        return _getRanking(self.eliminated)

    def _createRounds(self, trn):
        teams = trn.getTeams()

        if len(teams) == 2:
            g = Game()
            self.rounds = [
                [(g, lambda: teams[0], lambda: teams[1])],
                [(Game(), g.getWinner, g.getLoser)],
            ]
            return

        wrounds = _generateSingleElimBracket(teams)
        lrounds = _generateLosersBracket(wrounds)

        self.rounds = []
        self.rounds.append(wrounds[0])

        for i in range(len(wrounds)-1):
            self.rounds.append(wrounds[i+1] + lrounds[i*2])
            self.rounds.append(lrounds[i*2+1])

        # first final
        wwinner = wrounds[-1][0][0].getWinner
        lwinner = lrounds[-1][0][0].getWinner

        self.rounds.append([(Game(), wwinner, lwinner)])

class RoundRobinGenerator(object):
    def __init__(self):
        self.rounds = [] # list of list of functions to get participants
        self.roundNum = 0

    def generateRound(self, trn):
        if self.roundNum == 0:
            self._createRounds(trn)

        if self.roundNum >= len(self.rounds):
            return None
        self.roundNum += 1
        return self.rounds[self.roundNum-1]

    def getRanking(self):
        wins = defaultdict(int)
        for r in self.rounds:
            for g in r:
                wins[g.getWinner()] += 1
        return _getRanking(sorted([(v, k) for (k, v) in wins.items()]))

    def _createRounds(self, trn):
        teams = trn.getTeams()

        if len(teams) % 2 == 1:
            teams.append(None)
        numRounds = len(teams)-1
        self.rounds = []
        for i in range(numRounds):
            curRound = []
            for j in range(0, len(teams)//2):
                curRound.append(Game(teams[j], teams[-1-j]))
            tmp = teams[1]
            for j in range(1, len(teams)-1):
                teams[j] = teams[j+1]
            teams[-1] = tmp
            self.rounds.append(curRound)

class SwissGenerator(object):
    def __init__(self):
        self.rounds = [] # list of list of functions to get participants
        self.roundNum = 0

        self.teams = None
        self.scores = defaultdict(int)
        self.played = defaultdict(set)

        self.previousRound = []

    def generateRound(self, trn):
        self.teams = trn.getTeams()
        for g in self.previousRound:
            self.scores[g.getWinner()] += 1
        if 2**(self.roundNum) >= len(self.teams):
            return None

        t = [y for (x, y) in reversed(sorted([(self.scores[t], t) for t in self.teams]))]
        games = []
        assigned = set()
        for team in t:
            if team in assigned:
                continue
            assigned.add(team)
            found = False
            for team2 in t:
                if team2 in assigned:
                    continue
                if team2 in self.played[team]:
                    continue
                games.append(Game(team, team2))
                self.played[team].add(team2)
                self.played[team2].add(team)
                assigned.add(team2)
                found = True
                break
            if not found:
                # give bye
                games.append(Game(team, None))
        self.roundNum += 1
        self.previousRound = games
        return games

    def getRanking(self):
        return _getRanking(sorted([(v, k) for (k, v) in self.scores.items()]))

def _generateSingleElimRound(prevRound):
    curRound = []
    for i in range(0, len(prevRound), 2):
        curRound.append((Game(),
            prevRound[i][0].getWinner, prevRound[i+1][0].getWinner))
    return curRound

def _generateOrdering(size):
    roundSize = 1
    prevRound = [0]
    while roundSize < size:
        roundSize *= 2
        prevRound = [x for i in prevRound for x in (i, roundSize-1-i)]
    return prevRound

def _generateSingleElimBracket(teams):
    ordering = _generateOrdering(len(teams))

    prevRound = [(Game(teams[i]), None, None) if i < len(teams) else (Game(), None, None)
        for i in ordering]

    rounds = []

    while len(prevRound) >= 2:
        curRound = []
        for i in range(0, len(prevRound), 2):
            curRound.append((Game(),
                prevRound[i][0].getWinner, prevRound[i+1][0].getWinner))
        rounds.append(curRound)
        prevRound = curRound
    return rounds

def _generateLosersBracket(wrounds):
    prevRound = []
    for i in range(0, len(wrounds[0]), 2):
        prevRound.append((Game(), wrounds[0][i][0].getLoser, wrounds[0][i+1][0].getLoser))

    rounds = [prevRound]
    reverse = True
    for wround in wrounds[1:]:
        curRound = []
        # generate major round, pulling in from wround
        if reverse:
            wround = reversed(wround)
        reverse = not reverse
        for wgame, lgame in zip(wround, prevRound):
            curRound.append((Game(), wgame[0].getLoser, lgame[0].getWinner))
        prevRound = curRound
        rounds.append(prevRound)

        if len(prevRound) < 2:
            continue
        prevRound = _generateSingleElimRound(prevRound)
        rounds.append(prevRound)
    return rounds

def _generateSeededOrdering(size):
    roundSize = 1
    prevRound = [0]
    while roundSize < size:
        roundSize *= 2
        prevRound = [x for i in prevRound for x in (i, roundSize-1-i)]
    return prevRound

def _getRanking(eliminated):
    pplace = 0
    pround = 1 << 64
    placements = []
    for i, (r, t) in enumerate(reversed(eliminated)):
        if r < pround:
            pround = r
            pplace = i+1
        placements.append((pplace, t))
    return placements

if __name__ == '__main__':
    # FIXME: remove
    import tournament
    import sys
    import random
    gen = getGenerator('swiss')
    t = tournament.Tournament([str(x) for x in range(0, int(sys.argv[1]))], gen)
    while True:
        games = gen.generateRound(t)
        if not games:
            break
        print(f'Round {gen.roundNum}')
        for g in games:
            v = random.randint(0, 1)
            g.setScore((v, 1-v))
            print(g)
    print('\n'.join(map(str, gen.getRanking())))
