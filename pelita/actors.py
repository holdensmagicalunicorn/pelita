# -*- coding: utf-8 -*-

import sys
import Queue

from pelita.messaging import DispatchingActor, expose, actor_registry, actor_of, RemoteConnection, DeadConnection

from pelita.game_master import GameMaster, PlayerTimeout, PlayerDisconnected

import logging

_logger = logging.getLogger("pelita")
_logger.setLevel(logging.DEBUG)

TIMEOUT = 3

class _ClientActor(DispatchingActor):
    def on_start(self):
        self.team = None
        self.server_actor = None

    @expose
    def register_team(self, message, team):
        """ We register the team.
        """
        # TODO: Maybe throw an exception, if a team
        # is already registered.
        # Also: investigate how to deal with concurrency issues
        self.team = team

    @expose
    def say_hello(self, message, main_actor, team_name, host, port):
        """ Opens a connection to the remote main_actor,
        and sends it a "hello" message with the given team_name.
        """

        self.server_actor = RemoteConnection().actor_for(main_actor, host, port)

        # self.server_actor = actor_registry.get_by_name(main_actor)
        if not self.server_actor:
            _logger.warning("Actor %r not found." % main_actor)
            return

        if self.server_actor.query("hello", [team_name, self.ref.uuid]).get() == "ok":
            _logger.info("Connection accepted")
            self.ref.reply("ok")

    @expose
    def set_bot_ids(self, message, *bot_ids):
        """ Called by the server. This method sets the available bot_ids for this team.
        """
        self.ref.reply(self.team._set_bot_ids(bot_ids))

    @expose
    def set_initial(self, message, universe):
        """ Called by the server. This method tells us the initial universe.
        """
        self.ref.reply(self.team._set_initial(universe))

    @expose
    def play_now(self, message, bot_index, universe):
        """ Called by the server. This message requests a new move
        from the bot with index `bot_index`.
        """
        move = self.team._get_move(bot_index, universe)
        self.ref.reply(move)


class ClientActor(object):
    def __init__(self, team_name):
        self.team_name = team_name

        self.actor_ref = actor_of(_ClientActor)
        self.actor_ref._actor.thread.daemon = True # TODO remove this line
        self.actor_ref.start()

    def register_team(self, team):
        """ Registers a team with our local actor.
        """
        self.actor_ref.notify("register_team", [team])

    def connect(self, main_actor, host="", port=50007):
        """ Tells our local actor to establish a connection with `main_actor`.
        """
        print "Trying to establish a connection with remote actor '%s'..." % main_actor,
        sys.stdout.flush()

        try:
            print self.actor_ref.query("say_hello", [main_actor, self.team_name, host, port]).get(TIMEOUT)
        except Queue.Empty:
            print "failed."


class RemoteTeamPlayer(object):
    def __init__(self, reference):
        self.ref = reference

    def _set_bot_ids(self, bot_ids):
        return self.ref.query("set_bot_ids", bot_ids).get(TIMEOUT)

    def _set_initial(self, universe):
        return self.ref.query("set_initial", [universe]).get(TIMEOUT)

    def _get_move(self, bot_idx, universe):
        try:
            result = self.ref.query("play_now", [bot_idx, universe]).get(TIMEOUT)
            return tuple(result)
        except TypeError:
            # if we could not convert into a tuple (e.g. bad reply)
            return None
        except Queue.Empty:
            # if we did not receive a message in time
            raise PlayerTimeout()
        except DeadConnection:
            # if the remote connection is closed
            raise PlayerDisconnected()

class ServerActor(DispatchingActor):
    def on_start(self):
        self.teams = []
        self.team_names = []
        self.game_master = None

    @expose
    def initialize_game(self, message, layout, number_bots, game_time):
        self.game_master = GameMaster(layout, number_bots, game_time)

    @expose
    def hello(self, message, team_name, actor_uuid):
        _logger.info("Received 'hello' from '%s'." % team_name)

        if self.ref.remote:
            other_ref = self.ref.remote.create_proxy(actor_uuid)
        else:
            other_ref = actor_registry.get_by_uuid(actor_uuid)

        self.teams.append(other_ref)
        self.team_names.append(team_name)
        self.ref.reply("ok")

        if len(self.teams) == 2:
            _logger.info("Two players are available. Starting a game.")

            self.ref.notify("start_game")

    @expose
    def register_viewer(self, message, viewer):
        self.game_master.register_viewer(viewer)

    @expose
    def start_game(self, message):
        for team_idx in range(len(self.teams)):
            team_ref = self.teams[team_idx]
            team_name = self.team_names[team_idx]

            remote_player = RemoteTeamPlayer(team_ref)

            self.game_master.register_team(remote_player)

            # hack which sets the name in the universe
            self.game_master.universe.teams[team_idx].name = team_name

        self.game_master.play()