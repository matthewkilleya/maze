'''
    goodies.py

    Definitions for some example goodies
'''

import random

from maze import Goody, UP, DOWN, LEFT, RIGHT, STAY, PING, ZERO, Position

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
        self.previous_locations = [ZERO]
        self.ping = None

    def take_turn(self, obstruction, _ping_response):
        ''' Ping first time. After that try and minimize distance to ping '''

        # Makes sense to store location and pings as absolutes, as there can be a lot moves in between pings .

        # We ping first time if no one has #
        if self.ping is None and _ping_response is None:
            return PING
        elif _ping_response is not None:  # otherwise update if there is a new ping #
            self.ping  = dict((key, value + self.location)
                            for key, value in _ping_response.iteritems())

        # We don't know how ping_response will be keyed as not sure what type of goody.
        goody_key = [key for key in self.ping.keys() if isinstance(key, Goody)][0]
        goody_ping = self.ping[goody_key]

        # We are the target location (location of last ping). Need to ping - they must have moved.
        if distance(goody_ping, self.location) < 1:
            return PING

        possibilities = filter(lambda direction: not obstruction[direction], [UP, DOWN, LEFT, RIGHT])

        # Calc distance to goody of all possibilities
        distances = [distance(self.location + move_to_location(possibility), goody_ping)
                      for possibility in possibilities]
        # Return moves which minimizes distance to last known location of goody
        move = possibilities[distances.index(min(distances))]
        move_to_loc = move_to_location(move)

        # If been here before, do random move instead #
        if self.location + move_to_loc in self.previous_locations:
            move = random.choice(possibilities)
            move_to_loc = move_to_location(move)

        self.location = self.location + move_to_loc
        self.previous_locations.append(self.location)

        return move
