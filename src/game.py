class Game(object):
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

        # will be None until winner is determined
        self.winner = None

    def getTeams(self):
        return (self.team1, self.team2)

    def reportResult(self, winner):
        if winner not in self.getTeams():
            raise ValueError()

        self.winner = winner
