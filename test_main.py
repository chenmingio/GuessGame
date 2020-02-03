from main import Game, SID_DICT, build_game, send_game_status, handle_join
from pprint import pprint
from json import dumps

sid = [sid + n for n in range(0, 10)].next

data_1 = {
    name = "Chen",
    room = 601
}

data_2 = {
    name = "Li",
    room = 601
}
data_3 = {
    name = "Chen",
    room = 602
}

sid_1 = 105
def test_handle_join(sid):
    handle_join(data)

handle_join(data)

game_1 = build_game(room_1)
game_1.add_player("Chen Ming")
game_1.add_player("Yuan Yuan")
game_1.add_player("Xiao BAO")
game_1.add_player("Xiao CHEN")


pprint(GAME_DICT)
pprint(data)

