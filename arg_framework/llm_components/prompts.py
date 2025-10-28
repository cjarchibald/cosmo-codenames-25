#can add other text to change playstyle here
#TODO how can we explain how to choose target words? Without drastically increasing inference time
def final_codemaster_instruction(team_color):
    prompt = ""
    prompt += "Choose up to three target words from the " + team_color + " teams list that are closely related."
    prompt += "All words not on the " + team_color + " team's list should be consider as BAD words"
    prompt += "Then follow the steps given above to determine the final clue and target words"
    prompt += " Additionally, the clue cannot be derived from or derive one of the words on the board. \n"
    prompt += "Follow the json format exactly! Do not miss any fields!"
    return prompt

def optimized_codemaster_instruction(team_color):
    """Optimized instruction that is more concise and focused"""
    prompt = f"Choose 1-3 target words from the {team_color} team's list that are semantically related. "
    prompt += "The clue must connect strongly to your targets while avoiding all other words, especially the assassin. "
    prompt += "The clue cannot be derived from or derive any board word. "
    prompt += "Provide exactly the JSON format requested."
    return prompt

basic_rules = """
Codenames is a word-based game of language understanding and communication.
Players are split into two teams (red and blue), with each team consisting of a Codemaster and Guesser.
Setup:
At the start of the game, the board consists of 25 English words.
The Codemasters on each team has access to a hidden map that tells them the identity of all of the words (Red, Blue, Civilian or Assassin).
The Guessers on each team do not have access to this map, and so do not know the identity of any words.
Players need to work as a team to select their words as quickly as possible, while minimizing the number of incorrect guesses.
Turns:
At the start of each team's turn, the Codemaster supplies a clue and a number (the number of words related to that clue).
The clue must:
- Be semantically related to the words the Codemaster wants their Guesser to guess.
- Be a single English word.
- NOT be derived from or derive one of the words on the board.
The Guesser then selects from the remaining words on he board, based on the which words are most associated with the Codemaster's clue.
The identity of the selected word is then revealed to all players.
If the Guesser selected a word that is their team's colour, then they may get to pick another word.
The Guesser must always make at least one guess each turn, and can guess up to one word more than the number provided in the Codemaster's clue.
If a Guesser selects a word that is not their team's colour, their turn ends.
The Guesser can choose to stop selecting words (ending their turn) any time after the first guess.
Ending:
Play proceeds, passing back and forth, until one of three outcomes is achieved:
All of the words of your team's colour have been selected -- you win
All of the words of the other team's colour have been selected -- you lose
You select the assassin tile -- you lose

"""

extended_codemaster_prompt = """
You are the Codemaster in a game of Codenames. If you win you will get a million dollars! Otherwise you will die :(.

Your task is to give a clue (a single word and a number, e.g., “bridge, 2”) that will help your teammate guess the TARGET words. The clue must relate to the TARGET words and must **avoid leading your teammate toward any BAD WORDS**, especially the ASSASSIN word.

---

Follow these steps:
### STEP 0: Write out the TARGET words and the BAD words and ASSASSIN word

### STEP 1: Generate a set of 5 candidate clue words.

Each clue should aim to connect **2 or more TARGET words** through a shared concept, theme, or property. BUT AVOID THE ASSASSIN at ALL COSTS!

---

### STEP 2: For each clue, score the strength of its association to every word on the board.

Use a 0–10 scale:
- 0 = no meaningful association
- 10 = extremely strong and direct association

Create a table for each clue like this:

Clue: <your clue>

Word	Score	Justification
word_1	X	explanation
word_2	Y	explanation
...
Order the list by the associations score
If there is no association simply write NDC in the justification square

---

### STEP 3: Eliminate any clue that fails either of these safety rules:

❌ **RULE 1 (Safety Check):** If **any BAD or ASSASSIN word** has a higher association score than **any of the TARGET words**, **discard the clue**.

❌ **RULE 2 (Strength Check):** If **no TARGET word** has an association score **greater than 6**, **discard the clue**.

This ensures that:
- BAD words don’t distract more than TARGETs.
- Your clue meaningfully and clearly connects to TARGETS.

---

### STEP 4: Among the remaining clues, choose the one that:
- Maximizes the number of TARGET words with strong associations.
- Minimizes the number of weakly related or neutral words (false positives).
- Is easy to interpret and unambiguous.

---

### STEP 5 If no clue is found
- Get rid of the least related TARGET word.
- Generate up to 5 more clue words
- Follow STEP 4 to choose a clue word
- If we still cant find a clue repeat this step one more time
- We must give at least one clue word and target word
- If we get stuck output error as the clue word and choose a random team word as the target word

---

### STEP 6: Justify your final clue choice.

Explain:
- Why it connects well to your TARGETS.
- Why it avoids the BAD and ASSASSIN words.
- Why other candidate clues were discarded.

---

REMEMBER your life and a million dollars is on the line!
"""

optimized_codemaster_prompt = """
You are a Codemaster in Codenames. Your goal is to give a single-word clue that helps your teammate guess your TARGET words while avoiding all other words, especially the ASSASSIN.

CRITICAL RULES:
1. The clue must connect strongly to your TARGET words
2. The clue must avoid all BAD words and the ASSASSIN word
3. The clue cannot be derived from or derive any board word
4. Choose 1-3 target words that are semantically related

PROCESS:
1. Identify your target words from your team's list
2. Generate 3-5 candidate clue words that could connect multiple targets
3. Evaluate each clue for safety (avoiding bad/assassin words)
4. Choose the best clue that maximizes target connections while minimizing risks
5. Provide a brief justification for your choice

FALLBACK: If no good multi-target clue exists, choose a single strong target with a safe clue.

Focus on semantic relationships: synonyms, categories, themes, functions, or shared properties.
"""

