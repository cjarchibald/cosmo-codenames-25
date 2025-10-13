from pydantic import BaseModel, Field,field_validator

class WordList(BaseModel):
    word_list : list[str] = Field(...,description="A list of words that fits the criteria given earlier")
    @field_validator('word_list', mode='after')
    @classmethod
    def lowercase_words(cls, v):
        if isinstance(v, list):
            return [item.lower() if isinstance(item, str) else item for item in v]
        return v