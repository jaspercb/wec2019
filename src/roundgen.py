from game import Game

def getGenerator(mode='single'):
    if mode == 'single':
        return SingleEliminationGenerator()
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
        # create a bye for each team that the next round can be generated from
        teams = trn.getTeams()

        ordering = self._generateOrdering(len(teams))

        prevRound = [(Game(teams[i]), None, None) if i < len(teams) else (Game(), None, None)
            for i in ordering]

        while len(prevRound) >= 2:
            curRound = []
            if len(prevRound) % 2 == 1:
                curRound.append((Game(), prevRound[0][0].getWinner, lambda: None))
                prevRound = prevRound[1:]
            for i in range(0, len(prevRound), 2):
                curRound.append((Game(),
                    prevRound[i][0].getWinner, prevRound[i+1][0].getWinner))
            self.rounds.append(curRound)
            prevRound = curRound
        self.winner = prevRound[0][0].getWinner

    def _generateOrdering(self, size):
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
    gen = getGenerator()
    t = tournament.Tournament([str(x) for x in range(0, int(sys.argv[1]))], gen)
    while True:
        games = gen.generateRound(t)
        if not games:
            break
        print(f'Round {gen.roundNum}')
        for g in games:
            g.score = (1, 0)
            print(g)
    print(gen.getWinner())
