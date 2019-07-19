from game import Game
from tournament import Tournament


class DummyRoundGenerator(object):
    def __init__(self):
        pass

    def generateGames(self, tournament):
        teams = tournament.getTeams()
        if len(teams) < 2:
            return []

        return [Game(team1, team2) for team1, team2
                in zip(teams, teams[1:] + [teams[0]])]


def test_tournament_init():
    tourney = Tournament(['a', 'b', 'c', 'd', 'e'], DummyRoundGenerator())
    print(tourney.currentGames())


if __name__ == '__main__':
    test_tournament_init()