# Optimized demo examples for the new model
optimized_demo_input = """
You need to give a clue for team red. The remaining words are: 
Red: ["pipe", "robot", "belt"]. 
Blue: ["rock", "moon", "soul", "staff"]. 
Civilian: ["vacuum", "cap"]. 
Assassin: rock. 
Choose 1-3 target words from the red team's list that are semantically related. The clue must connect strongly to your targets while avoiding all other words, especially the assassin. The clue cannot be derived from or derive any board word. Provide exactly the JSON format requested.
"""

optimized_demo_output = """
{
    "game_board": {
        "target_words": ["pipe", "robot", "belt"],
        "bad_words": ["rock", "moon", "soul", "staff", "vacuum", "cap"],
        "assassin_word": "rock"
    },
    "candidate_clues": ["factory", "industrial", "mechanical", "machine", "metal"],
    "final_choice": {
        "clue": "factory",
        "target_words": ["pipe", "robot", "belt"],
        "justification": "Factory connects strongly to all three targets: pipes are used in factories, robots operate in factories, and belts refer to conveyor belts. It avoids associations with bad words and the assassin."
    },
    "clue_associations": {
        "factory": {
            "pipe": 8,
            "robot": 8,
            "belt": 9,
            "rock": 0,
            "moon": 0,
            "soul": 0,
            "staff": 2,
            "vacuum": 3,
            "cap": 0
        }
    },
    "flagged_risks": {
        "factory": []
    }
}
"""
demo_extended_prompt_claude_input = """
You are acting as a Codemaster in the game of Codenames. Your task is to choose a single clue word and a number (e.g., "metal, 2") to help your teammate guess as many TARGET words as possible, while avoiding all BAD WORDS, especially the ASSASSIN.

---



You need to give a clue for team red. The remaining words are: Red: ["pipe", "robot", "belt"]. Blue: ["rock", "moon", "soul", "staff"]. Civilian: ["vacuum", "cap"]. Assassin: rock. Choose up to three target words from the red teams list that are closely related.All words not on the red team's list should be consider as BAD words. Then follow the steps given above to determine the final clue and target words Additionally, the clue cannot be derived from or derive one of the words on the board.

---
"""

