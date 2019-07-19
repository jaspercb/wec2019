from collections import OrderedDict


class Tournament(object):
    def __init__(self, teams, round_generator):
        # win/loss record for each team, ordered by original seed
        self.team_records = OrderedDict([(team, (0, 0)) for team in teams])

        self.games = round_generator.generateGames(self)
        self.next_game_id = 0

    def currentGames(self):
        return self.games[self.next_game_id:]

    def reportResult(self, gameid, winner):
        self.games[gameid]

    def getTeamRecord(self, string):
        self.team_records[string]

    def getTeams(self):
        return [name for name in self.team_records.keys()]

    def getTeamHistory(self, team):
        return [game for game in self.games if team in game.getTeams()]
