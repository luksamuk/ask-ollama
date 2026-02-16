from langchain.tools import tool

import requests


@tool
def fetch_pokemon(pokemon_name: str) -> str:
    """Fetch general information about a Pokémon, including its abilities.

    Args:
        pokemon_name (str): the name of the Pokémon in lowercase.
    """
    print(f"DEBUG: Fetching information for {pokemon_name}...")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
        if r.status_code != 200:
            msg = f"Error fetching pokémon {pokemon_name}: HTTP status code {r.status_code}"
            print(f"DEBUG: {msg}")
            return msg

        j = r.json()

        name = j["name"].capitalize()
        ability_list = [obj["ability"]["name"] for obj in j["abilities"]]
        stat_list = [obj["stat"]["name"] for obj in j["stats"]]
        move_list = [obj["move"]["name"] for obj in j["moves"]]

        abilities = "".join(
            [fetch_pokemon_ability(ability) for ability in ability_list]
        )
        moves = "".join([fetch_pokemon_move(move) for move in move_list])
        stats = "".join([fetch_pokemon_stat(stat) for stat in stat_list])

        message = f"""\
Pokémon name: {name}
Abilities:
{abilities}
Moves:
{moves}
Stats:
{stats}"""
        print("DEBUG: Fetching done.")
        return message
    except Exception as e:
        msg = f"Error fetching pokémon {pokemon_name}: {e}"
        print(f"DEBUG: {msg}")
        return msg


def fetch_pokemon_ability(ability_name: str) -> str:
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/ability/{ability_name}/")
        if r.status_code != 200:
            return f"Error fetching ability {ability_name}: HTTP status code {r.status_code}"

        j = r.json()

        name = [n["name"] for n in j["names"] if n["language"]["name"] == "en"][0]
        effect = [
            e["short_effect"]
            for e in j["effect_entries"]
            if e["language"]["name"] == "en"
        ][0]

        return f"""\
    Ability name: {name} ({ability_name})
    Effect: {effect}
\n"""
    except Exception as e:
        print(f"Error fetching ability {ability_name}: {e}")
        return f"Error fetching ability {ability_name}: {e}"


def fetch_pokemon_move(move_name: str) -> str:
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/move/{move_name}/")
        if r.status_code != 200:
            return f"Error fetching move {move_name}: HTTP status code {r.status_code}"

        j = r.json()

        name = [n["name"] for n in j["names"] if n["language"]["name"] == "en"][0]
        accuracy = f"{j['accuracy']}%"
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
    except Exception as e:
        print(f"Error fetching move {move_name}: {e}")
        return f"Error fetching move {move_name}: {e}"


def fetch_pokemon_stat(stat_name: str) -> str:
    try:
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
    except Exception as e:
        print(f"Error fetching stat {stat_name}: {e}")
        return f"Error fetching stat {stat_name}: {e}"
