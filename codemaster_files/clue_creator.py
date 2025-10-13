from abc import ABC, abstractmethod
import heapq
import random

import numpy as np

from .. import vector_utils
from ..associator_data_cache import AssociatorDataCache
from ..scorers import Scorer
from ..vector_data_cache import VectorDataCache
from ..llm_components.human_score import HumanInterpretabilityScore
from ..bot_files.bot_settings_obj import BotSettingsObj
from ..enums import Color

from .. import utils

class ClueGiver(ABC):

    def __init__(self):
        self.sample_size = 50

    @abstractmethod
    def initialize(self, bot_settings, *_):
        pass

    def set_sample_size(self, new_size):
        self.sample_size = new_size

    @abstractmethod
    def give_clue(self, noise, red_words, blue_words, byst_words, assassin_word, boardwords):
        pass

    def load_embeddings_and_associations(self, vectors, associations):
        self.vectors = vectors
        self.associations = associations

    def load_weights(self, weights):
        self.weights = weights

    def game_start(self):
        pass
    def round_update(self, clue, guess_colors):
        pass
    def game_end(self):
        pass

class DistanceClueGiver(ClueGiver):

    vectors: VectorDataCache
    associations: dict[str, list] # boardwords to 300 most associated words

    def initialize(self, _, scorer: Scorer, *args):
        self.scorer = scorer

    def game_start(self):
        self.scorer.game_start()

    def round_update(self, clue, guess_colors):
        self.scorer.round_update(clue, guess_colors)

    def game_end(self):
        self.scorer.game_end()
    
    def give_clue(self, noise, player_words, opp_words, byst_words, assassin_word, board_words):
        board_word_colors = utils.translate_words_to_colors(board_words, player_words, opp_words, byst_words, assassin_word)

        max_score = -np.inf
        max_lists = []
        
        self.clue_board_dict = utils.get_clue_to_playerwords(self.associations, player_words, board_words)
        for clue, words in self.clue_board_dict.items():
            max_size = len(player_words)
            board_word_distances = [self.vectors.distance_word(clue, w) for w in board_words]
            noisy_distance_samples = vector_utils.get_perturbed_dist_distances(board_word_distances, noise, self.sample_size)
            
            scores = _get_sampled_scores_by_size(self.scorer, noisy_distance_samples, max_size, board_word_colors)
            
            max_idx = np.argmax(scores)
            if scores[max_idx] >= max_score:
                if scores[max_idx] > max_score:
                    max_lists.clear()
                    max_score = scores[max_idx]
                max_lists.append((clue, max_idx+1))

        return _break_tie(self.vectors, max_lists, board_words)
    
class MiniClueGiver(ClueGiver):
    associations: AssociatorDataCache
    vectors: VectorDataCache

    def initialize(self, vectors, associations):
        self.vectors = vectors
        self.associations = associations

    # TODO consider some kind of safety measures
    # MUST be called before give_clue
    def load_clues(self, boardwords):
        self.boardwords = boardwords.copy()
        self.possible_clues = self._get_possible_clues(boardwords, exclude=False)
        self.sorted_words = {
            clue:
            heapq.nsmallest(25, [(self.vectors.distance_word(clue, boardwords[w]), w) for w in range(len(boardwords))])
            for clue in self.possible_clues
        }

    def _get_possible_clues(self, boardwords, state=None, exclude=True):
        possible_clue_words = set()
        possible_clue_words.update(*[self.associations[boardwords[w]] for w in range(len(boardwords))])

        if exclude: possible_clue_words.difference_update(boardwords)
        return list(possible_clue_words)

    def give_clue(self, state, boardwords, num_player):
        max_clue_word, max_size_num, min_dist = None, 0, float('inf')
        max_targets = None
        print(len(self.possible_clues))
        for clue in self.possible_clues:
            num = 0 # number clues found
            dist = 0 # distance
            targets = [] # target
            for d, w in self.sorted_words[clue]:
                if self.boardwords[w] not in boardwords: continue
                if num == num_player or state[boardwords.index(self.boardwords[w])] != Color.TEAM: break
                num+=1
                dist+=d
                targets.append(w)

            if num != 0 and num >= max_size_num and (num != max_size_num or dist < min_dist):
                max_clue_word, max_size_num, min_dist = clue, num, dist
                max_targets = targets
            
        if max_clue_word == None:
            max_clue_word, max_size_num = random.choice(self.possible_clues), 1

        
        max_targets = [self.boardwords[i] for i in max_targets]
        return (max_clue_word, max_targets)


