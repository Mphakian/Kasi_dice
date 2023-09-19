
"""    
    Asyncio TCP Server with Callbacks
    For 2-player games with "fat" clients
    The server stores and forwards messages only

    Prince D. Mphaka
    September 2022
    CIS 771 - Advanced Programming, GUI and Networking Project

"""

import asyncio
from collections import deque
from random import choice
import socket
import sys

class Player:
    """This class creates a player instance with a name and a balance of R50k"""
    def __init__(self, name=None):
        """This function initalizes the name and the balance of the player"""
        self.name = name
        self.balance = 50_000    

# shared server state - available to all connections
CONNECTIONS = dict.fromkeys([1,2], None)
TURNS = dict.fromkeys([1,2], None)
GAME_STATE = '1,2,0,0,0' #dice_1, Dice_2, roll, target, bet
BALANCES = '50000,50000' #Thabang's balance,Thabo's balance
thabang_is_playing = True

class Server(asyncio.Protocol):

    def __init__(self):
        """Initialize the server with essential variables"""
        self.thabo = Player(name='thabo')
        self.thabang = Player(name='thabang')
        self.players = [self.thabo.name, self.thabang.name]
        self.player_nr = 0
        self.opponent = 0
        
    def _broadcast(self, message):
        """This function broadcasts messages"""
        for transport in CONNECTIONS.values():
            if transport:
                transport.write(message.encode('utf-8'))

    def _register_player(self):
        """This function assigns a name and player ID to connections, and assigns player"""
        if CONNECTIONS[1] is None and CONNECTIONS[2] is None:
            TURNS[1] = choice(self.players)
            self.players.remove(TURNS[1])
            TURNS[2] = self.players.pop()

        # REGISTER PLAYER 1
        if CONNECTIONS[1] is None:
            self.player_nr, self.opponent = 1, 2
            CONNECTIONS[1] = self.transport
            if CONNECTIONS[2]:
                self._broadcast(f"ok")
            else:
                self._broadcast("wait")

        # REGISTER PLAYER 2
        elif CONNECTIONS[2] is None:
            self.player_nr, self.opponent = 2, 1
            CONNECTIONS[2] = self.transport
            if CONNECTIONS[1]:
                self._broadcast(f"ok")
            else:
                self._broadcast("wait")
        # REJECT SURPLUS PLAYERS
        else:
            self.transport.write(b"refused")
            print('Connection refused - server is full')

    def _deregister_players(self):
        """Remove all players from the connection and reset the game state"""
        global GAME_STATE
        global thabang_is_playing
        global BALANCES
        CONNECTIONS[self.player_nr] = None
        for transport in CONNECTIONS.values():
            if transport:
                transport.close()
        #Reset initial game state
        CONNECTIONS[self.opponent] = None
        thabang_is_playing = True
        GAME_STATE = '1,2,0,0,0' #dice_1, Dice_2, roll, target, bet
        BALANCES = '50000,50000'

    def _handle_message(self, msg):
        """ handle text message or send back an echo if message is not defined """
        global GAME_STATE
        global thabang_is_playing
        global BALANCES

        #A request to identify player ID and player name
        if msg == 'who_am_i':
            self.data = f"{self.player_nr}{TURNS[self.player_nr]}".encode('utf-8')

        #A request to identify if it's thabang's turn 
        elif msg == 'turn':
            self.data = f"{thabang_is_playing}".encode('utf-8')

        #A request for thabang's balance
        elif msg[0:2] == 'b+':
            BALANCES = msg[3:-1]
            
       #A request for thabang's balance
        elif msg == 'b-':
            self.data = f'{BALANCES}'.encode('utf-8')

        #A request to update game state on the server
        elif msg[0] == 's':
            GAME_STATE = msg[2:-1]
            self.data = f'{GAME_STATE}'.encode('utf-8')

        #A request to send current game state
        elif msg[0] == 'g':
            self.data = f'{GAME_STATE}'.encode('utf-8')

        #A request to change thabang_is_playing to true or false
        elif msg == 'change':
            thabang_is_playing = self.change_turn()

        # send the response or echo
        self.transport.write(self.data)
    
    def change_turn(self):
        if thabang_is_playing:
            return False
        else:
            return True

    def connection_made(self, transport):
        """ handles a connection request """
        self.transport = transport
        self.address = transport.get_extra_info('peername')
        self.data = b''
        print(f'Accepted connection from {self.address}')
        self._register_player()

    def data_received(self, data):
        """ handles receipt of data from any client """
        self.data = data
        self._handle_message(data.decode('utf-8'))

    def connection_lost(self, exc):
        """ handles loss of a client connection """
        self._deregister_players()
        print(f'Client {self.address} left the server')

if __name__ == '__main__':   
    # set server address
    host = socket.gethostbyname_ex(socket.gethostname())[-1][0]
    port = 8888
    address = (host, port)

    # create event loop and coroutine
    event_loop = asyncio.get_event_loop()
    coroutine = event_loop.create_server(Server, *address)

    # run main server loop until user presses Ctrl-C
    try:
        server = event_loop.run_until_complete(coroutine)
        print(f'Server started - listening at {address}')
        event_loop.run_forever()
    except KeyboardInterrupt:
        print('Server shutdown')
        sys.exit()
    except Exception as e:
        print(f"Could not start server at {address}\n{e}")
        sys.exit()
  