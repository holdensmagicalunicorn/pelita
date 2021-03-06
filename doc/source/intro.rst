======================
Introduction to Pelita
======================

Autonomous agent environment in Python

Glossary
========

:``Universe``:
    The game state.

:``Bot``:
    The datastructure used to store the agent.

:``Team``:
    In capture-the-flag each ``Bot`` belongs to a ``Team``.

:``Player``:
    Your implementation of the *intelligence* for a ``Bot``.

:``Mesh``:
    A two-dimensional container mapping a position tuple to an object.

:``Maze``:
    Datastructure that stores the maze.

:``MazeComponent``:
    Objects stored in the ``Maze``.

:``GameMaster``:
    Controller object that asks players for moves and updates the ``Universe``.

:``Move``:
    A tuple that indicates where a ``Bot`` should move.

The connections are as follows: A ``Universe`` contains a list of ``Bot``
objects, a list of ``Team`` objects and a ``Maze`` object. The ``Maze`` object
is implemented with a ``Mesh`` where a list of ``MazeComponent`` objects such as
``Free``, ``Wall`` and ``Food`` are store at each position.  A ``Player``
implements/controls the logic required to navigate a ``Bot``. The ``GameMaster``
will forward the current state of the ``Universe`` to the ``Player`` and request
a ``Move`` in return. Upon receipt of the next ``Move`` the ``GameMaster`` will
update the ``Universe``.

Writing a Player
================

In order to write a Player you should subclass from
``pelita.player.AbstractPlayer``. This is an abstract class which provides several
convenience methods to interrogate the Universe including the Bot instance that this
player controls but lacks the functions to actually control the Bot. In order to
make your Player do something useful you must implement at least the method
``get_move(self)`` to return a move. This can be one of::

    north = (0, -1)
    south = (0, 1)
    west  = (-1, 0)
    east  = (1, 0)
    stop  = (0, 0)

The moves are provided by the ``datamodel``, import them with::

    from pelita.datamodel import north, south, west, east, stop

An example of such a player is the trivial ``StoppingPlayer`` which simply returns
``stop``:

.. literalinclude:: ../../pelita/player.py
   :pyobject: StoppingPlayer

A slightly more useful example is the ``RandomPlayer`` which always selects a move
at random from the possible moves:

.. literalinclude:: ../../pelita/player.py
   :pyobject: RandomPlayer

Here we can see the first convenience method: ``legal_moves`` which returns a
dictionary mapping move tuples to position tuples. The random player simply
selects a move at random from the keys (moves) of this dictionary and then moves
there. ``legal_moves`` always includes stop.

The next example if the not-quite random Player ``NQRandomPlayer``. This ones
does not move back to the position where it was on its last turn and does not
ever stop in place:


.. literalinclude:: ../../pelita/player.py
   :pyobject: NQRandomPlayer

Here we can see the use of another convenience method: ``previous_pos`` which
gives the position the Bot had in the previous round. Lets take a closer look at
how this is implemented:

.. literalinclude:: ../../pelita/player.py
   :pyobject: AbstractPlayer.previous_pos

Importantly we see that the ``AbstractPlayer`` automatically maintains a stack of
previous states of the Universe called ``universe_states``. Here we look at the
previous state and obtain the bots positions. The Universe maintains a list of
Bots ``bots`` and each Player has an attribute ``_index`` which can be used to
obtain the respective Bot instance controlled by the Player. Lastly we simply
look at the ``current_pos`` property of the Bot to obtain the previous position.

A somewhat more elaborate example is the ``BFSPlayer`` which uses breadth first
search to find food:

.. literalinclude:: ../../pelita/player.py
   :pyobject: BFSPlayer

Here we can already see some more advanced concepts. The first thing to note is
that any player can override the method ``set_initial(self)`` where ``current_uni``
is the starting state of the game. All food is still present and all Bots are at
their initial position. In this method we initialise the adjacency list
representation of the maze. Lets look as the implementation of ``current_uni``:



.. literalinclude:: ../../pelita/player.py
   :pyobject: AbstractPlayer.current_uni

As we can see its simply the top element on the ``universe_states`` stack
mentioned earlier. In order to obtain the positions of all ``Free`` the Universe
provides a method ``pos_of(maze_component)`` which will return the positions of
all ``MazeComponent`` type objects. We then use the method
``get_legal_moves(self,pos)`` for each of the free positions to build the
adjacency list.

The breadth-first search is implemented in the method ``bfs_food`` which returns a
path to closest food element. In this method we see some more convenience, for
example ``enemy_food`` which returns a list of all food that we can eat. One of
the convenience properties used here is ``current_pos`` which returns the
current position. Let have a look at this:

.. literalinclude:: ../../pelita/player.py
   :pyobject: AbstractPlayer.current_pos

We see that this makes use of the ``me`` property which is defined as follows:

.. literalinclude:: ../../pelita/player.py
   :pyobject: AbstractPlayer.me

As you can see ``me`` will simply obtain the Bot instance controlled by this
player from the current universe using the hidden ``_index`` attribute of the
Player. In practice you should be able to avoid having to use the
``_index`` directly but its good to know how this is implemented in case you
wish to do something exotic.

As a defensive example we have the ``BasicDefensePlayer``:

.. literalinclude:: ../../pelita/player.py
   :pyobject: BasicDefensePlayer

All example Players can be found in the module ``pelita.player``.

Below is the complete code for the ``AbstractPlayer`` which shows you all of the
convenience methods/properties and also some of the implementation details:

.. literalinclude:: ../../pelita/player.py
   :pyobject: AbstractPlayer

Git-Repository
==============

The official Git-Repository is hosted at Github:
`https://github.com/Debilski/pelita <https://github.com/Debilski/pelita>`_

You can create a clone with::

    $ git clone git://github.com/Debilski/pelita.git

Project-Wall
============

We used an agile project wall to track tasks for the initial stages of the
development. In our case we split it into four distinct sections: ``todo``
(upper right), ``current iteration`` (upper left), ``done`` (lower left) and
``nice to have`` (lower right). Since we only had one whiteboard we kept the
center for sketches and doodles.  You can read about the agile project wall in
the book: `The Agile Samurai
<http://pragprog.com/book/jtrap/the-agile-samurai>`_ by by Jonathan Rasmusson

Here are some photos:


.. figure:: images/project_wall_full.jpg
   :width: 820px
   :alt: the whole wall

   The whole wall


.. figure:: images/project_wall_todo.jpg
   :width: 640px
   :alt: The 'todo' section

   The 'todo' section

.. figure:: images/project_wall_current.jpg
   :width: 640px
   :alt: the 'current' section

   The 'current' section

.. figure:: images/project_wall_done.jpg
   :width: 640px
   :alt: the done section

   The 'done' section

.. figure:: images/project_wall_nice.jpg
   :width: 640px
   :alt: the nice to have section

   The 'nice to have' section
