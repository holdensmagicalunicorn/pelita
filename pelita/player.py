""" Base classes for player implementations. """

from pelita.universe import stop, Free
from collections import deque
import random


class AbstractPlayer(object):
    """ Base class for all user implemented Players. """

    def _set_index(self, index):
        """ Called by the GameMaster to set this Players index.

        Parameters
        ----------
        index : int
            this players index

        """
        self._index = index

    def _set_initial(self, universe):
        """ Called by the GameMaster on initialisation.

        Parameters
        ----------
        universe : Universe
            the initial state of the universe

        """
        self.universe_states = []
        self.universe_states.append(universe)
        self.set_initial()

    def set_initial(self):
        """ Subclasses can override this if desired. """
        pass

    def _get_move(self, universe):
        """ Called by the GameMaster to obtain next move.

        This will add the universe to the list of universe_states and then call
        `self.get_move()`.

        Parameters
        ----------
        universe : Universe
            the universe in its current state.

        """
        self.universe_states.append(universe)
        return self.get_move(universe)

    def get_move(self, universe):
        raise NotImplementedError(
                "You must override the 'get_move' method in your player")

    @property
    def current_uni(self):
        """ The current Universe.

        Returns
        -------
        universe : Universe
            the current Universe

        """
        return self.universe_states[-1]

    @property
    def me(self):
        """ The Bot object this Player controls.

        Returns
        -------
        me : Bot
            the bot controlled by this player

        """
        return self.current_uni.bots[self._index]

    @property
    def team_bots(self):
        """ A list of Bots that are on this players team.

        Returns
        -------
        team_mates : list of Bot objects
            the team mates

        """
        this_team = [self.current_uni.bots[i] for i in
            self.current_uni.teams[self._index].bots]
        this_team.pop(self._index)
        return this_team

    @property
    def enemy_food(self):
        return self.current_uni.enemy_food(self.me.team_index)

    @property
    def enemy_bots(self):
        """ A list of enemy Bots.

        Returns
        -------
        enemy_bots : list of Bot objects
            all Bots on all enemy teams
        """
        return self.current_uni.enemy_bots(self.me.team_index)

    @property
    def current_pos(self):
        """ The current position of this bot.

        Returns
        -------
        current_pos : tuple of (int, int)
            the current position (x, y) of this bot
        """
        return self.me.current_pos

    @property
    def initial_pos(self):
        """ The initial_pos of this bot.

        Returns
        -------
        initial_pos : tuple of (int, int)
            the initial position (x, y) of this bot

        """
        return self.me.initial_pos

class StoppingPlayer(AbstractPlayer):
    """ A Player that just stands still. """

    def get_move(self, universe):
        return stop


class RandomPlayer(AbstractPlayer):
    """ A player that makes moves at random. """

    def get_move(self, universe):
        legal_moves = universe.get_legal_moves(
                universe.bots[self._index].current_pos)
        return random.choice(legal_moves.keys())

class BFSPlayer(AbstractPlayer):
    """ This player uses breadth first search to always go to the closest food.

    This player uses an adjacency list [1] to store the topology of the
    maze. It will then do a breadth first search [2] to search for the
    closest food. When found, it will follow the determined path until it
    reaches the food. This continues until all food has been eaten or the
    enemy wins.

    [1] http://en.wikipedia.org/wiki/Adjacency_list
    [2] http://en.wikipedia.org/wiki/Breadth-first_search

    """
    @staticmethod
    def free_positions(maze):
        """ Get a list of all free positions in the Maze.

        Returns
        -------
        free_pos : list of tuples (int, int)
            all free positions in the Maze
        """
        free_pos = []
        for pos in maze.positions:
            if maze.has_at(Free, pos):
                free_pos.append(pos)
        return free_pos

    def set_initial(self):
        # Before the game starts we initialise our adjacency list.
        free_pos = self.free_positions(self.current_uni.maze)
        # Here we use a generator on a dictionary to create adjacency list.
        self.adjacency = dict((pos, self.current_uni.get_legal_moves(pos).values())
                for pos in free_pos)
        self.current_path = self.bfs_food()

    def bfs_food(self):
        """ Breadth first search for food.

        Returns
        -------
        path : a lits of tuples (int, int)
            The positions (x, y) in the path furthest to closest. The first
            element is the final destination.

        """
        # Initialise `to_visit` of type `deque` with current position.
        # We use a `deque` since we need to extend to the right
        # but pop from the left, i.e. its a fifo queue.
        to_visit = deque([self.current_pos])
        # `seen` is a list of nodes we have seen already
        # We append to right and later pop from right, so a list will do.
        # Order is important for the back-track later on, so don't use a set.
        seen = []
        while to_visit:
            current = to_visit.popleft()
            if current in seen:
                # This node has been seen, ignore it.
                continue
            elif current in self.enemy_food:
                # We found some food, break and back-track path.
                break
            else:
                # Otherwise keep going, i.e. add adjacent nodes to seen list.
                seen.append(current)
                to_visit.extend(self.adjacency[current])
        # Now back-track using seen to determine how we got here.
        # Initialise the path with current node, i.e. position of food.
        path = [current]
        while seen:
            # Pop the latest node in seen
            next_ = seen.pop()
            # If thats adjacent to the current node
            # its in the path
            if next_ in self.adjacency[current]:
                # So add it to the path
                path.append(next_)
                # And continue back-tracking from there
                current = next_
        # The last element is the current position, we don't need that in our
        # path, so don't include it.
        return path[:-1]

    @staticmethod
    def pos_diff(pos1, pos2):
        # TODO assert for adjacency
        return (pos2[0]-pos1[0], pos2[1]-pos1[1])

    def get_move(self, universe):
        if not self.current_path:
            self.current_path = self.bfs_food()
        new_pos = self.current_path.pop()
        return self.pos_diff(self.current_pos, new_pos)