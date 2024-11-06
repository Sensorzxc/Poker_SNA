from pathlib import Path
import os
from typing import Dict


class Action:
    def __init__(self, name: str, action_type: str, pos: str, value=0, pot_before=0):
        self.name = name
        self.action_type = action_type
        self.value = value
        self.pot_before = pot_before
        self.pos = pos


class Round:
    def __init__(self, board: list, actions: list[Action], pot=0):
        self.board = board
        self.actions = actions
        self.pot = pot


class Game:
    def __init__(self, rounds: list[Round], cards: dict[str, list], pot: float, changes: dict):
        self.rounds = rounds
        self.cards = cards
        self.changes = changes
        self.pot = pot


class Session:
    def __init__(self, games: list[Game]):
        self.games = games


class Stats:
    def __init__(self, vpip, pfr, af, bet3, cbet, calls, folds, bets, raises, checks, hands, vpm, tpfr, tbet3):
        self.raises = raises  #
        self.bets = bets  #
        self.folds = folds  #
        self.calls = calls  #
        self.checks = checks  #
        self.cbet = cbet
        self.vpip = vpip  #
        self.pfr = pfr
        self.af = af  #
        self.bet3 = bet3
        self.hands = hands  #
        self.vpm = vpm  #
        self.tpfr = tpfr #
        self.tbet3 = tbet3


sessions: list[Session] = []


