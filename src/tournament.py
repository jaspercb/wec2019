from collections import OrderedDict


class Tournament(object):
    def __init__(self, teams, round_generator):
        self.round_generator = round_generator
        self.next_game_id = 0

        # win/loss record for each team, ordered by original seed
        self.team_records = OrderedDict([(team, (0, 0)) for team in teams])

        # stores games in consistent "scheduled order"
        # (games in a round may be played out of order)
        self.current_round = OrderedDict()

        # will store past values of current_round
        self.past_rounds = []

        # set of gameids representing unplayed games in the current round
        self.unplayed_games = set()

        self.startNextRound()

    # will not verify that all games in past round were played
    def startNextRound(self):
        if len(self.current_round) > 0:
            self.past_rounds.append(self.current_round)

        self.current_round = OrderedDict()
        for game in self.round_generator.generateGames(self):
            self.current_round[self.next_game_id] = game
            self.next_game_id += 1

        self.unplayed_games = set(self.currentRound())

    # past rounds
    def currentRound(self):
        return list(self.current_round.keys())

    def getGame(self, gameid):
        if gameid in self.current_round.keys():
            return self.current_round[gameid]
        elif gameid in self.past_rounds.keys():
            return self.past_rounds[gameid]
        raise KeyError()

    # |score| is a tuple (team1_score, team2_score)
    def setScore(self, gameid, score):
        self.current_round[gameid].score = score

        try:
            self.unplayed_games.remove(gameid)
        except KeyError:
            pass
        else:
            self.past_rounds.append(gameid)

    def getTeamRecord(self, string):
        self.team_records[string]

    def getTeams(self):
        return list(self.team_records.keys())

    def getTeamHistory(self, team):
        return [game for game in self.games if team in game.getTeams()]