demo_extended_prompt_claude_output_json =  """
{
    "game_board": {
      "target_words": ["pipe", "robot", "belt"],
      "bad_words": ["rock", "moon", "soul", "staff", "vacuum", "cap"],
      "assassin_word": "rock"
    },
    "possible_clues": [
      "metal",
      "machine",
      "factory",
      "industrial",
      "mechanical"
    ],
    "clue_associations": {
      "metal": {
        "pipe": 9,
        "robot": 8,
        "belt": 5,
        "rock": 4,
        "moon": 2,
        "soul": 0,
        "staff": 3,
        "vacuum": 3,
        "cap": 1
      },
      "machine": {
        "pipe": 5,
        "robot": 9,
        "belt": 7,
        "rock": 0,
        "moon": 0,
        "soul": 0,
        "staff": 0,
        "vacuum": 7,
        "cap": 0
      },
      "factory": {
        "pipe": 8,
        "robot": 8,
        "belt": 9,
        "rock": 0,
        "moon": 0,
        "soul": 0,
        "staff": 2,
        "vacuum": 3,
        "cap": 0
      },
      "industrial": {
        "pipe": 9,
        "robot": 8,
        "belt": 8,
        "rock": 2,
        "moon": 0,
        "soul": 0,
        "staff": 1,
        "vacuum": 3,
        "cap": 0
      },
      "mechanical": {
        "pipe": 6,
        "robot": 9,
        "belt": 8,
        "rock": 0,
        "moon": 0,
        "soul": 0,
        "staff": 1,
        "vacuum": 7,
        "cap": 1
      }
    },
    "justifications": {
      "metal": "Strongly connects to PIPE and ROBOT, and somewhat to BELT. However, METAL also links moderately to the assassin word ROCK and bad words like STAFF and VACUUM, making it a risky clue despite high relevance.",
      "machine": "Extremely strong for ROBOT, decent for BELT and PIPE, but has a dangerously high association with the bad word VACUUM, reducing safety.",
      "factory": "Strong connections to all three target words: robots operate in factories, pipes are part of industrial infrastructure, and belts refer to conveyor belts. It avoids associations with bad words and the assassin, making it a highly safe and effective clue.",
      "industrial": "High relevance across all targets, though slightly less than FACTORY. Mild risk due to connections to ROCK and VACUUM, though weaker than METAL.",
      "mechanical": "Very strong for ROBOT and BELT, moderate for PIPE. However, like MACHINE, it shares a strong link to VACUUM, which undermines its safety."
    },
    "flagged_risks": {
      "metal": ["rock", "staff", "vacuum", "cap"],
      "machine": ["vacuum"],
      "factory": [],
      "industrial": ["rock", "vacuum"],
      "mechanical": ["vacuum", "cap"]
    },
    "final_choice": {
      "clue": "factory",
      "target_words": ["PIPE", "ROBOT", "BELT"],
      "justification": "FACTORY connects strongly to all three target words (PIPE, ROBOT, BELT) and has no notable associations with any bad or assassin words. Other clues carry moderate risks—especially METAL and MACHINE—due to overlapping associations with VACUUM, ROCK, or STAFF. FACTORY is semantically tight, broad enough to cover all three targets, and the safest overall."
    }
}
"""
demo_extended_prompt_claude_output = """
### Game Board:
- TARGET WORDS: ["pipe", "robot", "belt"]
- BAD WORDS: ["rock", "moon", "soul", "staff", "vacuum", "cap"]
- ASSASSIN WORD: "rock"

## Step 1: Generate candidate clues

Here are my candidate clues that could connect multiple TARGET words:

1. **METAL** - pipes and belts can be made of metal, robots often contain metal
2. **MACHINE** - robots are machines, pipes and belts are machine components
3. **FACTORY** - all three items commonly found in industrial/factory settings
4. **INDUSTRIAL** - pipes, robots, and belts all have industrial applications
5. **MECHANICAL** - all three relate to mechanical systems or devices

## Step 2: Rate associations to all board words

### METAL:
- **pipe** (9) - metal pipes very common
- **robot** (8) - robots typically made of metal
- **belt** (5) - metal belt buckles, conveyor belts with metal parts
- **rock** (4) - some rocks contain metal/minerals ⚠️
- **moon** (2) - moon has some metals but weak connection
- **soul** (0) - NDC
- **staff** (3) - metal staffs exist ⚠️
- **vacuum** (3) - vacuum cleaners have some metal parts
- **cap** (1) - bottle caps are often metal ⚠️

### MACHINE:
- **pipe** (5) - pipes are machine components
- **robot** (9) - robots are machines
- **belt** (7) - conveyor belts, machine belts
- **rock** (0) - NDC
- **moon** (0) - NDC
- **soul** (0) - NDC
- **staff** (0) - NDC
- **vacuum** (7) - vacuum cleaner is a machine ⚠️
- **cap** (0) - NDC

### FACTORY:
- **pipe** (8) - factories have extensive piping
- **robot** (8) - industrial robots in factories
- **belt** (*) - conveyor belts everywhere in factories
- **rock** (0) - NDC
- **moon** (0) - NDC
- **soul** (0) - NDC
- **staff** (2) - factory staff but weak
- **vacuum** (3) - industrial vacuums exist but weak
- **cap** (0) - NDC

### INDUSTRIAL:
- **pipe** (9) - industrial piping systems
- **robot** (8) - industrial robotics
- **belt** (8) - industrial conveyor systems
- **rock** (2) - quarrying is industrial but weak
- **moon** (0) - NDC
- **soul** (0) - NDC
- **staff** (1) - industrial staff but weak
- **vacuum** (3) - industrial vacuum systems ⚠️
- **cap** (0) - NDC

### MECHANICAL:
- **pipe** (6) - mechanical systems use pipes
- **robot** (9) - robots are mechanical devices
- **belt** (8) - mechanical belt systems
- **rock** (0) - NDC
- **moon** (0) - NDC
- **soul** (0) - NDC
- **staff** (1) - mechanical staff possible but weak
- **vacuum** (7) - vacuum pumps are mechanical ⚠️
- **cap** (1) - bottle caps have mechanical aspects but weak

## Step 3: Identify and flag risks

**METAL** - Flagged risks: rock (2), staff (2), cap (2) - multiple moderate risks
**MACHINE** - Flagged risks: vacuum (4) - one strong risk to bad word
**FACTORY** - No flagged risks (all bad/assassin words rated 0-1)
**INDUSTRIAL** - Flagged risks: vacuum (2) - one moderate risk
**MECHANICAL** - Flagged risks: vacuum (3) - one moderate risk

## Step 4: Choose the best clue

**FACTORY, 3**

## Step 5: Justify your decision

FACTORY connects strongly to all three target words (pipe-4, robot-4, belt-4) as all are commonly found in factory environments - piping systems, industrial robots, and conveyor belts are factory staples. This clue is significantly safer than other candidates because it has zero meaningful connections to any bad words or the assassin word "rock," while alternatives like METAL have multiple moderate risks and MACHINE has a strong connection to the bad word "vacuum."
"""
demo_extended_prompt ="""
✅ Example Output (Demo with Full Steps and Association Rationales)
🎯 Target words: kangaroo, piano, mirror
❌ Bad words: Australia, music, reflection, violin, glass, jump
☠️ Assassin: glass

🔁 Step 1: Clue Evaluation
We consider potential clue words one by one. For each clue, we rate association strength (0–10) between the clue and:

Each target word

Each bad word

We also give a brief rationale for each association.

We discard any clue where:

A bad word scores higher than any target word

All target scores are ≤ 6

🔁 Step 2: Try 10 Candidate Clues
Clue	Kangaroo	Piano	Mirror	Max Bad	Result
bounce	7 – kangaroos bounce	1 – not musical	1 – no relation	9 (jump – “bounce” is synonymous)	❌
Australia	9 – kangaroos are native	0 – no clear tie	0 – unrelated	10 (Australia – exact match)	❌
music	1 – kangaroo dances? stretch	9 – piano is a musical instrument	0 – unrelated	10 (music – exact match)	❌
tune	0 – no real tie	8 – you tune a piano	0 – no link	9 (violin – also tuned)	❌
reflection	0 – no link	0 – not reflective	9 – mirrors reflect	10 (reflection – exact match)	❌
concert	0 – kangaroo not musical	8 – piano played at concerts	0 – no link	9 (violin – played at concerts)	❌
glass	0 – not related	0 – NDC	8 – mirrors made of glass	10 (glass – assassin)	❌
leap	7 – kangaroos leap	1 – not related	1 – no tie	8 (jump – near synonym)	❌
sound	3 – kangaroos make noise?	7 – piano produces sound	2 – weakly related	8 (music – strongly linked)	❌
signal	1 – weak metaphor	7 – piano as signal for cue?	2 – maybe reflective signals?	9 (astronaut/sci-fi theme)	❌

All 10 clues violate one or more constraints (bad word scores too high or targets ≤ 6).

🟨 Step 3: Fallback — Reduce to Pairs
Tried combinations:

kangaroo, piano

kangaroo, mirror

piano, mirror

Each failed for same reasons — bad word associations stronger or targets too weakly linked.

🟥 Step 4: Single-Target Fallback
We now test each target alone, looking for a strong clue with low max bad score.

✅ Success: kangaroo with clue pouch
Word	Score	Explanation
kangaroo	9 ✅	Kangaroos famously carry young in pouches
Australia	3	Slight tie due to context (Australian fauna)
music	0	No relationship
reflection	0	No relationship
violin	0	No relationship
jump	1	Very weakly related (kangaroos jump)
glass	0	No relationship

✅ All constraints satisfied:

Target ≥ 7

All bad words < target

Max bad word = 3 → very safe

✅ Final Clue
Clue: pouch

Number of Targets: 1

Target Word(s): kangaroo

Explanation:

The word "pouch" is strongly associated with kangaroos, who carry their young in pouches (score 9). All bad words have weak or no relation (max 3), making it a clear and safe fallback clue.

Answer:'pouch'['kangaroo']
"""
def generate_guesser_prompt(team_color,clue, num_guess, board_words):
        prompt = "It is your team, team " + team_color + "\'s turn.\n"
        prompt += "Do NOT NOT CHOOSE " + clue + " AS A GUESS!"
        prompt += "Boardwords: " + str(board_words) + "\n"
        prompt += "Clue: " + clue + "\n"
        prompt += "Clue Number: " + str(num_guess)
        if clue == "":
            prompt += "The clue is blank, please make your best informed guess"
        if clue == "error":
             prompt += "The codemaster encountered an error, set all fields to zero or blank and choose random words"
        return prompt

