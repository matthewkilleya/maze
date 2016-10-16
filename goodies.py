'''
    goodies.py

    Definitions for some example goodies
'''

import collections
import random

from maze import Baddy, DOWN, Goody, LEFT, PING, Position, RIGHT, STAY, UP, ZERO

class StaticGoody(Goody):
    ''' A static goody - does not move from its initial position '''

    def take_turn(self, _obstruction, _ping_response):
        ''' Stay where we are '''
        return STAY

class RandomGoody(Goody):
    ''' A random-walking goody '''

    def take_turn(self, obstruction, _ping_response):
        ''' Ignore any ping information, just choose a random direction to walk in, or ping '''
        possibilities = filter(lambda direction: not obstruction[direction], [UP, DOWN, LEFT, RIGHT]) + [PING]
        return random.choice(possibilities)

def move_to_location(move):
    ''' This maps a 'move' label to an x and y increment. '''
    mapper = {
        STAY  : ZERO,
        LEFT  : Position(-1, 0),
        RIGHT : Position(1, 0),
        UP    : Position(0, 1),
        DOWN  : Position(0, -1)}
    return mapper[move]

def distance(position1, position2):
    ''' Find distance between two points '''
    return (abs(position1.x - position2.x) +  abs(position1.y - position2.y))

class MattGoody(Goody):
    ''' Matt is a goody '''



    def __init__(self):
        super(MattGoody, self).__init__()

        self.location = ZERO
        self.previous_locations = collections.deque(maxlen=10)

        self.dead_ends = []
        self.ping = None
        self.ping_age = 0

    def take_turn(self, obstruction, _ping_response):
        ''' Ping first time. After that try and minimize distance to ping '''

        # Makes sense to store location and pings as absolutes, as there can be a lot moves in between pings .

        # We ping first time if no one has (or if we haven't seen a new ping for 5 turns)
        if (self.ping is None and _ping_response is None) or self.ping_age > 5:
            self.ping_age = 0  # reset
            return PING
        elif _ping_response is not None:  # otherwise update if there is a new ping #
            self.ping  = dict((key, value + self.location)
                            for key, value in _ping_response.iteritems())
            self.ping_age = 0  # reset

        # We don't know how ping_response will be keyed as not sure what type of goody.
        goody_key = [key for key in self.ping.keys() if isinstance(key, Goody)][0]
        goody_ping = self.ping[goody_key]

        baddy_key = [key for key in self.ping.keys() if isinstance(key, Baddy)][0]
        baddy_ping = self.ping[baddy_key]

        possibilities = filter(lambda direction: not obstruction[direction], [UP, DOWN, LEFT, RIGHT])

        # Store dead ends so we don't go into them again.
        if len(possibilities) == 1:
            self.dead_ends.append(self.location)

        # Evade/run away if baddy close.
        if distance(self.location, baddy_ping) <= 3:
            possibilities.append(STAY)
            distances = [distance(self.location + move_to_location(possibility), baddy_ping)
                          for possibility in possibilities]
            return possibilities[distances.index(max(distances))]

        # We are the target location (location of last ping). Need to ping - they must have moved.
        if distance(goody_ping, self.location) < 1:
            return PING

        # Calc distance to goody of all possibilities.
        distances = [distance(self.location + move_to_location(possibility), goody_ping)
                      for possibility in possibilities]
        # Return moves which minimizes distance to last known location of goody.
        move = possibilities[distances.index(min(distances))]
        move_to_loc = move_to_location(move)

        # If been here before (recently as 'deque'), or moving to a dead end do random move instead.
        new_location = self.location + move_to_loc
        if new_location in self.previous_locations or new_location in self.dead_ends:
            move = random.choice(possibilities)
            new_location =  self.location + move_to_location(move)

        self.previous_locations.append(self.location)
        self.location = new_location
        self.ping_age += 1

        return move
