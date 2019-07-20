import sys
import curses
import curses.ascii

from tournament import Tournament
from tests import DummyRoundGenerator

"""
States:
    Creating a new tournament
    * Input list of players
    Running a game
    * Displays currently active games
    * Arrow keys to select a game, left-right to mark a winner? (for no game scores)
    * Enter on a game: input Score1-Score2
"""

class ExitInProgressTournament(Exception):
    pass

class Interface():
    def __init__(self, stdscr, tournament = None):
        self.stdscr = stdscr
        self.tournament = tournament

    def run(self):
        if self.tournament is None:
            self.tournament = self.createTournament()
        try:
            while True: # while not complete
                self.viewRound()
                self.tournament.startNextRound()
        except ExitInProgressTournament:
            pass

    def drawMaybeHighlightedLine(self, highlighted_index, y, string, formatting=0):
        if highlighted_index == y:
            formatting = formatting | curses.A_REVERSE

        self.stdscr.addstr(y, 0, string, formatting)

    def createTournament(self):
        """
        Input a list of players
        ENTER: input new player
        enter twice: create tourny

        TODO: prevent duplicate team names
        """
        teamNames = [""]
        i = 0

        def noDuplicateTeams():
            return len(set(teamNames)) == len(teamNames)
        def redrawScreen():
            for j, name in enumerate(teamNames):
                self.drawMaybeHighlightedLine(i, j+1, name)
            if teamNames[i] == "":
                if noDuplicateTeams():
                    self.stdscr.addstr(j+1, 1, "Input a team name or press ENTER to create tournament")
                else:
                    self.stdscr.addstr(j+1, 1, "Please change duplicate team name")

        while True:
            ch = self.stdscr.getch()
            self.stdscr.clear()
            self.stdscr.addstr(10, 10, str(ch))
            if (ch == 10 or ch == curses.KEY_DOWN): # newline/enter
                # if previous team is null, we're done entering
                if teamNames[i] == "" and noDuplicateTeams():
                    break
                i += 1
                if len(teamNames) <= i:
                    teamNames.append("")
            elif ch == curses.KEY_UP:
                i = max(0, i-1)
            elif (ch == 263): # backspace
                teamNames[i] = teamNames[i][:-1] if teamNames[i] else ""
            else:
                teamNames[i] += chr(ch)
            redrawScreen()

        tourny = Tournament(teamNames, DummyRoundGenerator())
        return tourny

    def viewTournament(stdscr):
        """
        Controls:
            asdf
        """
        pass

    def viewRound(self):
        """
        Displays a list of games. Press "UP" and "DOWN" to navigate.
        Controls:
        * up-down arrows to select a row
        * ENTER to edit the game record
        * left-right arrows as a shortcut for 0-1 or 1-0

        TODO: Filter games by team name
        """
        selected_index = 0
        tourny = self.tournament
        
        SCORE_LENGTH = 7
        DISPLAY_LENGTH = max(map(len, tourny.getTeams())) + 3

        def redrawScreen():
            game_ids = tourny.currentRound()
            for i, game_id in enumerate(game_ids):
                game = tourny.getGame(game_id)
                t1, t2 = game.getTeams()
                score = game.score # (int, int)
                line = ""
                line += t1[:DISPLAY_LENGTH].ljust(DISPLAY_LENGTH)
                if score:
                    line += "-".join(map(str, score)).ljust(SCORE_LENGTH)
                else:
                    line += "".ljust(SCORE_LENGTH)
                line += t2[:DISPLAY_LENGTH].ljust(DISPLAY_LENGTH)
                formatting = curses.A_BOLD if score is not None else 0
                self.drawMaybeHighlightedLine(selected_index, i, line, formatting)
            self.drawMaybeHighlightedLine(selected_index, len(game_ids), "FINISH ROUND", curses.A_BOLD if tourny.roundCompleted() else 0)

        while True:
            redrawScreen()
            game_ids = tourny.currentRound()
            ch = self.stdscr.getch()

            if ch == 10 and selected_index == len(game_ids) and tourny.roundCompleted():
                # Finish round
                break

            if ch == curses.KEY_DOWN or ch == ord("j"):
                selected_index += 1
            elif ch == curses.KEY_UP or ch == ord("k"):
                selected_index -= 1
            elif ch == curses.KEY_LEFT and selected_index < len(game_ids):
                tourny.setScore(game_ids[selected_index], (1, 0))
            elif ch == curses.KEY_RIGHT and selected_index < len(game_ids):
                tourny.setScore(game_ids[selected_index], (0, 1))
            elif ch == 10 and selected_index < len(game_ids): # enter
                while True:
                    self.stdscr.standout()
                    newscore = self.stdscr.addstr(selected_index, DISPLAY_LENGTH, " "*SCORE_LENGTH)
                    curses.echo()
                    newscore = self.stdscr.getstr(selected_index, DISPLAY_LENGTH, 10)
                    curses.noecho()
                    self.stdscr.standend()
                    try:
                        arr = newscore.split(b" ")
                        if len(arr) == 1:
                            arr = newscore.split(b"-")
                        a, b = arr
                        tourny.setScore(game_ids[selected_index], (int(a), int(b)))
                        break
                    except ValueError:
                        pass # THERE IS NO ESCAPE
            elif ch == curses.ascii.ctrl("s"):
                # save
                if self.saveDialog():
                    return


            selected_index = max(selected_index, 0)
            selected_index = min(selected_index, len(tourny.currentRound()))

    def saveDialog(self):
        self.stdscr.clear()
        filename = ""
        while filename != "":
            self.stdscr.addstr(0, 0, "Enter save file name:")
            filename = self.stdscr.getstr(1, 0, 20)
        # TODO: save to filename

def main(stdscr):
    tourny = None
    if len(sys.argv) > 1:
        tourny = None # TODO: unpickle

    interface = Interface(stdscr, tourny)
    interface.run()

curses.wrapper(main)