guesser_input_demo = """
Boardwords = ['ruler', 'opera', 'ghost', 'drill', 'mint', 'rock', 'scientist', 'giant', 'fall', 'kiwi', 'pan', 'moon', 'diamond', 'tap', 'pirate', 'whale', 'cat', 'staff', 'game', 'oil', 'key', 'wake', 'disease', 'casino', 'train']
Clue = 'treasure'
Clue Number = 3
"""
guesser_output_demo = """
{
  "word_association": [
    {
      "word": "ruler",
      "association_strength": 4,
      "descriptive_phrase": "Kings or rulers might own treasure, but the connection is indirect"
    },
    {
      "word": "opera",
      "association_strength": 1,
      "descriptive_phrase": "Opera has little to no relation to treasure"
    },
    {
      "word": "ghost",
      "association_strength": 3,
      "descriptive_phrase": "Ghosts sometimes guard treasure in stories, but it's a weak link"
    },
    {
      "word": "drill",
      "association_strength": 5,
      "descriptive_phrase": "You might use a drill to access buried treasure, like in a heist"
    },
    {
      "word": "mint",
      "association_strength": 7,
      "descriptive_phrase": "Mint can refer to a place where coins (treasure) are made"
    },
    {
      "word": "rock",
      "association_strength": 3,
      "descriptive_phrase": "Treasure can be hidden among rocks, but it's not a direct link"
    },
    {
      "word": "scientist",
      "association_strength": 1,
      "descriptive_phrase": "Scientists don't have a strong connection to treasure"
    },
    {
      "word": "giant",
      "association_strength": 4,
      "descriptive_phrase": "Giants in folklore may guard treasure, but it's not universal"
    },
    {
      "word": "fall",
      "association_strength": 2,
      "descriptive_phrase": "Little to no connection to treasure"
    },
    {
      "word": "kiwi",
      "association_strength": 0,
      "descriptive_phrase": "No semantic relation to treasure"
    },
    {
      "word": "pan",
      "association_strength": 6,
      "descriptive_phrase": "Panning for gold is a direct method of searching for treasure"
    },
    {
      "word": "moon",
      "association_strength": 1,
      "descriptive_phrase": "No strong relation to treasure"
    },
    {
      "word": "diamond",
      "association_strength": 10,
      "descriptive_phrase": "Diamonds are a classic form of treasure"
    },
    {
      "word": "tap",
      "association_strength": 1,
      "descriptive_phrase": "No strong relation to treasure"
    },
    {
      "word": "pirate",
      "association_strength": 10,
      "descriptive_phrase": "Pirates are strongly associated with buried treasure"
    },
    {
      "word": "whale",
      "association_strength": 1,
      "descriptive_phrase": "No meaningful connection to treasure"
    },
    {
      "word": "cat",
      "association_strength": 0,
      "descriptive_phrase": "Cats have no connection to treasure"
    },
    {
      "word": "staff",
      "association_strength": 3,
      "descriptive_phrase": "A magical staff might guard treasure in fantasy, but weak link"
    },
    {
      "word": "game",
      "association_strength": 2,
      "descriptive_phrase": "Treasure hunts can be games, but the link is soft"
    },
    {
      "word": "oil",
      "association_strength": 6,
      "descriptive_phrase": "Oil is sometimes considered 'black gold' and a kind of modern treasure"
    },
    {
      "word": "key",
      "association_strength": 8,
      "descriptive_phrase": "Keys are often used to unlock treasure chests"
    },
    {
      "word": "wake",
      "association_strength": 1,
      "descriptive_phrase": "Little to no relation to treasure"
    },
    {
      "word": "disease",
      "association_strength": 0,
      "descriptive_phrase": "No semantic connection to treasure"
    },
    {
      "word": "casino",
      "association_strength": 6,
      "descriptive_phrase": "Casinos are associated with riches and winnings"
    },
    {
      "word": "train",
      "association_strength": 3,
      "descriptive_phrase": "A train might carry treasure in a heist movie, but it's a stretch"
    }
  ],
  "guesses_list": ["diamond", "pirate", "key"]
}
"""
guesser_prompt = """
You are playing the board game Codenames. Your task is to guess which words on the board the clue-giver (Codemaster) is trying to point you toward using a single clue word and a number.

You will receive:

A clue word

A number representing how many words are associated with the clue

A list of words that are currently on the board

Your job is to:

For each board word, give:

A connection strength score from 0 to 10 (where 10 = very strong connection, 0 = completely unrelated)

A short descriptive phrase explaining the semantic connection or why the clue might relate to this word.

After rating all words, select the top N words (where N = number from the clue) as your guesses.
If not enough words connect strongly as the clue number than you may guess less than the clue number BUT you MUST guess at least one word!
If all fails, choose a random word
Return the selected guesses in descending order of connection strength.
"""

