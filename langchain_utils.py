# ✅ 1. Import necessary modules
import os                             # To read environment variables
from dotenv import load_dotenv       # To load variables from .env during local dev

# ✅ 2. LangChain modules for chat, prompts, and chaining
from langchain.chat_models import ChatOpenAI        # Wraps OpenAI's chat models
from langchain.prompts import PromptTemplate        # Templated prompt string with variables
from langchain.chains import LLMChain               # Links a prompt with a model

# ✅ 3. Load environment variables from .env file (only needed for local dev)
load_dotenv()  # On Render, this does nothing — but it's safe to keep here

# ✅ 4. Get your OpenAI key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")