class AllWordsClueGiver(ClueGiver):
    associations: AssociatorDataCache
    vectors: VectorDataCache

    def initialize(self, vectors, associations):
        self.vectors = vectors
        self.associations = associations

    # TODO consider some kind of safety measures
    # MUST be called before give_clue
    def load_clues(self, boardwords):
        self.boardwords = boardwords.copy()
        self.possible_clues = self._get_possible_clues(boardwords, exclude=False)
        self.sorted_words = {
            clue:
                heapq.nsmallest(25,
                                [(self.vectors.distance_word(clue, boardwords[w]), w) for w in range(len(boardwords))])
            for clue in self.possible_clues
        }

    def _get_possible_clues(self, boardwords, state=None, exclude=True):
        possible_clue_words = set()
        possible_clue_words.update(*[self.associations.wordlist])

        # Make sure our clues are legal
        illegal_clues = set()
        for clue in possible_clue_words:
            for word in boardwords:
                if clue in word or word in clue:
                    illegal_clues.add(clue)
                    break

        possible_clue_words = possible_clue_words - illegal_clues

        if exclude: possible_clue_words.difference_update(boardwords)
        return list(possible_clue_words)

    def give_clue(self, state, boardwords, num_player):
        max_clue_word, max_size_num, min_dist = None, 0, float('inf')
        max_targets = None
        print(len(self.possible_clues))
        for clue in self.possible_clues:
            num = 0  # number clues found
            dist = 0  # distance
            targets = []  # target
            for d, w in self.sorted_words[clue]:
                if self.boardwords[w] not in boardwords: continue
                if num == num_player or state[boardwords.index(self.boardwords[w])] != Color.TEAM: break
                num += 1
                dist += d
                targets.append(w)

            if num != 0 and num >= max_size_num and (num != max_size_num or dist < min_dist):
                max_clue_word, max_size_num, min_dist = clue, num, dist
                max_targets = targets

        if max_clue_word == None:
            max_clue_word, max_size_num = random.choice(self.possible_clues), 1

        max_targets = [self.boardwords[i] for i in max_targets]
        return (max_clue_word, max_targets)

class MaxNWordsClueGiver(ClueGiver):
    associations: AssociatorDataCache
    vectors: VectorDataCache

    def __init__(self, n: int):
        super().__init__()
        self.max_clue_num = n

    def initialize(self, vectors, associations):
        self.vectors = vectors
        self.associations = associations

    # TODO consider some kind of safety measures
    # MUST be called before give_clue
    def load_clues(self, boardwords):
        self.boardwords = boardwords.copy()
        self.possible_clues = self._get_possible_clues(boardwords, exclude=False)
        self.sorted_words = {
            clue:
                heapq.nsmallest(25,
                                [(self.vectors.distance_word(clue, boardwords[w]), w) for w in range(len(boardwords))])
            for clue in self.possible_clues
        }

    def _get_possible_clues(self, boardwords, state=None, exclude=True):
        possible_clue_words = set()
        possible_clue_words.update(*[self.associations.wordlist])

        # Make sure our clues are legal
        illegal_clues = set()
        for clue in possible_clue_words:
            for word in boardwords:
                if clue in word or word in clue:
                    illegal_clues.add(clue)
                    break

        possible_clue_words = possible_clue_words - illegal_clues

        if exclude: possible_clue_words.difference_update(boardwords)
        return list(possible_clue_words)

    def give_clue(self, state, boardwords, num_player, new_max_clue_num = None):
        if new_max_clue_num != None:
            self.max_clue_num = new_max_clue_num
        max_clue_word, max_size_num, min_dist = None, 0, float('inf')
        max_targets = None
        print(len(self.possible_clues))
        for clue in self.possible_clues:
            num = 0  # number clues found
            dist = 0  # distance
            targets = []  # target
            for d, w in self.sorted_words[clue]:
                if self.boardwords[w] not in boardwords: continue
                if num == num_player or state[boardwords.index(self.boardwords[w])] != Color.TEAM or num >= self.max_clue_num: break
                num += 1
                dist += d
                targets.append(w)

            if num != 0 and num >= max_size_num and (num != max_size_num or dist < min_dist):
                max_clue_word, max_size_num, min_dist = clue, num, dist
                max_targets = targets

        if max_clue_word == None:
            max_clue_word, max_size_num = random.choice(self.possible_clues), 1

        max_targets = [self.boardwords[i] for i in max_targets]
        return (max_clue_word, max_targets)