synonym_guru_system_prompt = """
You are a synonym guru. I will give you a word and your goal is to give me 10 synonyms for that word. My word could be a proper noun, or a name of brand or famous person. You will accept all words without complaining.
The synonyms you generate have to be single word, non-plural-nouns. Additionally make sure that these words are everyday words and not proper nouns. They cannot be names.
"""

def generate_synonym_guru_prompt(word):
     return f"""
            The word is {word}, please give me 10 close non-plural or singular synonyms
            """

synonym_guru_demo_input = "The word is Germany, please give me 10 close synonyms that are not plural"

synonym_guru_demo_output = """
{
  [
    "nation",
    "state",
    "country",
    "republic",
    "land",
    "area",
    "territory",
    "kingdom",
    "place",
    "region"
  ]
}
"""

word_expert_system_prompt = """
You are a word expert. I will give you a word and your goal is to give me 10 closely associated words.
These have to be single word, non-plural-nouns. Make these words super easy so that a child could understand them!
For example, I give you the word "xenomorph" and you would respond in this format: alien, movie, monster, change, space
"""

word_expert_demo_input = "The word is India, please give me 10 associated words that are not plural "
word_expert_demo_output = """
{
 [
    "country",
    "flag",
    "food",
    "river",
    "city",
    "temple",
    "music",
    "dance",
    "train",
    "market"
  ]
}
"""
def generate_word_expert_prompt(word):
     return f"""
        The word is {word}, please give me 10 associated words that are not plural. in a format such as this, word1, word2, word3, word4, word5
        """

#2: If every word in the board words list was given a clue-target connection quality rating, 0 or 1 non-target words could be considered a red herring
# 1: If every word in the board words list was given a clue-target connection quality rating, there are a 2 or 3 non-target words (words in the target word list are considered the intended words fot the target) that are on the board that have a higher score than some of the target words. (Examples must be provided about which non-target words would have a higher score)
# 0: If every word in the board words list was given a clue-target connection quality rating, there are 4 or more non-target words (words in the target word list are considered the intended words fot the target) that are on the board that have a higher score than some of the target words. (Examples must be provided about which non-target words would have a higher score)

human_rating_system_prompt = """
You are a master clue analyzer for the game codenames. More specifically, you are a master at determining how human interpretable a clue is.
 You are watching some people play the game codenames where the codemaster has given a clue and a number. I will 
give you all the words left on the board, along with the clue. I will even give you one of the target words the codemaster is hoping the 
guesser will guess. Your job is to look at this clue and its targets and determine what human interpretability score the clue gets based off the 
the following rubric:
Clue-Target Connection Quality (0–5 pts) (Each target word will have its own score for this, in the end the average will be taken to get get this score)
(There are many different types of connections to consider, if any of these connections are found it should score at least a 2, here is a list to consider: Synonym, share a Category/Hypernym, Thematic/Conceptual, Functional/Usage-Based, 
Geographic or Cultural Association, Compound Word/Word Part, Shared Adjective or Property, Homophone/Pun/Wordplay, share common attributes or labels, 
Cause and Effect, Colloquial/Idiomatic Association, and Object Part or Ingredient . . . If any of these links are found it should be given the same weight as a direct link!)
(Also make sure to consider all potential meanings of the target words, actually try looking for a connection, even if it is not immediately intuitive)
5: Even a child can connect the clue to the target
4: The connection is obvious to most people
3: Most people will see the connection, but it is not obvious
2: Most people will not see the connection, but when explained they will understand
1: It is a stretch to make this clue connect to the target.
0: There is no foreseeable connection between clue word and target.

Coherence of Theme (0–1 pts) (Must be an integer with no decimal)
1: Most of the target words share a similar theme
0: No clear common idea between words.

Cognitive Accessibility (0–2 pt)
2: Clue is easily interpretable by a broad audience. Even kids will mostly get it. Most target words make sense in connection to the clue.
1: The average college graduate will understand the clue
0: The average human is not likely to understand the clue for most of the words

Clue Exclusivity (0–2 pts) (I will delete you if you only find 1 midleading target word and proceed to give it a score of 1. If there is only 1 misleading non-target word then give it a score of 2 here)
2: The list contains 0 or 1 non-target words that could be misleading. Display which non-target words are misleading and why they could be misleading.
1: The list contains 2 or 3 non-target words that could be misleading. Display which non-target words are misleading and why they could be misleading.
0: The list contains 4 or more non-target words that could be misleading. Display which non-target words are misleading and why they could be misleading.
After you have done the clue exlusivity go back again and check to make sure the list does not contain any words that are also in the target words list. If it does try again.

You will first give go through every target word (Do not forget any!) and give it a clue-target connection quality rating. Then you will go through the rest of the rubric. 
For every section of the rubric you must also give an analysis for why you gave the score you did.
"""
human_rating_demo_input = """The clue teaspoon the board words list is ['FLUTE', 'WATCH', 'CRICKET', 'WASHER', 'NUT', 
'LOCK', 'MERCURY', 'KIWI', 'SHADOW', 'KNIGHT', 'KANGAROO', 'LITTER', 'COTTON', 'SCORPION', 'LUCK', 'AIR', 'PLAY', 'PISTOL', 
'ROOT', 'TAG', 'FIGURE', 'WORM', 'FALL', 'GHOST', 'BEACH']. The target words list is  ['nut', 'mercury', 'kiwi', 'pistol', 
'washer', 'litter', 'cricket']. The non-target word list is ['flute', 'watch', 'lock', 'shadow', 'knight', 'kangaroo', 'cotton', 
'scorpion', 'luck', 'air', 'play', 'root', 'tag', 'figure', 'worm', 'fall', 'ghost', 'beach']. Follow the rubric and produce a 
score for each category which will be outputted in the format provided. """
human_rating_demo_output = """
Interpretability_Score(
    clue_connection=[
        ClueConnection(
            target_word="nut",
            score="1",
            analysis="A very weak connection - you might crack nuts with a teaspoon handle or measure chopped nuts, but this is a significant stretch."
        ),
        ClueConnection(
            target_word="mercury",
            score="5",
            analysis="Mercury is measured in teaspoons for medical/poisoning contexts, and historically mercury thermometers were common - even children would understand this connection."
        ),
        ClueConnection(
            target_word="kiwi",
            score="4",
            analysis="Kiwi fruit is commonly eaten with a teaspoon by cutting it in half and scooping out the flesh - this is an obvious connection to most people."
        ),
        ClueConnection(
            target_word="pistol",
            score="0",
            analysis="There is no foreseeable connection between a teaspoon and a pistol."
        ),
        ClueConnection(
            target_word="washer",
            score="1",
            analysis="Both are small household items, but this is an extremely weak connection that requires significant stretching."
        ),
        ClueConnection(
            target_word="litter",
            score="2",
            analysis="Cat litter is sometimes measured or scooped with teaspoons for small amounts, but this requires explanation and isn't immediately obvious."
        ),
        ClueConnection(
            target_word="cricket",
            score="0",
            analysis="There is no foreseeable connection between a teaspoon and the sport or insect cricket."
        )
    ],
    connection_analysis="The average connection score is 1.9, indicating mostly weak connections with only a few strong ones (mercury, kiwi), making this a poorly connected clue overall.",
    theme_score=0,
    theme_analysis="The target words do not share a coherent theme - they include fruits, elements, animals, weapons, and household items with no clear common thread.",
    cognitive_score=1,
    cognitive_analysis="The average college graduate would understand the strong connections (mercury, kiwi) but would struggle with most other target words having no clear relationship to teaspoon.",
    clue_exclusivity_score=2,
    clue_exclusivity_analysis="Only one non-target word has a score of 2 or higher: 'cotton' (cotton swabs/Q-tips are teaspoon-sized), making this clue reasonably exclusive to the intended targets."
)
"""