def parse_game(game: list[str]) -> Game:
    rounds = []
    cards = {}
    pot = 150
    board = []
    changes = {}
    pos = {}
    if game[0] == '':
        game = game[1:]
    for i in range(2, 8):
        changes[game[i].split(' ')[2]] = 0
        pos[game[i].split(' ')[2]] = i - 2
    changes[game[8].split(':')[0]] += -50
    changes[game[9].split(':')[0]] += -100

    for i in range(11, 17):
        cards[game[i].split(' ')[2]] = [game[i].split(' ')[3][1:], game[i].split(' ')[4][:-1]]
    actions = []
    ind = 17
    while True:
        if game[ind][0] == '*' or game[ind].split(' ')[0] == 'Uncalled':
            break
        board = []
        if game[ind].split(':')[1].split(' ')[1] == 'folds' or game[ind].split(':')[1].split(' ')[1] == 'checks':
            actions.append(
                Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1], pot_before=pot,
                       pos=pos[game[ind].split(':')[0]]))
        elif game[ind].split(':')[1].split(' ')[1] == 'calls':
            actions.append(Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1],
                                  value=float(game[ind].split(':')[1].split(' ')[2]), pot_before=pot,
                                  pos=pos[game[ind].split(':')[0]]))
            changes[game[ind].split(':')[0]] += -float(game[ind].split(':')[1].split(' ')[2])
            pot += float(game[ind].split(':')[1].split(' ')[2])
        else:
            actions.append(Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1],
                                  value=float(game[ind].split(':')[1].split(' ')[4]), pot_before=pot,
                                  pos=pos[game[ind].split(':')[0]]))
            changes[game[ind].split(':')[0]] += -float(game[ind].split(':')[1].split(' ')[4])
            pot += float(game[ind].split(':')[1].split(' ')[4])
        ind += 1
    rounds.append(Round([], actions, pot))
    if game[ind].split(' ')[0] == 'Uncalled':
        changes[game[ind].split(' ')[-1]] += float(game[ind].split(' ')[2][1:-1])
        ind += 1
        actions.append(
            Action(name=game[ind].split(' ')[0], action_type='wins', value=float(float(game[ind].split(' ')[2])),
                   pot_before=pot, pos=pos[game[ind].split(' ')[0]]))
        changes[game[ind].split(' ')[0]] += float(float(game[ind].split(' ')[2]))
        ind += 2
        pot = float(game[ind].split(' ')[2])
        gm = Game(rounds, cards, pot, changes)
        return gm
    if '*** FLOP ***' in game[ind]:
        board = [game[ind].split(' ')[3][1:], game[ind].split(' ')[4], game[ind].split(' ')[5][:-1]]
        ind += 1
    actions = []
    while True:
        if game[ind][0] == '*' or game[ind].split(' ')[0] == 'Uncalled':
            break
        if game[ind].split(':')[1].split(' ')[1] == 'folds' or game[ind].split(':')[1].split(' ')[1] == 'checks':
            actions.append(
                Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1], pot_before=pot,
                       pos=pos[game[ind].split(':')[0]]))
        elif game[ind].split(':')[1].split(' ')[1] == 'calls' or game[ind].split(':')[1].split(' ')[1] == 'bets':
            actions.append(Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1],
                                  value=float(game[ind].split(':')[1].split(' ')[2]), pot_before=pot,
                                  pos=pos[game[ind].split(':')[0]]))
            changes[game[ind].split(':')[0]] += -float(game[ind].split(':')[1].split(' ')[2])
            pot += float(game[ind].split(':')[1].split(' ')[2])
        else:
            actions.append(Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1],
                                  value=float(game[ind].split(':')[1].split(' ')[4]), pot_before=pot,
                                  pos=pos[game[ind].split(':')[0]]))
            changes[game[ind].split(':')[0]] += -float(game[ind].split(':')[1].split(' ')[4])
            pot += float(game[ind].split(':')[1].split(' ')[4])
        ind += 1
    rounds.append(Round(board, actions, pot))
    if game[ind].split(' ')[0] == 'Uncalled':
        changes[game[ind].split(' ')[-1]] += float(game[ind].split(' ')[2][1:-1])
        ind += 1
        actions.append(
            Action(name=game[ind].split(' ')[0], action_type='wins', value=float(float(game[ind].split(' ')[2])),
                   pot_before=pot, pos=pos[game[ind].split(' ')[0]]))
        changes[game[ind].split(' ')[0]] += float(float(game[ind].split(' ')[2]))
        ind += 2
        pot = float(game[ind].split(' ')[2])
        gm = Game(rounds, cards, pot, changes)
        return gm
    if '*** TURN ***' in game[ind]:
        board.append(game[ind].split(' ')[6][1:-1])
        ind += 1
    actions = []
    while True:
        if game[ind][0] == '*' or game[ind].split(' ')[0] == 'Uncalled':
            break
        if game[ind].split(':')[1].split(' ')[1] == 'folds' or game[ind].split(':')[1].split(' ')[1] == 'checks':
            actions.append(
                Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1], pot_before=pot,
                       pos=pos[game[ind].split(':')[0]]))
        elif game[ind].split(':')[1].split(' ')[1] == 'calls' or game[ind].split(':')[1].split(' ')[1] == 'bets':
            actions.append(Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1],
                                  value=float(game[ind].split(':')[1].split(' ')[2]), pot_before=pot,
                                  pos=pos[game[ind].split(':')[0]]))
            changes[game[ind].split(':')[0]] += -float(game[ind].split(':')[1].split(' ')[2])
            pot += float(game[ind].split(':')[1].split(' ')[2])
        else:
            actions.append(Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1],
                                  value=float(game[ind].split(':')[1].split(' ')[4]), pot_before=pot,
                                  pos=pos[game[ind].split(':')[0]]))
            changes[game[ind].split(':')[0]] += -float(game[ind].split(':')[1].split(' ')[4])
            pot += float(game[ind].split(':')[1].split(' ')[4])
        ind += 1
    rounds.append(Round(board, actions, pot))
    if game[ind].split(' ')[0] == 'Uncalled':
        changes[game[ind].split(' ')[-1]] += float(game[ind].split(' ')[2][1:-1])
        ind += 1
        actions.append(
            Action(name=game[ind].split(' ')[0], action_type='wins', value=float(float(game[ind].split(' ')[2])),
                   pot_before=pot, pos=pos[game[ind].split(' ')[0]]))
        changes[game[ind].split(' ')[0]] += float(float(game[ind].split(' ')[2]))
        ind += 2
        pot = float(game[ind].split(' ')[2])
        gm = Game(rounds, cards, pot, changes)
        return gm
    if '*** RIVER ***' in game[ind]:
        board.append(game[ind].split(' ')[7][1:-1])
        ind += 1
    actions = []
    while True:
        while 'collected' in game[ind]:
            actions.append(
                Action(name=game[ind].split(' ')[0], action_type='collected',
                       value=float(float(game[ind].split(' ')[2])),
                       pot_before=pot, pos=pos[game[ind].split(' ')[0]]))
            changes[game[ind].split(' ')[0]] += float(float(game[ind].split(' ')[2]))
            ind += 1
            rounds.append(Round(board, actions, pot))
            gm = Game(rounds, cards, pot, changes)
            return gm
        if game[ind][0] == '*' or game[ind].split(' ')[0] == 'Uncalled':
            break
        if game[ind].split(':')[1].split(' ')[1] == 'folds' or game[ind].split(':')[1].split(' ')[1] == 'checks':
            actions.append(
                Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1], pot_before=pot,
                       pos=pos[game[ind].split(':')[0]]))
        elif game[ind].split(':')[1].split(' ')[1] == 'calls' or game[ind].split(':')[1].split(' ')[1] == 'bets':
            actions.append(Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1],
                                  value=float(game[ind].split(':')[1].split(' ')[2]), pot_before=pot,
                                  pos=pos[game[ind].split(':')[0]]))
            changes[game[ind].split(':')[0]] += -float(game[ind].split(':')[1].split(' ')[2])
            pot += float(game[ind].split(':')[1].split(' ')[2])
        else:
            actions.append(Action(name=game[ind].split(':')[0], action_type=game[ind].split(':')[1].split(' ')[1],
                                  value=float(game[ind].split(':')[1].split(' ')[4]), pot_before=pot,
                                  pos=pos[game[ind].split(':')[0]]))
            changes[game[ind].split(':')[0]] += -float(game[ind].split(':')[1].split(' ')[4])
            pot += float(game[ind].split(':')[1].split(' ')[4])
        ind += 1
    rounds.append(Round(board, actions, pot))
    if game[ind].split(' ')[0] == 'Uncalled':
        changes[game[ind].split(' ')[-1]] += float(game[ind].split(' ')[2][1:-1])
        ind += 1
        actions.append(
            Action(name=game[ind].split(' ')[0], action_type='wins', value=float(float(game[ind].split(' ')[2])),
                   pot_before=pot, pos=pos[game[ind].split(' ')[0]]))
        changes[game[ind].split(' ')[0]] += float(float(game[ind].split(' ')[2]))
        ind += 2
        pot = float(game[ind].split(' ')[2])
        gm = Game(rounds, cards, pot, changes)
        return gm
    if '*** SHOWDOWN ***' in game[ind]:
        ind += 1
    actions = []
    while 'shows' in game[ind]:
        actions.append(
            Action(name=game[ind].split(':')[0], action_type='shows', pot_before=pot, pos=pos[game[ind].split(':')[0]]))
        ind += 1
    while 'collected' in game[ind]:
        actions.append(
            Action(name=game[ind].split(' ')[0], action_type='collected', value=float(float(game[ind].split(' ')[2])),
                   pot_before=pot, pos=pos[game[ind].split(' ')[0]]))
        changes[game[ind].split(' ')[0]] += float(float(game[ind].split(' ')[2]))
        ind += 1
    rounds.append(Round(board, actions, pot))
    gm = Game(rounds, cards, pot, changes)
    return gm


