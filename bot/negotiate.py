import requests
import os
import json
from typing import Dict, Any, Optional

from langchain.agents import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import AgentExecutor
from dotenv import load_dotenv

# --- Load Environment Variables ---
# Assumes a .env file in the project root with OPENAI_API_KEY
load_dotenv()

# --- Tool Definition ---
# This defines the custom tool that the LangChain agent can use.
@tool
def recommend_price(product_id: int, min_margin: Optional[float] = None, max_competitor_gap: Optional[float] = None) -> str:
    """
    Calls the pricing API to get a recommended price for a product.
    You can provide constraints like 'min_margin' (e.g., 0.2 for 20%) or
    'max_competitor_gap' (e.g., 0.1 for 10% more than competitor).
    """
    api_url = "http://api:8000/api/v1/recommend_price"
    print(f"Calling pricing tool for product_id: {product_id} with constraints...")

    payload = {
        "product_id": product_id,
        "constraints": {}
    }
    if min_margin is not None:
        payload["constraints"]["min_margin"] = min_margin
    if max_competitor_gap is not None:
        payload["constraints"]["max_competitor_gap"] = max_competitor_gap

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.RequestException as e:
        return f"API call failed: {str(e)}"

# --- Agent Setup ---
def create_negotiation_agent():
    """
    Creates and returns a LangChain agent for price negotiation.
    """
    tools = [recommend_price]

    # Make sure OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set. Please add it to your .env file.")

    llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI pricing negotiation assistant. "
                   "Your goal is to help business managers find the optimal price for their products. "
                   "You should understand their requests in natural language and translate them into constraints for the `recommend_price` tool. "
                   "When you get a result from the tool, present it to the user in a clear and friendly way. "
                   "Always state the recommended price and the policy ID that generated it."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    llm_with_tools = llm.bind_tools(tools)

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )

    return AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Main Interaction Loop ---
if __name__ == "__main__":
    print("Starting AI Pricing Negotiator Chatbot...")
    print("Type 'exit' to end the conversation.")

    try:
        agent_executor = create_negotiation_agent()

        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                break

            response = agent_executor.invoke({"input": user_input})
            print(f"Assistant: {response['output']}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
