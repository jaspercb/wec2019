from game import Game

def getGenerator(mode='single'):
    if mode == 'single':
        return SingleEliminationGenerator()
    elif mode == 'double':
        return DoubleEliminationGenerator()
    else:
        raise ValueError(f'Tournament type {mode} not recognized')

class SingleEliminationGenerator(object):
    def __init__(self):
        self.rounds = [] # list of list of functions to get participants
        self.winner = lambda: None
        self.roundNum = 0

    def generateRound(self, trn):
        if self.roundNum == 0:
            self._createRounds(trn)
        if self.roundNum >= len(self.rounds):
            return None
        games = []
        for game, f1, f2 in self.rounds[self.roundNum]:
            game.teams = (f1(), f2())
            if not game.isNull():
                games.append(game)
        self.roundNum += 1
        return games

    def getWinner(self):
        return self.winner()

    def _createRounds(self, trn):
        teams = trn.getTeams()

        self.rounds = _generateSingleElimBracket(teams)
        self.winner = self.rounds[-1][0].getWinner


class DoubleEliminationGenerator(object):
    def __init__(self):
        self.rounds = [] # list of list of functions to get participants
        self.lastFinal = None
        self.winner = lambda: None
        self.roundNum = 0

    def generateRound(self, trn):
        if self.roundNum == 0:
            self._createRounds(trn)
        while True:
            if self.roundNum == len(self.rounds):
                lastGame = self.rounds[-1][0][0]
                if lastGame.getWinner() == lastGame.teams[0]:
                    self.winner = lastGame.getWinner
                    return None
                else:
                    self.lastFinal = Game(lastGame.teams[0], lastGame.teams[1])
                    self.roundNum += 1
                    return [self.lastFinal]
            elif self.roundNum == len(self.rounds) + 1:
                self.winner = self.lastFinal.getWinner
                return None

            games = []
            for game, f1, f2 in self.rounds[self.roundNum]:
                game.teams = (f1(), f2())
                if not game.isBye():
                    games.append(game)
            self.roundNum += 1
            if games:
                return games

    def getWinner(self):
        return self.winner()

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

if __name__ == '__main__':
    # FIXME: remove
    import tournament
    import sys
    gen = getGenerator('double')
    t = tournament.Tournament([str(x) for x in range(0, int(sys.argv[1]))], gen)
    while True:
        games = gen.generateRound(t)
        if not games:
            break
        print(f'Round {gen.roundNum}')
        for g in games:
            g.score = (0, 1)
            print(g)
    print(gen.getWinner())
