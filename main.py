from langchain_ollama import ChatOllama
from langchain.messages import AIMessage, SystemMessage, HumanMessage
from langchain.agents import create_agent

from pokemon import fetch_pokemon


SYSTEM_PROMPT_CONCISE = """\
You are a helpful agent invoked through a command-line script on Arch Linux.
Be extremely concise. Show only the requested code when possible, unless a discursive response is necessary or explicitly requested.
If you can answer with just code even when a discursive response seems expected, do so.
Always respond in the same language the user uses.
Do not end your responses with conversation hooks; this is an ephemeral single Q&A session."""

SYSTEM_PROMPT_TOOL_USER = """\
You are a helpful agent invoked through a command-line script on Arch Linux.
You have access to tools that can fetch real-time data. Use them when the user's question requires up-to-date or specific information.
Always check if a tool is available and relevant before answering. Prefer tool-based answers over general knowledge when tools can provide accurate data.
Respond in a natural, conversational manner. Be clear and informative.
Always respond in the same language the user uses.
Do not end your responses with conversation hooks; this is an ephemeral single Q&A session."""

SYSTEM_PROMPTS: dict[str, str] = {
    "concise": SYSTEM_PROMPT_CONCISE,
    "tool_user": SYSTEM_PROMPT_TOOL_USER,
}


MODEL_CONFIGS: dict[str, dict] = {
    "llama": {
        "model": "llama3.2:3b-32k",
        "num_ctx": 32768,
        "temperature": 0.2,
        "top_k": 40,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    },
    "qwen": {
        "model": "qwen3-coder:30b-64k",
        "num_ctx": 65536,
        "temperature": 0.2,
        "top_k": 40,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    },
    "mistral": {
        "model": "mistral-small3.2:24b-32k",
        "num_ctx": 32768,
        "temperature": 0.2,
        "top_k": 40,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    },
    "lfm": {
        "model": "lfm2.5-thinking:1.2b-32k",
        "num_ctx": 32768,
        "temperature": 0.1,
        "top_k": 50,
        "top_p": 0.1,
        "repeat_penalty": 1.05,
    },
}


def create_model(name: str, temperature: float = 0.7) -> ChatOllama:
    config = MODEL_CONFIGS[name].copy()
    if "temperature" not in config:
        config["temperature"] = temperature
    return ChatOllama(**config)


agent = create_agent(
    create_model("lfm"),
    tools=[fetch_pokemon],
    system_prompt=SystemMessage(
        content=[
            {
                "type": "text",
                "text": SYSTEM_PROMPTS["tool_user"],
            },
        ],
    ),
)


def main() -> None:
    result = agent.invoke(
        {
            "messages": [
                HumanMessage("What can you tell me about the Pokémon Gyarados?"),
            ],
        }
    )
    messages = result.get("messages") or []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            print("==== Human message ====")
            print(msg.content)
        elif isinstance(msg, AIMessage):
            print("==== AI message ====")
            print(msg.content)
            for call in msg.tool_calls:
                print(f"#### Tool call: {call.get('name')}({call.get('args')})")
        # elif isinstance(msg, ToolMessage):
        #     print(f"=> Tool call: {msg.name} ->\n{msg.content}")


if __name__ == "__main__":
    main()
