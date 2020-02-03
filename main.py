from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit, send
import random
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123!'
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

SID_DICT = {} # SID: (Game game, String name)
 

class Game(object):
    def __init__(self, room):
        self.turn = 1
        self.room = room
        self.guesser = None
        self.players = []
        self.word = None
        self.hints = []
        self.trys = []

    def add_player(self, name):
        if name not in self.players:
            self.players.insert(0, name)
            print(f"[add player] Player {name} is added to room {self.room}.")
    

    def start(self):
        """nominate guesser, update the game data (word/turn/guesser)."""
        if (self.players):
            self.word = get_random_words()

            # temp is 0 if turn < players. Then use temp at this case. Else use turn mod players. Turn = realistic turn.
            guesser_index = self.turn % len(self.players)
            self.guesser = self.players[guesser_index - 1]

            self.turn += 1

            self.hints = []
            self.trys = []
    
    def remove_player(self, name):
        """remove the player by name"""
        if name in self.players:
            self.players.remove(name)
            print(">>> {name} is removed from room.")

def get_game_name_by_sid(sid):
    """Used to check database completeness. Return (game, name) tuple or None"""
    if (sid in SID_DICT):
        print(f"[search sid] success. User found in history")
        return SID_DICT[sid]
    else:
        print(f"[search sid] current sid not found in dict. Please request to rejoin")
        return None 

def build_game(room):
    '''create a game with room number into ROOM DICT, if not in SID dict. Return the game'''

    print(f"[build game]: Try to build game with room {room}. Looking if alreday exist.")

    # try to find room
    for (game, name) in SID_DICT.values():
        if game.room == room:
            print(f"[build game] existing game with room {room} found. ")
            return game 
    # code to run when room not found
    print(f"[build game] room {room} not found. Build new game")
    new_game = Game(room)
    return new_game

def get_random_words():
    f = open('words.txt')
    lines = f.readlines()
    word = random.choice(lines).strip()
    return word


@app.route('/')
def sessions():
    return render_template('game_session.html')


def send_game_status(room):
    for (game, name) in SID_DICT.values():
        if game.room == room:
            data = game.__dict__
            socketio.emit('game', data, room=room)
            print(f"[update game] Updated status send to room {room}")
            return
    
    # if not found
    print(f"[error] game status not found. Not supposed to get here.")

def send_rejoin_msg():
    socketio.emit('rejoin', "please rejoin")
    print("[rejoin request] rejoin request just sent.")


@socketio.on('connect')
def handle_connect():
    """when connected, special case maybe connect-break-connect. Client has room/name context but server have no idea who he is. So need to request a client backgroud rejoin."""
    print(f"new client {request.sid} connected")


@socketio.on('disconnect')
def handle_disconnect():
    rc = get_game_name_by_sid(request.sid)
    if rc:
        # remove name from game
        game, name = rc
        game.remove_player(name)
        room = game.room
        send_game_status(room)
        print("[disconnect] {name} left the room {room}")

@socketio.on('join')
def handle_join(data):
    name = data['name']
    room = data['room']
    sid = request.sid

    print(f"[join game] Player {name} wants to join room {room}")

    if (name and room):

        new_game = build_game(room)
        new_game.add_player(name)

        SID_DICT[sid] = (new_game, name)
        
        join_room(room)
        send_game_status(room)

        print(f"[join game] success: {name} joined the room {room}")
    
    else:
        print(f"[join game] faild: empty data: name={name} and room={room}")


@socketio.on('game_start')
def handle_start(room):
    print(f"[game start] room {room} try to start.") 
    rc = get_game_name_by_sid(request.sid)
    if rc:
        game, name = rc
        room = game.room
        game.start()
        send_game_status(room)
        print(f"[game start] success. Game in room {room} started.")
    else:
        send_rejoin_msg()
        print(f"[game start] search game failed. Asked client to rejoin the room")


@socketio.on('send_answer')
def handle_answer(answer):
    print(f"[receive answer] answer received: {answer}.")
    rc = get_game_name_by_sid(request.sid)
    if rc:
        game, name = rc
        room = game.room

        if game.guesser == name:
            game.trys.append(answer)
        else:
            game.hints.append(answer)
        send_game_status(room)
        print(f"[receive answer] {name} provide the answer {answer} in room {room} ")
    else:
        send_rejoin_msg()
        print(f"[receive answer] search game failed. Asked client to rejoin the room")


if __name__ == '__main__':
    socketio.run(app, debug=True)