class OptimizedClueGiver(ClueGiver):
    associations: AssociatorDataCache
    vectors: VectorDataCache

    def initialize(self, vectors, associations):
        self.vectors = vectors
        self.associations = associations

    # TODO consider some kind of safety measures
    # MUST be called before give_clue
    def load_clues(self, boardwords):
        self.boardwords = boardwords.copy()
        self.possible_clues = self._get_possible_clues(boardwords, exclude=False)
        self.sorted_words = {
            clue:
                heapq.nsmallest(25,
                                [(self.vectors.distance_word(clue, boardwords[w]), w) for w in range(len(boardwords))])
            for clue in self.possible_clues
        }

    def _get_possible_clues(self, boardwords, state=None, exclude=True):
        possible_clue_words = set()
        possible_clue_words.update(*[self.associations.wordlist])


        # Make sure our clues are legal
        illegal_clues = set()
        for clue in possible_clue_words:
            for word in boardwords:
                if clue in word or word in clue:
                    illegal_clues.add(clue)
                    break

        possible_clue_words = possible_clue_words - illegal_clues

        if exclude: possible_clue_words.difference_update(boardwords)
        return list(possible_clue_words)

    def check_zero(self, state, boardwords, total_player):
        max_clue_word = None
        for clue in self.possible_clues:
            num = 0
            for d, w in reversed(self.sorted_words[clue]):
                if self.boardwords[w] not in boardwords: continue
                if state[boardwords.index(self.boardwords[w])] != Color.TEAM: break
                num += 1

            if num == total_player:
                max_clue_word = clue
                break
        return max_clue_word

    def give_clue(self, state, boardwords, num_player, total_player):
        max_clue_word, max_size_num, min_dist = None, 0, float('inf')
        max_targets = None

        backup_clue = None
        backup_num = 0
        backup_dist = float('inf')
        backup_targets = []

        # If first turn check for clue for zero
        if total_player == num_player:
            zero_clue = self.check_zero(state, boardwords, total_player)
            if zero_clue is not None:
                return (zero_clue, [])

        for clue in self.possible_clues:
            num = 0  # number clues found
            dist = 0  # distance
            targets = []  # target
            for d, w in self.sorted_words[clue]:
                if self.boardwords[w] not in boardwords: continue
                if num == num_player or state[boardwords.index(self.boardwords[w])] != Color.TEAM: break
                num += 1
                dist += d
                targets.append(w) #Targets ends up being a list of indexes and not the actual words

            if num != 0 and num >= backup_num and (num != backup_num or dist < backup_dist):
                backup_clue = clue
                backup_targets = targets
                backup_dist = dist
                backup_num = num

            num_temp = num
            # we don't really need to check if there's a valid second clue unless first clue is greater than or equal to 5
            # if we want it to run faster we can remove the check if dist < min dist
            if num >= 5 and num >= max_size_num and (num != max_size_num or dist < min_dist):
                target_words = [self.boardwords[i] for i in targets]
                future_boardwords = [x for x in boardwords if x not in target_words]
                second_guess_exists = False
                for future_clue in self.possible_clues:
                    num = 0  # number clues found
                    for d, w in self.sorted_words[future_clue]:
                        if self.boardwords[w] not in future_boardwords: continue
                        if num == (num_player - num_temp) or state[boardwords.index(self.boardwords[w])] != Color.TEAM: break
                        num += 1

                    if num == (num_player - num_temp):
                        second_guess_exists = True
                        break

                if second_guess_exists:
                    max_clue_word = clue
                    max_targets = targets
                    min_dist = dist
                    max_size_num = num_temp

        if backup_clue == None:
            backup_clue, backup_targets = random.choice(self.possible_clues), [0]
        if max_clue_word == None:
            max_clue_word, max_targets = backup_clue, backup_targets

        max_targets = [self.boardwords[i] for i in max_targets]
        return (max_clue_word, max_targets)

