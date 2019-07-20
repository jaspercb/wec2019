class Game(object):
    def __init__(self, team1=None, team2=None):
        self.teams = (team1, team2)

        self.scores = [None]
        self.wins = [0, 0]

    def setScore(self, score, match=0):
        self.scores[match] = score

        self.wins = [sum(1 for score in self.scores
                         if score is not None and score[0] > score[1]),
                     sum(1 for score in self.scores
                         if score is not None and score[1] > score[0])]

    def getScores(self):
        return self.scores

    def getTeams(self):
        return self.teams

    # assumes isComplete()
    def getWinner(self):
        if self.isBye():
            return self.teams[0] if self.teams[0] else self.teams[1]

        return max(zip(self.wins, self.teams))[1]

    # assumes isComplete()
    def getLoser(self):
        if self.isBye():
            return None

        return min(zip(self.wins, self.teams))[1]

    def getOpponent(self, team):
        return self.teams[0] if team != self.teams[0] else self.teams[1]

    def isBye(self):
        return None in self.teams

    def isNull(self):
        return self.teams[0] is None and self.teams[1] is None

    def isComplete(self):
        return self.minimumGamesLeft() <= 0
    
    def gamesPlayed(self):
        return sum(self.wins)

    def minimumGamesLeft(self):
        return int((len(self.scores) + 1) / 2) - max(self.wins)

    def __repr__(self):
        return f'teams: {self.teams}, score: {self.scores}'