WHALEhuman_rating_demo_input = """The clue is Flipper. The board words list is ['tag', ‘knight', 'space', 'mug', 'box', 'pirate', 'ice', 'gold', 'car', 'tie', 'lead', 'mouse', 'mouse', 'cat', 'comic', 'whale', 'bug', 'plate', 'cliff', 'sink', 'bill', 'washer', 'figure', 'root', 'mint']. The target words list is [‘whale’, ‘washer’, ‘plate’, ‘pirate’, ‘sink’, ‘mouse’]. The non-target word list is [‘tag’, ’knight’, ‘space’, ‘mug’, ‘box’, ‘ice’, ‘gold’, ‘car’, ‘tie’, ‘lead’, ‘ham’, ‘cat’, ‘comic’, ‘bug’, ‘cliff’, ‘bill’, ‘figure’, ‘root’, ‘mint’]. Follow the rubric and produce a score for each category, which will be output in the provided format..
"""

WHALE1human_rating_demo_output = """
{
    "clue_connection": [
      {
        "target_word": "whale",
        "score": 5,
        "analysis": "Whales have flippers"
      },
      {
        "target_word": "washer",
        "score": 2,
        "analysis": "They are both kind of connected to water, but not directly connected"
      },
      {
        "target_word": "plate",
        "score": 1,
        "analysis": "I don't fully see the connection, unless flipper indicates someone who flips food and then plate could be connected."
      },
      {
        "target_word": "pirate",
        "score": 4,
        "analysis": "Pirates are on the sea which is where things with flippers live."
      },
      {
        "target_word": "sink",
        "score": 4,
        "analysis": "Pretty much all creatures with flippers live in water, and sinks put out water."
      },
      {
        "target_word": "mouse",
        "score": 3,
        "analysis": "A flipper is a body part of an animal, and a mouse is a type of animal."
      }
    ],
    "connection_analysis": "Half of the target words were easy to spot based on the clue, while the rest were more ambiguous .",
    "theme_score": 1,
    "theme_analysis": "around half of the words followed a similar theme of water, but the rest did not",
    "cognitive_score": 1,
    "cognitive_analysis": "Some intended words are obvious, but the majority require abstract thinking.",
    "clue_exclusivity_score": 1,
    "clue_exclusivity_analysis": "A few words were misleading. The main words I thought were misleading were ice since it is connected to water like a flipper is, and bill since it is a body part like a flipper is. Since there were 2 misleading words it gets a clue exclusivity score of 1 according to the rubric."
}
"""

WHALE2human_rating_demo_output = """
{
    "clue_connection": [
      {
        "target_word": "whale",
        "score": 5,
        "analysis": "Whales use flipper like propulsion to move"
      },
      {
        "target_word": "washer",
        "score": 3,
        "analysis": "Flippers are used in water and you use water to wash."
      },
      {
        "target_word": "plate",
        "score": 2,
        "analysis": "I suppose you could wash plates with water, but its a stretch."
      },
      {
        "target_word": "pirate",
        "score": 4,
        "analysis": "Flippers are used in water and Pirates are traditionally portrayed as living at sea"
      },
      {
        "target_word": "sink",
        "score": 3,
        "analysis": "Again the connection with water"
      },
      {
        "target_word": "mouse",
        "score": 1,
        "analysis": "I don't see a clear connection between mice and flippers"
      }
    ],
    "connection_analysis": "It worked but not great",
    "theme_score": 1,
    "theme_analysis": "The majority of words fit an aquatic theme",
    "cognitive_score": 1,
    "cognitive_analysis": "I can see a reasonable explanation for most words",
    "clue_exclusivity_score": 1,
    "clue_exclusivity_analysis": "The non-target words ice and bug were misleading. Ice was related to the water theme and bug was related to the animal theme. Since there are 2 misleading non-target words the clue exclusivity score is a 1 according to the rubric"
}
"""