class OptimizedWithAssumptionClueGiver(ClueGiver):
    associations: AssociatorDataCache
    vectors: VectorDataCache

    def initialize(self, vectors, associations):
        self.vectors = vectors
        self.associations = associations

    # TODO consider some kind of safety measures
    # MUST be called before give_clue
    def load_clues(self, boardwords, illegal_clues = None):
        self._ignore_words = set()
        self.boardwords = boardwords.copy()
        self.first_turn = True
        self.two_turn_win_exists = False
        self.associations_dict = {}
        self.zero_clue_associations = {}
        all_possible_clue_words = self.vectors.vectors[0].keys()
        # Only create associations for legal clues
        if illegal_clues:
            for clue_word in all_possible_clue_words:
                if clue_word not in illegal_clues:
                    self.associations_dict[clue_word] = sorted(boardwords, key=lambda w: self.vectors.distance_word(clue_word, w))
                    self.zero_clue_associations[clue_word] = sorted(boardwords, key=lambda w: self.vectors.distance_word(clue_word, w), reverse=True)
        else:
            for clue_word in all_possible_clue_words:
                illegal_clue = False
                for word in boardwords:
                    # Make sure there there are no substrings so as to avoid illegal clues
                    if clue_word in word or word in clue_word:
                        illegal_clue = True
                if not illegal_clue:
                    self.associations_dict[clue_word] = sorted(boardwords, key=lambda w: self.vectors.distance_word(clue_word, w))
                    self.zero_clue_associations[clue_word] = sorted(boardwords, key=lambda w: self.vectors.distance_word(clue_word, w), reverse=True)

    def reload_clues(self, boardwords, illegal_clues):
        self.associations_dict = {}
        self.zero_clue_associations = {}
        all_possible_clue_words = self.vectors.vectors[0].keys()
        for clue_word in all_possible_clue_words:
            if clue_word not in illegal_clues:
                self.associations_dict[clue_word] = sorted(boardwords, key=lambda w: self.vectors.distance_word(clue_word, w))
                self.zero_clue_associations[clue_word] = sorted(boardwords, key=lambda w: self.vectors.distance_word(clue_word, w), reverse=True)
        
    def check_zero_clue(self):
        for clue, boardwords in self.zero_clue_associations.items():
            team_word_count = 0
            for word in boardwords:
                if word in self._team_words:
                    team_word_count += 1
                elif word in self._ignore_words or word not in self.boardwords: #Skip over words no longer on the board or words we are assuming to ignore
                    continue
                else:
                    break
            if team_word_count == len(self._team_words):
                return (clue,[])
        return None

    def get_association_score(self, clue, target_words):
        """Calculate the association score for a clue and its target words.
        Lower scores are better (closer associations)."""
        total_score = 0
        assoc_size = 1000  # Default association size, can be adjusted if needed
        
        for target in target_words:
            try:
                clue_assoc_strength = 0
                target_assoc_strength = 0
                clue_assoc_strength = self.associations.get_associations(clue).index(target)
                target_assoc_strength = self.associations.get_associations(target).index(clue)
                target_score = (clue_assoc_strength + target_assoc_strength) / 2
            except ValueError:
                if clue_assoc_strength != 0:
                    target_score = (assoc_size + clue_assoc_strength) / 2               
                else:
                    target_score = assoc_size
            total_score += target_score
        return total_score / len(target_words)

    def give_clue(self, state, boardwords, num_player, team_words, reset_assumptions = False):
        if reset_assumptions:
            self._ignore_words.clear()
            self.two_turn_win_exists = False
            self.first_turn = False
        self.boardwords = boardwords.copy()
        self._team_words = team_words.copy()
        if self.first_turn and len(team_words) > 2: # Only keep clues where the three closes words are part of our team so as to make it go faster
            targets_dict, clue_word_to_ignore = self.get_targets_dict(3)
        elif self.two_turn_win_exists: # If we know a two-turn win exists and it is curently turn 2, then we only need to get clues that get all the words left.
            targets_dict, clue_word_to_ignore = self.get_targets_dict(len(team_words), len(team_words))
        else: # Keep all clues where the closest word is ours
            targets_dict, clue_word_to_ignore = self.get_targets_dict()
        self.first_turn = False
        # Check if there is a way to win this turn and return it if it is possible
        immediate_win = self.find_one_turn_win(targets_dict, len(team_words))
        if immediate_win != None:
            self.clue_given = immediate_win
            return immediate_win
        # Find a clue that will guarantee a 2-turn win. If none is found then the greedy clue is returned as a backup
        clue_given = self.find_two_turn_win(targets_dict,clue_word_to_ignore)
        # print(f'codemaster words to ignore: {self._ignore_words}')
        return clue_given

    def find_two_turn_win(self, targets_dict: dict, clue_words_to_ignore: dict) -> tuple[str,list[str]]:
        """Considers all clues passed in the targets_dict and looks one turn ahead to see if a two turn win exists. 
        When looking one turn ahead it will use the clue_words_to_ignore dict to know what clue to ignore, assuming 
        the guesser will also ignore that word. It then prioritizes the clue that has the smallest summed dist 
        between the first and second clue. Note, if no two turn win is found this just returns the greedy clue."""
        #Keep track of orignals of variables to change them back between loop iterations
        og_words_to_ignore = self._ignore_words.copy()
        og_board = self.boardwords.copy()
        og_team_words = self._team_words.copy()
        # Keep track of the greedy best clue as a backup
        greedy_clue = None
        greedy_targets = []
        greedy_dist = float('inf')
        # keep track of best clue to give
        best_clue = None
        best_targets = None
        word_to_ignore = None
        best_dist = float('inf')
        best_balance = 100
        
        # Store all potential two-turn win clues with their scores
        potential_clues = []
        
        # Loop through all potential clues
        for clue,targets in targets_dict.items():
            dist = targets[1]
            # Check if better than greedy clue to update backup if needed
            if len(targets[0]) >= len(greedy_targets) and (len(targets[0]) != len(greedy_targets) or dist < greedy_dist):
                greedy_clue = clue
                greedy_targets = targets[0]
                greedy_dist = dist
            # Add the word to ignore
            self._ignore_words.add(clue_words_to_ignore[clue])
            # Update the board and team words to not include the targets of the first clue
            self.boardwords = [word for word in og_board if word not in targets[0]]
            self._team_words = [word for word in og_team_words if word not in targets[0]]
            # Calculate how many targets there are left
            num_targets_left = len(og_team_words) - len(targets[0])
            # With the updated values find new dicts for clue words and use them to find a one turn win if possible
            future_targets_dict, future_word_ignore = self.get_targets_dict(num_targets_left, num_targets_left)
            best_future_clue = self.find_one_turn_win(future_targets_dict, num_targets_left)
            if best_future_clue != None: #If a win is found update the combined dist with the new clue and change best clue if dist is lower
                # With balance we take the difference between targets length, and the smaller the better. 0 = perfect balance
                balance = abs(len(targets[0]) - len(best_future_clue[1]))
                if len(best_future_clue[1]) == 0: #Check if this is a 0 clue, if so give it a high dist so it is less prioritized
                    dist += 99999999999
                else:
                    dist += future_targets_dict[best_future_clue[0]][1]
                
                # Calculate association score for this clue
                if not best_future_clue[1]:
                    association_score = self.get_association_score(clue, targets[0])
                else:
                    association_score = self.get_association_score(clue, targets[0]) + self.get_association_score(best_future_clue[0],best_future_clue[1])
                
                # Store clue information for ranking
                potential_clues.append({
                    'clue': clue,
                    'targets': targets[0],
                    'dist': dist,
                    'balance': balance,
                    'association_score': association_score,
                    'word_to_ignore': clue_words_to_ignore[clue]
                })
                
            # Change global variables back to the originals for the next iteration of the loop
            self._ignore_words = og_words_to_ignore.copy()
            self.boardwords = og_board.copy()
            self._team_words = og_team_words.copy()
        
        # If we found potential two-turn wins, rank them and take top 5
        if potential_clues:
           # Count how many zero clues there are
            non_zero_clues = []
            for clue in potential_clues:
                if clue['dist'] < 9999999999:
                    non_zero_clues.append(clue)
            if non_zero_clues:
                potential_clues = non_zero_clues.copy()
             # Sort by association score first (lower is better), then by balance, then by distance
            potential_clues.sort(key=lambda x: (x['balance'], x['association_score'], x['dist']))
            
            # Take top 5 clues
            if len(potential_clues) >=5:
                top_clues = potential_clues[:5]
            else:
                top_clues = potential_clues[:len(potential_clues)]
            
            best_clue_info = top_clues[0]
            
            best_clue = best_clue_info['clue']
            best_targets = best_clue_info['targets']
            best_dist = best_clue_info['dist']
            best_balance = best_clue_info['balance']
            word_to_ignore = best_clue_info['word_to_ignore']
            
            # print("top clues: ", top_clues)
        # Check if a 2 turn win has been found and return it as well as update the words to ignore list
        if best_clue == None:
            self._ignore_words.add(clue_words_to_ignore[greedy_clue])
            return (greedy_clue, greedy_targets)
        else: # If no 2 turn win has been found return the greedy clue as a backup
            self.two_turn_win_exists = True
            self._ignore_words.add(word_to_ignore)
            return (best_clue, best_targets)
        
    
    def get_targets_dict(self, n=1, m=9):
        """Returns 2 dictionaries inside a tuple. In the first dictionary each key represents a clue that 
        has at least n closest team words and at most m closest team words. The value contains a list where  
        the first element is a list of the target words and the second element is a float representing the 
        sum of the distances between target words and clue words (Used for tie breakers, prioritizing smaller 
        distances). The second dict contains all the same keys as the first dict, but the value represents the 
        word that the closest non-team word, which we can then ignore later on."""
        targets_dict = {}
        clue_word_to_ignore = {}

        # Loop through all the potential clues and the sorted boardwords
        for clue, boardwords in self.associations_dict.items():
            targets = [[],0] #Stores all the targets in the first list and it stores the dist in the int
            for word in boardwords:
                if word in self._team_words:
                    targets[0].append(word)
                    targets[1] += self.vectors.distance_word(clue,word)
                elif word in self._ignore_words or word not in self.boardwords: #Skip over words no longer on the board or words we are assuming to ignore
                    continue
                else:
                    word_to_ignore = word
                    break
            
            if len(targets[0]) < n or len(targets[0]) > m: # Get rid of clues that have less than n or more than m target words
                continue
            else: #If the num of targets is within the threshold add clue and targets and dist to first dict and add clue and word to ignore in second dict
                targets_dict[clue] = targets
                clue_word_to_ignore[clue] = word_to_ignore
        # Sort the first dict by how many targets are connected to each key, clues with more targets will be at the top
        sorted_targets = dict(sorted(targets_dict.items(), key=lambda x: len(x[1][0]), reverse=True))
        return (sorted_targets,clue_word_to_ignore)
    
    def find_one_turn_win(self,targets_dict: dict, len_needed: int):
        """Check if there is a way to win in one turn. If there is return a tuple of the clue and target words"""
        potential_wins = []
        # Loop through the targets dict for potential clues to win this turn
        for clue,targets in targets_dict.items(): # targets[0] = list of targets and targets[1] = clue dist
            if len(targets[0]) == len_needed:
                association_score = self.get_association_score(clue, targets[0])
                potential_wins.append((clue,targets[1], association_score))
            else: #Since the dict is sorted from highest length of targets to lowest once we get below the needed length we can stop iterating
                break
        if potential_wins: # if there is a potential win then look at all of them and prioritize by lowest dist
            potential_wins.sort(key=lambda x: (x[2],x[1]))
            best_clue = potential_wins[0][0]
            best_targets = targets_dict[best_clue][0]
            return(best_clue, best_targets)
        zero_clue = self.check_zero_clue()
        if zero_clue != None:
            return zero_clue
        return None #If there are no potenial wins then return None
    
