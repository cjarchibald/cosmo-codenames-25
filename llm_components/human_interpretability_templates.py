from pydantic import BaseModel, Field

class ClueConnection(BaseModel):
    target_word : str = Field(...,description="The target word that is linked to the clue.")
    score :str = Field(...,description="A score between 0 and 5 representing the strength of the connection.")
    analysis: str = Field(...,description="A sentence explaining why the connection works or does not work.")

class Interpretability_Score(BaseModel):
    clue_connection : list[ClueConnection] = Field(...,description="The list comparing the clue word to each target word.")
    connection_analysis : str = Field(...,description="A sentence explaining the overall connection quality following the rubric.")
    theme_score : int = Field(..., description="A number between 0 and 1 representing the theme coherence as discussed by the rubric.")
    theme_analysis : str = Field(...,description="A discussion on how the theme score makes sense given the rubric.")
    cognitive_score : int = Field(..., description="A number between 0 and 2 representing the cognitive accessibillity as discussed by the rubric.")
    cognitive_analysis : str = Field(...,description="A discussion on how the cognitive accessibility score makes sense given the rubric.")
    clue_exclusivity_score : int = Field(..., description="A number between 0 and 2 representing the clue exclusivity to only the target word, following the rubric")
    clue_exclusivity_analysis: str = Field(..., description="A discussion on how the clue exlusivity score makes sense given by the rubric")