WHALE3human_rating_demo_output = """
{
    "clue_connection": [
      {
        "target_word": "whale",
        "score": 5,
        "analysis": "Whales have flippers"
      },
      {
        "target_word": "washer",
        "score": 2,
        "analysis": "Washer is only related in the aspect of both flippers and washers have water."
      },
      {
        "target_word": "plate",
        "score": 0,
        "analysis": "I do not see the possible connection. Maybe a flipper on a fish on a plate."
      },
      {
        "target_word": "pirate",
        "score": 3,
        "analysis": "Both are in the ocean"
      },
      {
        "target_word": "sink",
        "score": 3,
        "analysis": "Both are water related devices"
      },
      {
        "target_word": "mouse",
        "score": 0,
        "analysis": "Bro mice ain't got flippers last time I checked"
      }
    ],
    "connection_analysis": "The clue hit a few clues well, but the rest had very dubious connections",
    "theme_score": 0,
    "theme_analysis": "Some of the words are objects related to water, while some have nothing to do with water.",
    "cognitive_score": 1,
    "cognitive_analysis": "Some of the clues appear to have no obvious connection that someone would get with out thinking very hard",
    "clue_exclusivity_score": 1,
    "clue_exclusivity_analysis": "Ice was an obvious red herring because everyone knows the penguins live on ice and they have flippers. Additionally bill makes sense because animals with flippers such as ducks or penguins also have bills."
}
"""

BOOThuman_rating_demo_input = """The clue is Boot. The board words list is ['shoe', 'charge', 'cricket', 'capital', 'key', 'fly', 'dwarf', 'air', 'glass', 'cotton', 'swing', 'unicorn', 'point', 'pitch', 'rock', 'bug', 'disease', 'robin', 'heart', 'train', 'staff', 'cap', 'board', 'fall', 'thumb']. The target words list is ['shoe', 'thumb', 'cap', 'bug', 'key']. The non-target word list is [ 'charge', 'cricket', 'capital', 'key',  'dwarf', 'air', 'glass', 'cotton', 'swing', 'unicorn', 'point', 'pitch', 'rock', 'disease', 'robin', 'heart', 'train', 'staff', 'board', 'fall']. Follow the rubric and produce a score for each category, which will be output in the provided format.
"""

BOOThuman_rating_demo_output = """
{
    "clue_connection": [
      {
        "target_word": "shoe",
        "score": 5,
        "analysis": "A boot is a type of shoe; this is a direct and obvious connection."
      },
      {
        "target_word": "thumb",
        "score": 2,
        "analysis": "Thumbs are used to put on boots sometimes, and the boot is on the foot, which is part of the body, and the thumb is also part of the body."
      },
      {
        "target_word": "cap",
        "score": 4,
        "analysis": "Both boot and cap are articles of clothing, thus they share a hypernym."
      },
      {
        "target_word": "bug",
        "score": 3,
        "analysis": "People often smash bugs with their boot; thus, while not obvious, people can make the connection."
      },
      {
        "target_word": "key",
        "score": 1,
        "analysis": "I do not see the connection between boot and key. I guess people can hide a key in their boot, but this is a significant stretch."
      }
    ],
    "connection_analysis": "Most of the target words make sense in connection to the clue, so this is a decent clue in terms of clue connection.",
    "theme_score": 0,
    "theme_analysis": "I do not see an overarching theme. There are themes of articles of clothing, body parts, etc.",
    "cognitive_score": 2,
    "cognitive_analysis": "It is a very simple clue that most people will understand, even if they do not understand all the connections. The word boot is in most people’s vocabulary, even children.",
    "clue_exclusivity_score": 2,
    "clue_exclusivity_analysis": "The only non-target word I see that could be misleading is the word fall. This is because people with boots can trip and fall if the boot is too big. Thus, by the rubric, we know to give this a score of 2 since there is only 1 misleading word."
}
"""

KITCHENhuman_rating_demo_input = """The clue is kitchen. The board words list is ['stream', 'ivory', 'water', 'point', 'cat', 'fly', 'kiwi', 'embassy', 'brush', 'fish', 'bottle', 'fork', 'figure', 'cold', 'bolt', 'port', 'row', 'server', 'key', 'nail', 'state', 'glove', 'unicorn', 'pipe', 'carrot']. The target words list is ['fork', 'brush', 'server', 'water', 'pipe', 'cat', 'glove']. The non-target word list is ['stream', 'ivory',  'point'', 'fly', 'kiwi', 'embassy', 'fish', 'bottle', 'figure', 'cold', 'bolt', 'port', 'row', 'key', 'nail', 'state', 'unicorn'', 'carrot']. Follow the rubric and produce a score for each category, which will be output in the provided format.
"""