class EmbeddingClueGiver(ClueGiver):

    vectors: VectorDataCache
    associations: dict[str, list] # boardwords to 300 most associated words

    def initialize(self, _: BotSettingsObj, scorer: Scorer):
        self.scorer = scorer

    def game_start(self):
        self.scorer.game_start()

    def round_update(self, clue, guess_colors):
        self.scorer.round_update(clue, guess_colors)

    def game_end(self):
        self.scorer.game_end()
    
    def give_clue(self, noise, player_words, opp_words, byst_words, assassin_word, board_words):
        board_word_colors = utils.translate_words_to_colors(board_words, player_words, opp_words, byst_words, assassin_word )

        board_word_embeddings = np.array([self.vectors[w] for w in board_words])
        board_word_embeddings /= np.linalg.norm(board_word_embeddings, axis=1)[:, np.newaxis]

        max_score = -np.inf
        max_lists = []
        
        self.clue_board_dict = utils.get_clue_to_playerwords(self.associations, player_words, board_words)
        for clue, words in self.clue_board_dict.items():
            max_size = len(player_words) # or len(player_words)
            noisy_distance_samples = vector_utils.get_perturbed_emb_distances(self.vectors[clue], board_word_embeddings, noise, self.sample_size)
            
            scores = _get_sampled_scores_by_size(self.scorer, noisy_distance_samples, max_size, board_word_colors)

            max_idx = np.argmax(scores)
            if scores[max_idx] >= max_score:
                if scores[max_idx] > max_score:
                    max_lists.clear()
                    max_score = scores[max_idx]
                max_lists.append((clue, max_idx+1))

        return _break_tie(self.vectors, max_lists, board_words)

def _get_sampled_scores_by_size(scorer, noisy_distance_samples, max_size, board_word_colors):
    scores = np.zeros(max_size)
    for noisy_board_word_distances in noisy_distance_samples:
        sorted_idcs = heapq.nsmallest(max_size, range(len(board_word_colors)), key=noisy_board_word_distances.__getitem__)
        nearest_board_word_colors = [board_word_colors[i] for i in sorted_idcs]
        
        for size in range(len(nearest_board_word_colors)):
            score = scorer.score_clue(clue=size+1, guess_colors=nearest_board_word_colors)
            scores[size] += score
    return scores

def _break_tie(vectors, max_lists, board_words):
    clue_targets = None
    min_dist = np.inf
    for clue, size in max_lists:
        targets = utils.rank_boardwords_to_word(clue, board_words, vectors, limit=size)
        dist = sum(vectors.distance_word(clue, t) for t in targets)
        if dist < min_dist:
            min_dist = dist
            clue_targets = (clue, targets)
    return clue_targets