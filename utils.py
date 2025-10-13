import heapq
import os

import numpy as np
from . import vector_utils
from .vector_data_cache import VectorDataCache, distance_vec
from .enums import Color

def calculate_dist(embedding_a, embedding_b):
    return distance_vec(embedding_a, embedding_b)

def rank_boardwords_to_embedding(clue_emb, board_words, vectors, limit=None):
    return heapq.nsmallest(limit, board_words, key=lambda x: calculate_dist(clue_emb, vectors[x]))

def gen_possible_clues(player_words, association_dict, words_to_exclude):
    possible_clues = set(association_dict[player_words[0]])
    possible_clues.intersection_update(*[association_dict[v] for v in player_words[1:]])
    possible_clues.difference_update(player_words, words_to_exclude)
    return list(possible_clues)

def rank_boardwords_to_word(clue, board_words, distance_cache: VectorDataCache, limit=None, noise=0):
    random_distance = [(vector_utils.perturb_distance(distance_cache.distance_word(clue, word), noise), word) for word in board_words]
    return [word for _, word in heapq.nsmallest(limit, random_distance)]

def get_clue_to_playerwords(association_dict, player_words, words_to_exclude):
    ret = {}
    for word in player_words:
        associations = association_dict[word]
        for association in associations:
            if association not in player_words and association not in words_to_exclude:
                if association not in ret:
                    ret[association] = []
                ret[association].append(word)
    return ret

def get_round_weight_idx(num_team_guessed, was_blue_guessed, was_byst_guessed, was_assasin_guessed):
    return -1 + 4 * num_team_guessed + 1*was_blue_guessed + 2 * was_byst_guessed + 3 * was_assasin_guessed

def format_guesses(color_list, limit):
    categories = [0,0,0,0]

    for i, color in enumerate(color_list):
        if i >= limit: break
        categories[color] +=1
        if color != 0:
            break
    return categories

def translate_guesses_to_colors(word_list, player_words, opponent_words, bystander_words, assassin_word):
    result = list()
    
    for word in word_list:
        if word in player_words:
            result.append(Color.TEAM)
            continue
        elif word in opponent_words:
            result.append(Color.OPPONENT)
        elif word in bystander_words:
            result.append(Color.BYST)
        elif word == assassin_word:
            result.append(Color.ASSA)
        break
    return result

def translate_words_to_colors(word_list, player_words, opponent_words, bystander_words, assassin_word):
    result = list()
    
    for word in word_list:
        if word in player_words:
            result.append(Color.TEAM)
        elif word in opponent_words:
            result.append(Color.OPPONENT)
        elif word in bystander_words:
            result.append(Color.BYST)
        elif word == assassin_word:
            result.append(Color.ASSA)
    return result
        
def clamp(value, min_v, max_v):
    return np.clip(value, min_v, max_v)

if os.name == "nt":
    import msvcrt as ms
    class FileLocker:
        def __init__(self, file):
            self.file = file

        @property
        def file(self):
            return self.file

        def __enter__(self):
            ms.locking(self.file.fileno(), ms.LK_RLCK, os.stat(self.log_file_path).st_size)

        def __exit__(self):
            ms.locking(self.file.fileno(), ms.LK_UNLCK, os.stat(self.log_file_path).st_size)
else:
    import fcntl
    class FileLocker:
        def __init__(self, file):
            self.file = file
        
        @property
        def file(self):
            return self.file

        def __enter__(self):
            fcntl.lock(self.file.fileno(), fcntl.LOCK_EX)

        def __exit__(self):
            fcntl.lock(self.file.fileno(), fcntl.LOCK_UN)
            
lock_file = FileLocker