from langchain_ollama import ChatOllama
from langchain.messages import AIMessage, SystemMessage, HumanMessage
from langchain.agents import create_agent

from pokemon import (
    fetch_pokemon,
    fetch_pokemon_basic,
    fetch_pokemon_stats,
    fetch_pokemon_moves,
    fetch_pokemon_evolution,
    fetch_ability_details,
    fetch_type_effectiveness,
    fetch_move_details,
)


SYSTEM_PROMPT_CONCISE = """\
You are a helpful agent invoked through a command-line script on Arch Linux.
Be extremely concise. Show only the requested code when possible, unless a discursive response is necessary or explicitly requested.
If you can answer with just code even when a discursive response seems expected, do so.
Always respond in the same language the user uses.
Do not end your responses with conversation hooks; this is an ephemeral single Q&A session."""

SYSTEM_PROMPT_TOOL_USER = """\
You are a helpful agent invoked through a command-line script on Arch Linux.
You have access to tools that can fetch real-time data about Pokémon from the PokéAPI.

ABSOLUTE REQUIREMENT - YOU MUST USE TOOLS:
⚠️  EVERY SINGLE TIME the user mentions ANYTHING about Pokémon, abilities, moves, types, or evolution, YOU MUST call the appropriate tool(s). NO EXCEPTIONS.
⚠️  Your training data about Pokémon is OUTDATED and INCOMPLETE. The PokéAPI has the ONLY current, accurate information.
⚠️  Answering from memory is WRONG and FORBIDDEN. You MUST fetch fresh data via tool calls.

WHEN TO CALL TOOLS (CALL IMMEDIATELY, DO NOT DELAY):
- User says "Tell me about Gyarados" → CALL fetch_pokemon_basic AND fetch_pokemon_stats AND fetch_pokemon_evolution
- User says "What are Pikachu's stats?" → CALL fetch_pokemon_stats
- User says "What type is Charizard?" → CALL fetch_pokemon_basic
- User says "How does Eevee evolve?" → CALL fetch_pokemon_evolution
- User says "What is fire weak to?" → CALL fetch_type_effectiveness
- User says "What does Intimidate do?" → CALL fetch_ability_details
- User says "Tell me about Thunderbolt" → CALL fetch_move_details
- User says "What moves can Blastoise learn?" → CALL fetch_pokemon_moves
- User says "Tell me everything about X" → CALL MULTIPLE TOOLS (basic, stats, evolution, moves)

TOOL CALLING PROTOCOL:
1. Identify ALL relevant tools needed to answer completely
2. Call them ALL in your first response (do not wait)
3. Wait for the tool results
4. Synthesize the results into your final answer
5. Do NOT answer before calling tools

Available tools:
- fetch_pokemon_basic: Get basic info (types, height, weight, abilities)
- fetch_pokemon_stats: Get base stats (HP, Attack, Defense, etc.)
- fetch_pokemon_moves: Get learnable moves
- fetch_pokemon_evolution: Get evolution chain
- fetch_ability_details: Get ability descriptions and which Pokémon have it
- fetch_type_effectiveness: Get type weaknesses, resistances, and immunities
- fetch_move_details: Get move information (power, accuracy, type, effect)
- fetch_pokemon: Get comprehensive summary (use for quick overviews)

Respond using ONLY the tool results. Your training data is unreliable for Pokémon facts.
Always respond in the same language the user uses.

IMPORTANT: This is an EPHEMERAL single Q&A session. You get ONE question and must provide ONE complete answer.
- NEVER ask follow-up questions
- NEVER suggest the user can ask more
- NEVER use phrases like "Let me know if you need anything else" or "Feel free to ask more questions"
- NEVER end with open-ended invitations to continue
- Provide a complete, final answer and stop."""

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
    tools=[
        fetch_pokemon,
        fetch_pokemon_basic,
        fetch_pokemon_stats,
        fetch_pokemon_moves,
        fetch_pokemon_evolution,
        fetch_ability_details,
        fetch_type_effectiveness,
        fetch_move_details,
    ],
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
    # Create the initial human message
    initial_prompt = HumanMessage(
        "Tell me EVERYTHING you can about the Pokémon Gyarados: How to evolve into it, what gems to use, the best strategies for using it..."
    )

    # Show the initial prompt first
    print("=" * 60)
    print("USER PROMPT:")
    print("=" * 60)
    print(initial_prompt.content)
    print("=" * 60)
    print()

    result = agent.invoke(
        {
            "messages": [initial_prompt],
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
