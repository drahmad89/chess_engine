##NOT IN USE AS OF 29/03/2018

import os

import numpy as np

import train
from MCTS import MCTS
from chess_env import ChessEnv
# this is hypothetical functions and classes that should be created by teamates.
from config import Config
from policy_network import PolicyValNetwork_Giraffe


def generate_games():
    triplet = []
    model = PolicyValNetwork_Giraffe(Config.d_in, Config.h1, Config.h2p, Config.h2e, Config.d_out)
    old_net_iter = 0
    game_number = 0
    while True:
        net_stats = train.load(True)
        if net_stats is not None:
            net_iter = net_stats['iteration']
            if (net_iter != old_net_iter) and (game_number > Config.MINGAMES):
                game_number = 0
                model = model.load_state_dict(net_stats['state_dict'])
                old_net_iter = net_iter
        else:
            net_iter = 0
        step_game = 0
        temperature = 1
        env = ChessEnv()
        env.reset()
        moves = 0
        game_over, z = env.is_game_over(moves)
        while not game_over:
            state = env.board
            step_game += 1
            if step_game == Config.TEMP_REDUCE_STEP:
                temperature = 10e-6
            pi = MCTS(env, temp=temperature, network=model)

            action_index = np.argmax(pi)
            triplet.append([state, pi])

            env.step(Config.INDEXTOMOVE[action_index])
            moves += 1
            game_over, z = env.is_game_over(moves)

        for i in range(len(triplet) - step_game, len(triplet)):
            triplet[i].append(z)
        np.save(os.path.join(Config.GAMEPATH, 'p' + net_iter + '_g' + str(game_number)), np.array(triplet))
        triplet = []
        game_number += 1
