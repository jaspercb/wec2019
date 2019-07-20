from game import Game
from tournament import Tournament
from roundgen import SingleEliminationGenerator


class DummyRoundGenerator(object):
    def __init__(self):
        pass

    def generateRound(self, tournament):
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


def test_round_completion():
    result = True

    tourney = Tournament(
        ['a', 'b', 'c', 'd', 'e'], SingleEliminationGenerator())

    # round should be 3 byes and 1 match between d and e

    result = result and not tourney.roundCompleted()

    tourney.setScore(1, (1, 0))

    result = result and tourney.roundCompleted()

    return result


def test_multiple_rounds():
    result = True

    tourney = Tournament(
        ['a', 'b'], SingleEliminationGenerator(), num_matches=3)
    tourney.setScore(0, (1, 0), 0)

    result = result and not tourney.roundCompleted()

    tourney.setScore(0, (1, 0), 1)

    result = result and tourney.roundCompleted()

    return result


if __name__ == '__main__':
    tests = [
        test_tournament_init,
        test_record_past_rounds,
        test_round_completion,
        test_multiple_rounds,
    ]

    for test in tests:
        print(test())
