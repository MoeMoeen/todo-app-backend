# ✅ 1. Import necessary modules
import os                             # To read environment variables
from dotenv import load_dotenv       # To load variables from .env during local dev
from pydantic import SecretStr

# # ✅ 2. LangChain modules for chat, prompts, and chaining
# from langchain_community.chat_models import ChatOpenAI       # Wraps OpenAI's chat models
# from langchain.prompts import PromptTemplate        # Templated prompt string with variables
# from langchain.chains import LLMChain               # Links a prompt with a model

# ✅ NEW Import Path for ChatOpenAI
from langchain_openai import ChatOpenAI

# ✅ PromptTemplate is still from core langchain
from langchain.prompts import PromptTemplate

# ✅ For chaining with | pipe syntax
from langchain_core.runnables import Runnable

# ✅ Load environment variables from .env file (only needed for local dev)
load_dotenv()  # On Render, this does nothing — but it's safe to keep here

# ✅ Get your OpenAI key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")


# Create the OpenAI chat model object with LangChain
llm = ChatOpenAI(
    model="gpt-4",          # You can switch to "gpt-4" if you need better reasoning
    temperature=0.7,                # Creativity control: 0 = strict, 1 = random
    api_key=SecretStr(openai_api_key)   # Secure API key injection
)

# ✅ Define a reusable PromptTemplate
priority_prompt = PromptTemplate.from_template("""
You are a productivity assistant. Your job is to help prioritize tasks.

Here is a list of tasks:
{tasks}

Return a numbered list of these tasks ordered from most to least important, with a short explanation for each.
Be helpful and concise.
""")

# Combine prompt and LLM into a chain object (Chain Prompt → LLM using the pipe syntax)
priority_chain: Runnable = priority_prompt | llm


# ✅ 8. Function to be used in our FastAPI route
def get_task_priorities(task_list: list[str]) -> str:
    """
    Given a list of tasks, use the LLM to return a prioritized and reasoned list.
    """
    formatted_tasks = "\n".join(f"- {task}" for task in task_list)  # Convert to string with bullet points
    result = priority_chain.invoke({"tasks": formatted_tasks})  # Fill prompt and run model
    return result.content # Extract the content from the result

#---Example usage (not part of the module)---
if __name__ == "__main__":
    # Example usage of the function
    # This is just for testing locally, not part of the module
    print(get_task_priorities(["Submit taxes", "Buy milk", "Prepare for client meeting"]))
