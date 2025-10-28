import bisect
import scipy.spatial.distance as dist
import numpy as np
from json import load, dump 
import bisect

def generate(output_path, model_path, words_path, whitelist, n=300, verbose=False, cleaned=False):
    vectors = load_lm(model_path)
    if verbose: print("Parsed Embeddings")
    words = load_words(words_path)
    if verbose: print("Loaded Words... Starting generation")
    whitelist = set(load_words(whitelist))

    vectors = {k:v for k,v in vectors.items() if k in whitelist}

    if cleaned:
        associations = gen_cleaned_association(vectors, words, n=n, verbose=verbose)
    else:
        associations = gen_association(vectors, words, n=n, verbose=verbose)
    with open(output_path, "w") as f:
        dump(associations, f)

# txt files are actually faster to parse
def txt_to_json(output_path, model_path):
    '''To convert txt to json embeddings'''
    vectors = load_lm(model_path)
    with open(output, "w") as f:
        dump(vectors, f)

def vec_to_txt(output_path, model_path, words_path):
    '''To convert txt to json embeddings'''
    words = set(load_words(words_path))
    new_words = set()
    import codecs

    with open(output_path, "w") as output: 
        with open(model_path, "r", encoding="utf-8") as input_:

            for line in input_:
                word = line.split(maxsplit=1)[0]
                if word in words:
                    new_words.add(word)
                    output.write(line.lower().strip())
                    output.write('\n')
    print(bool(words-new_words))

### HELPER FUNCTIONS ###
embeddings = dict[str, list[float]]

def load_lm(file_name: str) -> embeddings:
    with open(file_name, "r") as f:
        if(file_name [-3:] in ("txt", "vec")):
            vectors = dict()
            for line in f:
                ls = line.split()
                assert len(ls) > 1, "Can't read embeddings file"
                vectors[ls[0]] = np.array([float(n) for n in ls[1:]])
            return vectors
        else:
            return {key:np.array(value) for key,value in load(f).items()}

def load_words(file_name: str) -> list[str]:
    lines = []
    with open(file_name, "r") as f:
        lines = [line.rstrip() for line in f]
    return lines
exceptions = ('lock', 'king', 'table')
add_ins = {
    'suit': ('lawsuit',), 
    'fan': ('fandom',), 
    "comic": ('comedy', "comedian"),
    "capital": ("capitol"),
    "cross": ('across',),
    "cycle": ("bicycle", "tricycle", "cyclist"),
    "tie": ("necktie", "untie"),
    "fighter": ("fighting", "fight"),
    "rose": ("raised", "raise", "raising"),
    "cast": ("outcast",),
    "head": ("airhead",),
    "giant": ("gigantic",),
    "charge": ("discharge",),
    "jack": ("hijack",),
    "bug": ("bugle", "buggy"),
    "fire": ("bonfire",),
    "gas": ("gasoline",),
    "luck": ("unlucky",),
    "shadow": ("shade",),
    "round": ("around",),
    "ham": ("hamper", "hamster", "hammock", "hem"),
    "pan": ("pant", "pane", "pancake", "pantyhose", "dustpan", "saucepan"),
    "cap": ("capitulate",),
    "washer": ("wash","washcloth", "washing"),
    "death": ("dying", "dead", "die",),
    "nail": ("toenail",),
    "snowman": ("snow", "weatherman", "woodsman", "snowboard", "snowball", "milkman", "fireman", "mailman", "caveman", "handyman", "hangman", "postman", "repairman", "tradesman", "man",),
    "fan": ("fandom", "fanatic","fanfare"),
    "piano": ("pianist",),
    "racket": ("rack", "racquet "),
    "cat": ("catwalk", "cataract", "catapult", "categorize", "copycat"),
    "pirate": ("piracy",),
    "row": ("rowdy",),
    "ray": ("stingray",),
    "ice": ("iceberg", "icebox", "icy"),
    "fly": ("dragonfly", "horsefly", "firefly", "flight", "flighty", "housefly",),
    "car": ("caribou", "carnivore"),
    "box": ("letterbox", "inbox", "mailbox", "icebox"),
    "lab": ("laboratory",),
    "air": ("airy", "airhead", "airless", "aircraft",),
    "bar": ("barf", "barmaid", "bartender"),
    "mug": ("muggy",),
    "king": ("kingly",),
    "nut": ("nutty", "nutmeg", "nutcracker", "hazelnut", "walnut", "peanut"),
    "oil": ("oily",),
    "mount": ("surmount",),
    "pipe": ("bagpipe",),
    "point": ("pinpoint",),
    "tap": ("tapioca",),
    "fall": ("fell",),
    "port": ("airport",),
    "scientist": ("science", "scientific"),
    "circle":("circular",),
    "table": ("tablecloth", "tablespoon"),
    "pit": ("pitiful", "pituitary"),
    "ruler": ("ruling",),
    "wake": ("awake", "awaken"),
}
exceptions = ('lock', 'king', 'table')
add_ins = {'suit': ('lawsuit',), 'fan': ('fandom',), "comic": ('comedy',)}
def gen_cleaned_association(dist_dict: embeddings, board_word: list[str],n=300, verbose=False) -> dict[str, list[str]]:
    temp_associations = []
    skipped_words = {}
    ret_dict = dict()
    for i, word in enumerate(board_word, start=1):
        for key in dist_dict.keys():
            if(key == word) or are_words_connected(word, key, word in exceptions) or key in add_ins.get(word, tuple()):
                if(key != word):
                    skipped_words.setdefault(word, []).append(key)
                    print(f"{word} : {key}") 
                continue
            
            pair = (key, dist.cosine(dist_dict[word], dist_dict[key]))
            #ind = bin_search(pair, temp_associations)
            bisect.insort(temp_associations, pair, key=lambda x:x[1])
            #temp_associations.insert(ind, pair)
            
            if(len(temp_associations) > n): del temp_associations[n:] #trim to 300

        ret_dict[word] = [pair[0] for pair in temp_associations]
        del temp_associations[:] # clear

        #if verbose: print(f"{i}/{len(board_word)}", end='\r')

    # with open("common.json", 'w') as f:
    #     dump(skipped_words, f)
    return ret_dict


def gen_association(dist_dict: embeddings, board_word: list[str],n=300, verbose=False) -> dict[str, list[str]]:
    ret_dict = dict()
    for i, word in enumerate(board_word, start=1):
        temp_associations = [
            (dist.cosine(dist_dict[word], dist_dict[key]), key)
            for key in dist_dict.keys()
            if key != word
        ]
        temp_associations.sort()

        ret_dict[word] = [pair[1] for pair in temp_associations[:n]]
        if verbose: print(f"{i}/{len(board_word)}", end='\r')

    return ret_dict


def bin_search(obj, ls)->int:
    '''Find the index of the slot next to it's predesesor'''
    low = -1
    high = len(ls)
    ind = (low + high)//2

    if len(ls)==0: return 0
    
    while(low < high-1):
        if obj[1] == ls[ind][1]: return ind+1
        elif obj[1] > ls[ind][1]: low = ind
        else: high = ind

        ind = (low + high)//2
    return high

### MAIN
if __name__ == "__main__":

    vectors = rf"arg_framework/cn_nb_word_vectors.txt"
    words = r"arg_framework/actual-final-wl.txt"
    whitelist = r"arg_framework/actual-final-wl.txt"
    output = fr"arg_framework/cn_nb_associations.json" 

    generate(output, vectors, words, whitelist, n=300, verbose=True, cleaned=False)
  
