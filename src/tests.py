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
    return len(tourney.currentRound()) > 0


def test_record_past_rounds():
    tourney = Tournament(['a', 'b', 'c', 'd', 'e'], DummyRoundGenerator())
    tourney.startNextRound()
    tourney.startNextRound()

    past_rounds = tourney.pastRounds()

    # expects 2 nonempty past rounds with all unique game ids
    return len(past_rounds) == 2 \
        and len(past_rounds[0]) > 0\
        and len(past_rounds[1]) > 0 \
        and len(set(past_rounds[0]) & set(past_rounds[1])) == 0


if __name__ == '__main__':
    tests = [
        test_tournament_init,
        test_record_past_rounds,
    ]

    for test in tests:
        print(test())
