class Game(object):
    def __init__(self, team1=None, team2=None):
        self.teams = (team1, team2)
        self.score = (0, 0)

    def getTeams(self):
        return self.teams

    def getWinner(self):
        if self.isBye():
            return self.teams[0]
        return max(zip(self.score, self.teams))[1]

    def getLoser(self):
        if self.isBye():
            return None
        return min(zip(self.score, self.teams))[1]

    def getOpponent(self, team):
        return self.teams[0] if team != self.teams[0] else self.teams[1]

    def isBye(self):
        return self.teams[1] == None

    def isNull(self):
        return self.teams[0] == None and self.teams[1] == None

    def __repr__(self):
        return f'teams: {self.teams}, score: {self.score}'
