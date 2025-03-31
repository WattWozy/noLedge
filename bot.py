# this Bot file includes an LLM to generate a response to the user input. 
# the idea is to populate a vector database, and pass it to the LLM as a context.


from huggingface_hub import login;
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import pipeline

login("<token>")

## tokenizer: load text into tokens, into vectors into a vector database (docker?)

## llm has to have access to the vector database. 

## user query must be converted into tokes, into vectors, and then passed to the llm, to query the vector database.

## vector database returns text to the llm who then returns a nl answer to the user. 

## to read: reasoning models. 