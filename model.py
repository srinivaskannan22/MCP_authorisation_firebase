
from pydantic import BaseModel
class PromptRequest(BaseModel):
    user_prompt: str

class usermodel(BaseModel):
    name:str
    email:str
    password:str  

class loginmodel(BaseModel):
    email:str
    password:str   