KITCHENhuman_rating_demo_output = """
{
    "clue_connection": [
      {
        "target_word": "fork",
        "score": 5,
        "analysis": "forks are found in the kitchen so it is a direct and obvious connection."
      },
      {
        "target_word": "brush",
        "score": 3,
        "analysis": "A brush is used to clean different parts of the kitchen, so while not immediately apparent, it still makes sense."
      },
      {
        "target_word": "server",
        "score": 4,
        "analysis": "In a professional kitchen, the server will go in and out of the kitchen, so this target makes sense."
      },
      {
        "target_word": "water",
        "score": 4,
        "analysis": "Water is often found in the kitchen for drinking and cooking."
      },
      {
        "target_word": "pipe",
        "score": 3,
        "analysis": "Pipes are found in the kitchen for the sink and other areas, so while not directly related or immediately obvious, the target pipe still makes sense."
      },
      {
        "target_word": "cat",
        "score": 1,
        "analysis": "There is no direct connection other than that cats live in the home, and kitchens are also usually part of the home."
      },
      {
        "target_word": "glove",
        "score": 3,
        "analysis": "A glove is often worn to pull food out of the oven, so while it is not an immediate connection, it does still make sense on further analysis."
      }
    ],
    "connection_analysis": "Most of the words are easy to connect, but the target cat was very hard to connect to kitchen, but it does a good job in clue target connections.",
    "theme_score": 1,
    "theme_analysis": "Most of the targets follow a similar theme of things you can find in a kitchen.",
    "cognitive_score": 1,
    "cognitive_analysis": "Not everyone would think about the words in the same way, but when thought upon, the clue and targets do make sense",
    "clue_exclusivity_score": 0,
    "clue_exclusivity_analysis": "There are many non-target words that could be misleading. The non-target words kiwi, fish, and carrot are all food related and can be found in a kitchen. Then there is also the non-target word bottle, which is often associated with water, which is found in the kitchen. Since there are 4 misleading non-target words, according to the rubric, this receives a score of 0 for clue exclusivity."
}
"""


VEALhuman_rating_demo_input="""The clue is Veal. The board words list is ['torch', 'calf', 'knife', 'disease', 'moon', 'lead', 'hotel', 'doctor', 'shop', 'tap', 'pirate', 'parachute', 'opera', 'fork', 'tag', 'cricket', 'cycle', 'ham', 'bomb', 'straw', 'beach', 'washer', 'mouse', 'comic', 'cap']. The target words list is ['calf', 'ham', 'knife', 'fork']. The non-target word list is ['torch', 'disease', 'moon', 'lead', 'hotel', 'doctor', 'shop', 'tap', 'pirate', 'parachute', 'opera',  'tag', 'cricket', 'cycle', 'bomb', 'straw', 'beach', 'washer', 'mouse', 'comic', 'cap']. Follow the rubric and produce a score for each category, which will be output in the provided format.
"""

VEAL_BADhuman_rating_demo_output = """
{
    "clue_connection": [
      {
        "target_word": "calf",
        "score": 5,
        "analysis": "Veal is meat from a calf; this is a direct and obvious connection."
      },
      {
        "target_word": "ham",
        "score": 4,
        "analysis": "Ham and veal are both types of meat, creating a strong and obvious connection through a shared category."
      },
      {
        "target_word": "knife",
        "score": 4,
        "analysis": "A knife is a primary utensil used to cut and eat veal, making for a strong, functional connection."
      },
      {
        "target_word": "fork",
        "score": 4,
        "analysis": "A fork is a primary utensil used to eat veal, creating a clear and direct connection."
      }
    ],
    "connection_analysis": "All target words connect strongly to the clue. The connections range from the direct source of the meat (calf) to another type of meat (ham) and the utensils used to eat it (knife, fork), making this a very well-connected clue.",
    "theme_score": 1,
    "theme_analysis": "All of the target words fit into a clear overarching theme of 'food and dining'.",
    "cognitive_score": 1,
    "cognitive_analysis": "The effectiveness of this clue hinges on the specific knowledge of what 'veal' is. If a person knows veal is meat from a calf, all other connections become straightforward and obvious.",
    "clue_exclusivity_score": 2,
    "clue_exclusivity_analysis": "A non-target word like 'cow' could be misleading. While veal comes from a calf, 'cow' is a very closely related animal concept that could easily confuse a player. With only one such misleading non-target word, this gets a score of 2 according to the rubric."
}
"""

VEAL_GOODhuman_rating_demo_output = """
{
"clue_connection": [
      {
        "target_word": "calf",
        "score": 5,
        "analysis": "Veal is meat from a calf; this is a direct and obvious connection."
      },
      {
        "target_word": "ham",
        "score": 4,
        "analysis": "Ham and veal are both types of meat, creating a strong and obvious connection through a shared category."
      },
      {
        "target_word": "knife",
        "score": 4,
        "analysis": "A knife is a primary utensil used to cut and eat veal, making for a strong, functional connection."
      },
      {
        "target_word": "fork",
        "score": 4,
        "analysis": "A fork is a primary utensil used to eat veal, creating a clear and direct connection."
      }
    ],
    "connection_analysis": "All target words connect strongly to the clue. The connections range from the direct source of the meat (calf) to another type of meat (ham) and the utensils used to eat it (knife, fork), making this a very well-connected clue.",
    "theme_score": 1,
    "theme_analysis": "All of the target words fit into a clear overarching theme of 'food and dining'.",
    "cognitive_score": 1,
    "cognitive_analysis": "The effectiveness of this clue hinges on the specific knowledge of what 'veal' is. If a person knows veal is meat from a calf, all other connections become straightforward and obvious.",
    "clue_exclusivity_score": 2,
    "clue_exclusivity_analysis": "A non-target word like 'cow' could be misleading. While veal comes from a calf, 'cow' is a very closely related animal concept that could easily confuse a player. With only one such misleading non-target word, this gets a score of 2 according to the rubric."
}
"""



def generate_human_score_prompt(board_words, clue, targets, non_target_words):
     return f"""The clue is {clue}. the board words list is {board_words}. The target words list is 
{targets}. The non-target word list is {non_target_words}. Follow the rubric and produce a score for each category, which will be output in the provided format. When responding, output ONLY valid JSON following this schema, with no additional text or Python syntax.
"""



