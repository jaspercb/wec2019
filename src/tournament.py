from collections import OrderedDict


class Tournament(object):
    def __init__(self, teams, round_generator):
        self.next_game_id = 0

        # win/loss record for each team, ordered by original seed
        self.team_records = OrderedDict([(team, (0, 0)) for team in teams])

        # stores games in consistent "scheduled order"
        # (games in a round may be played out of order)
        self.current_round = OrderedDict()

        for game in round_generator.generateGames(self):
            self.current_round[self.next_game_id] = game
            self.next_game_id += 1

        # will store games in order they were played
        self.past_games = OrderedDict()

    # games in current round
    def currentGames(self):
        return self.current_round.keys()

    def getGame(self, gameid):
        if gameid in self.current_round.keys():
            return self.current_round[gameid]
        elif gameid in self.past_games.keys():
            return self.past_games[gameid]
        raise KeyError()

    def reportResult(self, gameid, winner):
        self.current_round[gameid].reportResult(winner)

    def getTeamRecord(self, string):
        self.team_records[string]

    def getTeams(self):
        return [name for name in self.team_records.keys()]

    def getTeamHistory(self, team):
        return [game for game in self.games if team in game.getTeams()]
