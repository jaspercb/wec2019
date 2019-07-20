from tournament import Tournament
from tests import DummyRoundGenerator
from curses import wrapper
import curses


"""
States:
    Creating a new tournament
    * Input list of players
    Running a game
    * Displays currently active games
    * Arrow keys to select a game, left-right to mark a winner? (for no game scores)
    * Enter on a game: input Score1-Score2
"""

# Mode enums
MODE_CREATING_GAME = 37

def createTournament(stdscr):
    """
    Input a list of players
    ENTER: input new player
    enter twice: create tourny

    TODO: ability to update old teams
    TODO: prevent duplicate team names
    """
    teamNames = [""]
    i = 0
    while True:
        ch = stdscr.getch()
        stdscr.clear()
        stdscr.addstr(10, 10, str(ch))
        if (ch == 10 or ch == curses.KEY_DOWN): # newline/enter
            # if previous team is null, we're done entering
            if(teamNames[i]) == "":
                break
            i += 1
            if len(teamNames) <= i:
                teamNames.append("")
        elif ch == curses.KEY_UP:
            i = max(0, index-1)
        elif (ch == 263): # backspace
            teamNames[i] = teamNames[i][:-1] if teamNames[i] else ""
        else:
            teamNames[i] += chr(ch)
        # draw team names
        for j, name in enumerate(teamNames):
            stdscr.addstr(j+1, 1, "-" + name)
        if teamNames[i] == "":
            stdscr.addstr(j+1, 1, "Input a team name or press ENTER to create tourny")

    tourny = Tournament(teamNames, DummyRoundGenerator())
    return tourny

def viewTournament(stdscr):
    """
    Controls:
        asdf
    """
    pass

def viewRound(stdscr, tourny):
    """
    Displays a list of games. Press "UP" and "DOWN" to navigate.
    Controls:
    * up-down arrows to select a row
    * ENTER to edit the game record
    * left-right arrows as a shortcut for 0-1 or 1-0

    TODO: Filter games by team name
    """
    index = 0
    def drawMaybeHighlightedLine(y, string):
        # Intent: highlight selected line
        if index == y:
            stdscr.standout()

        stdscr.addstr(y, 0, string)

        if index == y:
            stdscr.standend()

    DISPLAY_LENGTH = 10
    SCORE_LENGTH = 7
    def redrawScreen():
        game_ids = tourny.currentRound()
        for i, game_id in enumerate(game_ids):
            game = tourny.getGame(game_id)
            t1, t2 = game.getTeams()
            try:
                score = game.score # (int, int)
            except: # TODO: this is for testing only, remove once stub exists
                score = (1, 2)
            line = ""
            line += t1[:DISPLAY_LENGTH].rjust(DISPLAY_LENGTH)
            line += "-".join(map(str, score)).rjust(SCORE_LENGTH)
            line += t2[:DISPLAY_LENGTH].rjust(DISPLAY_LENGTH)
            drawMaybeHighlightedLine(i, line)
        # TODO: maybe a button with "finish round"
        stdscr.addstr(i+2, 0, "FINISH ROUND")

    while True:
        redrawScreen()
        game_ids = tourny.currentRound()
        ch = stdscr.getch()
        if ch == 10 and index == len(game_ids): # finish round
            break

        if ch == curses.KEY_DOWN:
            index += 1
        elif ch == curses.KEY_UP:
            index -= 1
        elif ch == curses.KEY_LEFT and index < len(game_ids):
            tourny.setScore(game_ids[index], (1, 0))
        elif ch == curses.KEY_RIGHT and index < len(game_ids):
            tourny.setScore(game_ids[index], (0, 1))
        elif ch == 10: # enter
            while True:
                curses.echo()
                newscore = stdscr.getstr(index, DISPLAY_LENGTH + 1, 10) # y, x, length-of-string
                curses.noecho()
                try:
                    arr = newscore.split(b" ")
                    if len(arr) == 1:
                        arr = newscore.split(b"-")
                    a, b = arr
                    tourny.setScore(game_ids[index], (int(a), int(b)))
                    break
                except ValueError:
                    pass # THERE IS NO ESCAPE


                
        index = max(index, 0)
        index = min(index, len(tourny.currentRound()))

def main(stdscr):
    tourny = createTournament(stdscr)
    viewRound(stdscr, tourny)

wrapper(main)
