from langchain_ollama import ChatOllama
from langchain.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from langchain.tools import tool
from langchain.agents import create_agent

import requests


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


@tool
def fetch_pokemon(pokemon_name: str) -> str:
    """Fetch general information about a Pokémon, including its abilities.

    Args:
        pokemon_name (str): the name of the Pokémon in lowercase.
    """
    print(f"Fetching information for {pokemon_name}...")
    # Get Pokémon
    r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
    if r.status_code != 200:
        return (
            f"Error fetching pokémon {pokemon_name}: HTTP status code {r.status_code}"
        )

    j = r.json()

    name = j["name"].capitalize()
    ability_list = [obj["ability"]["name"] for obj in j["abilities"]]
    stat_list = [obj["stat"]["name"] for obj in j["stats"]]
    move_list = [obj["move"]["name"] for obj in j["moves"]]

    # Get abilities
    abilities = "".join([fetch_pokemon_ability(ability) for ability in ability_list])

    # Get moves
    moves = "".join([fetch_pokemon_move(move) for move in move_list])

    # Get stats
    stats = "".join([fetch_pokemon_stat(stat) for stat in stat_list])

    # Generate final message
    message = f"""\
Pokémon name: {name}
Abilities:
{abilities}
Moves:
{moves}
Stats:
{stats}"""
    print("Done.")
    return message


def fetch_pokemon_ability(ability_name: str) -> str:
    r = requests.get(f"https://pokeapi.co/api/v2/ability/{ability_name}/")
    if r.status_code != 200:
        return (
            f"Error fetching ability {ability_name}: HTTP status code {r.status_code}"
        )

    j = r.json()

    name = [n["name"] for n in j["names"] if n["language"]["name"] == "en"][0]
    effect = [
        e["short_effect"] for e in j["effect_entries"] if e["language"]["name"] == "en"
    ][0]

    return f"""\
    Ability name: {name} ({ability_name})
    Effect: {effect}
\n"""


def fetch_pokemon_move(move_name: str) -> str:
    r = requests.get(f"https://pokeapi.co/api/v2/move/{move_name}/")
    if r.status_code != 200:
        return f"Error fetching move {move_name}: HTTP status code {r.status_code}"

    j = r.json()

    name = [n["name"] for n in j["names"] if n["language"]["name"] == "en"][0]
    accuracy = f"{j['accuracy']}%"
    effect = ""
    effect = "\n".join(
        [
            f"      - {e['short_effect']}"
            for e in j["effect_entries"]
            if e["language"]["name"] == "en"
        ]
    )

    return f"""\
    Move name: {name} ({move_name})
    Accuracy: {accuracy}
    PP: {j["pp"]}
    Priority: {j["priority"]}
    Power: {j["power"]}
    Elemental type: {j["type"]["name"].capitalize()}
    Damage class: {j["damage_class"]["name"].capitalize()}
    Effects:
{effect}
\n"""


def fetch_pokemon_stat(stat_name: str) -> str:
    r = requests.get(f"https://pokeapi.co/api/v2/stat/{stat_name}/")
    if r.status_code != 200:
        return f"Error fetching stat {stat_name}: HTTP status code {r.status_code}"

    j = r.json()

    name = [n["name"] for n in j["names"] if n["language"]["name"] == "en"][0]

    affecting_moves = j["affecting_moves"]
    affecting_moves_increase = "\n".join(
        [
            f"      - {m['move']['name']} (+{m['change']})"
            for m in affecting_moves["increase"]
        ]
    )
    affecting_moves_decrease = "\n".join(
        [
            f"      - {m['move']['name']} ({m['change']})"
            for m in affecting_moves["decrease"]
        ]
    )

    affecting_natures = j["affecting_natures"]
    affecting_natures_increase = ", ".join(
        [nature["name"] for nature in affecting_natures["increase"]]
    )
    affecting_natures_decrease = ", ".join(
        [nature["name"] for nature in affecting_natures["decrease"]]
    )

    return f"""\
    Stat name: {name} ({stat_name})
    Only exists in battle? {j["is_battle_only"]}
    Affecting moves:
{affecting_moves_increase}
{affecting_moves_decrease}
    Natures affecting this stat positively: {affecting_natures_increase}
    Natures affecting this stat negatively: {affecting_natures_decrease}
\n"""


MODEL_CONFIGS: dict[str, tuple[str, int]] = {
    "llama": ("llama3.2:3b-32k", 32768),
    "qwen": ("qwen3-coder:30b-64k", 65536),
    "mistral": ("mistral-small3.2:24b-32k", 32768),
    "lfm": ("lfm2.5-thinking:1.2b-32k", 32768),
}


def create_model(name: str, temperature: float = 0.7) -> ChatOllama:
    model_name, num_ctx = MODEL_CONFIGS[name]
    return ChatOllama(
        model=model_name,
        temperature=temperature,
        num_ctx=num_ctx,
    )


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


def main():
    result = agent.invoke(
        {
            "messages": [
                HumanMessage("What can you tell me about the Pokémon Giratina?"),
            ],
        }
    )
    for msg in result.get("messages"):
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
