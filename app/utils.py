import os
from dotenv import load_dotenv
# from langchain.chains import llm
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchResults
import re
import json
import ast


load_dotenv()


gq_key = os.getenv("GROQ_API_KEY ")

# Initialize Groq LLM
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=gq_key
)

search = DuckDuckGoSearchResults(output_format="json")


def extract_json_from_response(text: str) -> dict:
    """
    Parses a variety of LLM outputs into a valid Python dictionary.
    Args:
        text (str): LLM output string that should represent a JSON/dict object.
    Returns:
        dict: Parsed Python dictionary.
    Raises:
        ValueError: If the input cannot be parsed into a dictionary.
    """
    # Trim and clean up common LLM issues
    text = text.strip()

    # Remove code block markers if present
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE).strip()

    # Try JSON decoding first
    try:
        return json.loads(text.replace("'", '"'))
    except json.JSONDecodeError:
        msg = "JSON Decode Error"

    # Try Python literal_eval
    try:
        result = ast.literal_eval(text)
        if isinstance(result, dict):
            return result
    except (SyntaxError, ValueError):
        msg = "Syntax Error, ast error"

    # Try extracting dictionary-like structure with regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return ast.literal_eval(match.group())
        except Exception:
            msg = "Regex Error"

    raise ValueError("Unable to parse LLM output into JSON in agent due " + msg)