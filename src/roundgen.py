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
        games = []
        for game, f1, f2 in self.rounds[self.roundNum]:
            game.teams = (f1(), f2())
            games.append(game)
        self.roundNum += 1
        return games

    def getWinner(self):
        return self.winner()

    def _createRounds(self, trn):
        # create a bye for each team that the next round can be generated from
        teams = trn.getTeams()
        prevRound = [(Game(t), None, None) for t in teams]

        while len(prevRound) >= 2:
            curRound = []
            if len(prevRound) % 2 == 1:
                curRound.append((Game(), prevRound[0][0].getWinner, lambda: None))
                prevRound = prevRound[1:]
            for i in range(len(prevRound)//2):
                curRound.append((Game(),
                    prevRound[i][0].getWinner, prevRound[-i-1][0].getWinner))
            self.rounds.append(curRound)
            prevRound = curRound
        self.winner = prevRound[0][0].getWinner
