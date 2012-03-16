import collections


Command = collections.namedtuple('Command', 'name data')
Command.WAIT = 'wait'
Command.MOVE = 'move'
Command.PICKUP = 'pickup'
Command.DROP = 'drop'
