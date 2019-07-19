from tournament import Tournament
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

    tourny = Tournament(teamNames)
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
    while True:
        games = tourny.currentGames()
        ch = stdscr.getch()
        if (ch == 10 and index == len(i)): # finish round
            break
        if (ch == curses.KEY_DOWN):
            index += 1
        elif (ch == curses.KEY_UP):
            index -= 1
        # TODO: enter to edit
        index = max(index, 0)
        index = min(index, len(tourny.currentGames()))

        # draw
        for i, game in enumerate(games):
            t1, t2 = game.teams()
            score = game.score() #int, int
            DISPLAYLENGTH = 10
            SCORELENGTH = 6
            stdscr.addstr(j+1, 0, t1[:DISPLAYLENGTH])
            stdscr.addstr(j+1, 1+DISPLAYLENGTH, score)
            stdscr.addstr(j+1, 1+DISPLAYLENGTH+SCORELENGTH, t2[:DISPLAYLENGTH])
        # TODO: maybe a button with "finish round"
        stdscr.getch()
        break

def main(stdscr):
    tourny = createTournament(stdscr)
    viewRound(stdscr, tourny)

wrapper(main)