def parse(path):
    with open(path) as f:
        session = []
        lines = f.read()
        all_games = lines.split('\n\n')
        for i in range(len(all_games)):
            game = all_games[i].split('\n')
            gm = parse_game(game)
            session.append(gm)
        sessions.append(Session(session))


def parse_all():
    path = 'pluribus_converted_logs'
    for file in os.listdir(path):
        parse(os.path.join(path, file))


parse_all()

all_players = []


def get_stats():
    stats = {}
    for session in sessions:
        for game in session.games:
            for round in game.rounds:
                changed_h = []
                changed_a = []
                flag = False
                for action in round.actions:
                    if action.name not in stats:
                        stats[action.name] = Stats(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0, 0)
                    if action.name not in changed_h:
                        stats[action.name].hands += 1
                        changed_h.append(action.name)
                    if action.action_type == 'bets' or action.action_type == 'raises' or action.action_type == 'calls':
                        if action.name not in changed_a:
                            stats[action.name].vpm += 1
                            changed_a.append(action.name)
                    if action.action_type == 'raises':
                        stats[action.name].raises += 1
                        if flag:
                            stats[action.name].tbet3 += 1
                        flag = True
                    elif action.action_type == 'bets':
                        stats[action.name].bets += 1
                    elif action.action_type == 'folds':
                        stats[action.name].folds += 1
                    elif action.action_type == 'calls':
                        stats[action.name].calls += 1
                    elif action.action_type == 'checks':
                        stats[action.name].checks += 1
                    if action.name not in all_players:
                        all_players.append(action.name)
        was = []
        for action in game.rounds[0].actions:
            if action.action_type == 'raises':
                was.append(action.name)
                stats[action.name].tpfr += 1


    return stats


stats = get_stats()

for stat in stats:
    print(stat)
    print('raises:', stats[stat].raises)
    stats[stat].af = (stats[stat].bets + stats[stat].raises) / stats[stat].calls
    print('bets:', stats[stat].bets)
    print('folds:', stats[stat].folds)
    print('calls:', stats[stat].calls)
    print('checks:', stats[stat].checks)
    print('af:', stats[stat].af)
    print('hands:', stats[stat].hands)
    print('vpm:', stats[stat].vpm)
    stats[stat].vpip = stats[stat].vpm / stats[stat].hands * 100
    print('vpip:', stats[stat].vpip)
    stats[stat].pfr = stats[stat].tpfr / stats[stat].hands * 100
    print('pfr:', stats[stat].pfr)
    stats[stat].bet3 = stats[stat].tbet3 / stats[stat].hands * 100
    print('bet3:', stats[stat].bet3)
    print('\n')
