# cosmo-codenames-25
cosmo codenames agent for 2025 ieee cog codenames competition
[Codenames Competition Repo](https://github.com/stepmat/Codenames_GPT)

Bot developed by Christopher Archibald, Joseph Dahlke, Thomas Esplin, Olivia Leavitt, and Matthew Sheppard

## Bot Overview
Our bot employs a hybrid strategy combining large language model (LLM) capabilities with a static word embedding to balance vocabulary breadth with precise alignment between the codemaster and guesser. Both roles use a set of 13,000 static embeddings from ConceptNet Numberbatch to calculate cosine distances between words.  The codemaster evaluates thousands of candidate words to find those that are closest semantically to the most target team words while being far from other board words. Instead of always selecting the clue yielding the highest number of connections, we typically choose a 4–5 word clue paired with a complementary second clue, targeting a two turn completion time while preserving strong semantic ties. 

The guesser, using the same embeddings, works backward from the clue to identify the intended words. Additionally, the guesser can deduce that the next word that it would guess after the target words is not a team word, allowing it to be eliminated from consideration by both agents on the next turn.  For games against another team, the guesser intentionally guesses only part of the target set on turn one, saving the rest for turn two in order to keep more confounding words on the board for the opponent. A key challenge was handling out-of-vocabulary (OOV) words that are not included in the word embeddings. For this, we use a local LLM (Ollama Gemma3:4b) to substitute OOV words with semantically related known words.  A fixed random seed is employed so that the codemaster and guesser each use the same substitution.

## How To Use These Bots

### Setup the Competition Environment
1. Follow the steps in the link to the repo above to set up the competition code.
2. Then follow the [Bot Instructions](setup_helpers/Instructions_for_Competition_Files.pdf) to set up the bots properly in the competition framework.

### Get The Word Embeddings
To get the word embeddings go to [ConceptNet Numberbatch](https://github.com/commonsense/conceptnet-numberbatch) and download the Version 19.08 English-only embeddings. Then you want to filter it so you only keep the words located within the [Word List](arg_framework/actual-final-wl.txt). 

Once you have those filtered embeddings you will put them into the [ConceptNet Numberbatch Embeddings](arg_framework/cn_nb_word_vectors.txt). Use example pictures [Example Pic 1](setup_helpers/embedding_example1.png) and [Example Pic 2](setup_helpers/embedding_example2.png) for reference as to what the final result will look like.

### Get the Word Associations
Navigate to the [Associations Creator](setup_helpers/associations_creator.py) file and run it. Make sure to run it from the parent directory so the filepaths work as they are supposed to.

### Run the Bots
Now you should have everything set up! Run the bots using the [Bot Instructions](setup_helpers/Instructions_for_Competition_Files.pdf)!
