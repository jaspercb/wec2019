import sys
import curses
import curses.ascii

import roundgen
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

Required TODOs:
    * scrolling behavior?
"""

class ExitInProgressTournament(Exception):
    pass

class Interface():
    def __init__(self, stdscr, tournament = None):
        self.stdscr = stdscr
        self.stdscr.scrollok(True)
        self.tournament = tournament
        self.scroll = 0

    def run(self):
        if self.tournament is None:
            self.tournament = self.createTournament()
        try:
            while True: # while not complete
                self.viewRound()
                self.tournament.startNextRound()
                if self.tournament.currentRound() is None:
                    break
            # TODO: print results
        except ExitInProgressTournament:
            pass

    def addstr(self, y, x, string, formatting=0):
        # if offscreen, do not render
        yi = y - self.scroll
        if yi < 0:
            return
        maxy, maxx = self.stdscr.getmaxyx()
        if yi >= maxy:
            return
        self.stdscr.addstr(yi, x, string, formatting)

    def drawMaybeHighlightedLine(self, highlighted_index, y, string, formatting=0):
        if highlighted_index == y:
            formatting = formatting | curses.A_REVERSE

        self.addstr(y, 0, string, formatting)

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

        def howManyTeams():
            return len([name for name in teamNames if len(name)])

        def canCreateTournament():
            return noDuplicateTeams() and howManyTeams() >= 2

        def redrawScreen():
            for j, name in enumerate(teamNames):
                self.drawMaybeHighlightedLine(i, j, name, curses.A_BOLD)
            if teamNames[i] == "":
                line = ""
                formatting = 0
                if canCreateTournament():
                    line = "Start typing another team name or press ENTER to create tournament"
                    formatting = curses.A_BOLD
                elif not noDuplicateTeams():
                    line = "Please change duplicate team name"
                elif howManyTeams() == 0:
                    line = "Start typing a team name"
                elif howManyTeams() <= 1:
                    line = "Start typing another team name"
                self.addstr(j, 3, line, formatting)
                self.addstr(j, 0, "", formatting)

        while True:
            redrawScreen()
            ch = self.stdscr.getch()
            self.stdscr.clear()
            if (ch == 10 or ch == curses.KEY_DOWN): # newline/enter
                # if previous team is null, we're done entering
                if teamNames[i] == "" and canCreateTournament():
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

        round_generator = None
        while round_generator is None:
            msg = "Which bracket type? (double, single) "
            self.addstr(0, 0, msg)
            self.addstr(0, len(msg), " "*10)
            curses.echo()
            mode = str(self.stdscr.getstr(0, len(msg), 10))[2:-1]
            curses.noecho()
            if mode in ["single", "double", "roundrobin"]:
                round_generator = roundgen.getGenerator(mode)
                break

        bestofn = None
        while bestofn is None:
            msg = "Matches per game (odd number): "
            self.addstr(1, 0, msg)
            self.addstr(1, len(msg), " "*3)

            try:
                curses.echo()
                bestofn = int(self.stdscr.getstr(1, len(msg), 3))
                curses.noecho()
                if bestofn % 2 == 0:
                    bestofn = None
            except ValueError:
                pass

        teamNames = [str(i) for i in range(1000)]
        tourny = Tournament(teamNames[:-1], round_generator, bestofn)

        return tourny

    def viewRound(self):
        """
        Displays a list of games. Press "UP" and "DOWN" to navigate.
        Controls:
        * up-down arrows to select a row
        * ENTER to edit the game record
        * left-right arrows as a shortcut for 0-1 or 1-0

        Neat possible feature: Filter games by team name
        """
        self.scroll = 0
        selected_index = 0
        tourny = self.tournament

        SCORE_LENGTH = 7
        DISPLAY_LENGTH = max(map(len, tourny.getTeams())) + 3

        backmap = {}
        # map from row -> (game_id, nth game)
        def updateBackmap():
            backmap.clear()
            row = 0
            for game_id in tourny.currentRound():
                game = tourny.getGame(game_id)
                lim = game.gamesPlayed() + game.minimumGamesLeft()
                for i, score in enumerate(game.scores[:lim]):
                    backmap[row] = (game_id, i)
                    row += 1

        def redrawScreen():
            updateBackmap()
            self.stdscr.clear()
            for row in backmap:
                game_id, n = backmap[row]
                game = tourny.getGame(game_id)
                t1, t2 = game.getTeams()
                score = game.scores[n] # (int, int)
                line = ""
                if n == 0 and t1:
                    line += t1[:DISPLAY_LENGTH].ljust(DISPLAY_LENGTH)
                else:
                    line += " " * DISPLAY_LENGTH
                if score:
                    line += "-".join(map(str, score)).ljust(SCORE_LENGTH)
                else:
                    line += "".ljust(SCORE_LENGTH)
                if n == 0 and t2:
                    line += t2[:DISPLAY_LENGTH].ljust(DISPLAY_LENGTH)
                else:
                    line += " " * DISPLAY_LENGTH
                formatting = curses.A_BOLD if game.isComplete() else 0
                self.drawMaybeHighlightedLine(selected_index, row, line, formatting)
            self.drawMaybeHighlightedLine(selected_index, len(backmap), "FINISH ROUND", curses.A_BOLD if tourny.roundCompleted() else 0)
            self.addstr(len(backmap)+1, 0, "'s' to save, 'q' to quit")

        while True:
            redrawScreen()
            game_ids = tourny.currentRound()
            ch = self.stdscr.getch()

            if ch == 10 and selected_index == len(backmap) and tourny.roundCompleted():
                # Finish round
                break

            if ch == curses.KEY_DOWN or ch == ord("j"):
                selected_index += 1
                if selected_index - self.scroll > 10:
                    self.scroll += 1
            elif ch == curses.KEY_UP or ch == ord("k"):
                selected_index -= 1
                if selected_index - self.scroll < 0:
                    self.scroll -= 1
            elif ch == curses.KEY_LEFT and selected_index < len(backmap):
                game_id, n = backmap[selected_index]
                tourny.setScore(game_id, (1, 0), n)
            elif ch == curses.KEY_RIGHT and selected_index < len(backmap):
                game_id, n = backmap[selected_index]
                tourny.setScore(game_id, (0, 1), n)
            elif ch == 10 and selected_index < len(backmap): # enter
                while True:
                    self.stdscr.standout()
                    newscore = self.addstr(selected_index, DISPLAY_LENGTH, " "*SCORE_LENGTH)
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
            elif ch == ord("s"):
                # save
                if self.saveDialog(tourny):
                    raise ExitInProgressTournament()

            elif ch == ord("q"):
                # exit
                raise ExitInProgressTournament()


            selected_index = max(selected_index, 0)
            selected_index = min(selected_index, len(backmap))

    def saveDialog(self, tourny):
        self.stdscr.clear()
        filename = ""
        while filename == "":
            msg = "Enter save file name: "
            self.addstr(0, 0, msg)
            curses.echo()
            filename = self.stdscr.getstr(0, len(msg), 20)
            curses.noecho()
        tourny.saveToFile(filename)
        return True

def main(stdscr):
    tourny = None
    if len(sys.argv) > 1:
        tourny = Tournament.fromFile(sys.argv[1])

    interface = Interface(stdscr, tourny)
    interface.run()

curses.wrapper(main)
