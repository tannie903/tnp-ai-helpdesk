from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()


def get_llm() -> ChatHuggingFace:
    """Create and return a ChatHuggingFace LLM instance.

    Returns:
        A ChatHuggingFace object wrapping a HuggingFaceEndpoint,
        ready to be used in LangChain chains.
    """
    endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        task="conversational",
        temperature=0.5,
        max_new_tokens=512,
    )
    return ChatHuggingFace(llm=endpoint)