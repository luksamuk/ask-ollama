from langchain.tools import tool

import requests


@tool
def fetch_pokemon_basic(pokemon_name: str) -> str:
    """Fetch basic information about a Pokémon (name, types, height, weight, abilities).

    Args:
        pokemon_name (str): the name of the Pokémon in lowercase.
    """
    print(f"DEBUG: Fetching basic info for {pokemon_name}...")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
        if r.status_code != 200:
            return f"Error: HTTP {r.status_code}"

        j = r.json()
        name = j["name"].capitalize()
        types = [t["type"]["name"] for t in j["types"]]
        abilities = [a["ability"]["name"] for a in j["abilities"]]
        height = j["height"] / 10  # decimeters to meters
        weight = j["weight"] / 10  # hectograms to kg

        return f"""\
Name: {name}
Types: {", ".join(types)}
Height: {height}m
Weight: {weight}kg
Abilities: {", ".join(abilities)}"""
    except Exception as e:
        return f"Error: {e}"


@tool
def fetch_pokemon_stats(pokemon_name: str) -> str:
    """Fetch base stats of a Pokémon (HP, Attack, Defense, etc.).

    Args:
        pokemon_name (str): the name of the Pokémon in lowercase.
    """
    print(f"DEBUG: Fetching stats for {pokemon_name}...")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
        if r.status_code != 200:
            return f"Error: HTTP {r.status_code}"

        j = r.json()
        name = j["name"].capitalize()
        stats = {s["stat"]["name"]: s["base_stat"] for s in j["stats"]}

        total = sum(stats.values())

        return f"""\
{name} Base Stats:
HP: {stats.get("hp", 0)}
Attack: {stats.get("attack", 0)}
Defense: {stats.get("defense", 0)}
Special Attack: {stats.get("special-attack", 0)}
Special Defense: {stats.get("special-defense", 0)}
Speed: {stats.get("speed", 0)}
Total: {total}"""
    except Exception as e:
        return f"Error: {e}"


@tool
def fetch_pokemon_moves(pokemon_name: str, limit: int = 20) -> str:
    """Fetch moves that a Pokémon can learn.

    Args:
        pokemon_name (str): the name of the Pokémon in lowercase.
        limit (int): maximum number of moves to return (default 20).
    """
    print(f"DEBUG: Fetching moves for {pokemon_name}...")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
        if r.status_code != 200:
            return f"Error: HTTP {r.status_code}"

        j = r.json()
        name = j["name"].capitalize()
        moves = [m["move"]["name"] for m in j["moves"][:limit]]

        return f"""\
{name} can learn {len(j["moves"])} moves total.
First {limit} moves:
{chr(10).join(f"  - {m}" for m in moves)}"""
    except Exception as e:
        return f"Error: {e}"


@tool
def fetch_pokemon_evolution(pokemon_name: str) -> str:
    """Fetch evolution chain for a Pokémon species.

    Args:
        pokemon_name (str): the name of the Pokémon species in lowercase.
    """
    print(f"DEBUG: Fetching evolution for {pokemon_name}...")
    try:
        # First get species to find evolution chain URL
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name}/")
        if r.status_code != 200:
            return f"Error: HTTP {r.status_code}"

        j = r.json()
        evo_chain_url = j["evolution_chain"]["url"]

        # Get evolution chain
        r = requests.get(evo_chain_url)
        if r.status_code != 200:
            return f"Error fetching evolution chain: HTTP {r.status_code}"

        chain = r.json()["chain"]

        def format_chain(link, depth=0):
            species = link["species"]["name"].capitalize()
            indent = "  " * depth
            result = f"{indent}- {species}"

            if link["evolution_details"]:
                details = link["evolution_details"][0]
                conditions = []
                if details.get("min_level"):
                    conditions.append(f"Level {details['min_level']}")
                if details.get("item"):
                    conditions.append(f"{details['item']['name']}")
                if details.get("trigger"):
                    conditions.append(f"{details['trigger']['name']}")
                if conditions:
                    result += f" (evolves via: {', '.join(conditions)})"

            for next_link in link.get("evolves_to", []):
                result += "\n" + format_chain(next_link, depth + 1)

            return result

        return f"Evolution Chain:\n{format_chain(chain)}"
    except Exception as e:
        return f"Error: {e}"


@tool
def fetch_ability_details(ability_name: str) -> str:
    """Fetch detailed information about a Pokémon ability.

    Args:
        ability_name (str): the name of the ability in lowercase.
    """
    print(f"DEBUG: Fetching ability details for {ability_name}...")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/ability/{ability_name}/")
        if r.status_code != 200:
            return f"Error: HTTP {r.status_code}"

        j = r.json()

        # Get English name and effect
        name = next(
            (n["name"] for n in j["names"] if n["language"]["name"] == "en"),
            ability_name,
        )
        effect = next(
            (
                e["short_effect"]
                for e in j["effect_entries"]
                if e["language"]["name"] == "en"
            ),
            "No effect description available.",
        )

        # Get Pokémon with this ability
        pokemon_list = [p["pokemon"]["name"] for p in j["pokemon"][:10]]

        return f"""\
Ability: {name}
Effect: {effect}
Pokémon with this ability: {", ".join(pokemon_list)}"""
    except Exception as e:
        return f"Error: {e}"


@tool
def fetch_type_effectiveness(type_name: str) -> str:
    """Fetch type effectiveness (weaknesses, resistances, immunities).

    Args:
        type_name (str): the name of the type in lowercase.
    """
    print(f"DEBUG: Fetching type effectiveness for {type_name}...")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/type/{type_name}/")
        if r.status_code != 200:
            return f"Error: HTTP {r.status_code}"

        j = r.json()
        dr = j["damage_relations"]

        double_damage_from = [t["name"] for t in dr["double_damage_from"]]
        half_damage_from = [t["name"] for t in dr["half_damage_from"]]
        no_damage_from = [t["name"] for t in dr["no_damage_from"]]
        double_damage_to = [t["name"] for t in dr["double_damage_to"]]
        half_damage_to = [t["name"] for t in dr["half_damage_to"]]

        return f"""\
{type_name.capitalize()} Type:

Weak to (2x damage): {", ".join(double_damage_from) or "None"}
Resistant to (0.5x damage): {", ".join(half_damage_from) or "None"}
Immune to (0x damage): {", ".join(no_damage_from) or "None"}

Super effective against (2x): {", ".join(double_damage_to) or "None"}
Not very effective against (0.5x): {", ".join(half_damage_to) or "None"}"""
    except Exception as e:
        return f"Error: {e}"


@tool
def fetch_move_details(move_name: str) -> str:
    """Fetch detailed information about a Pokémon move.

    Args:
        move_name (str): the name of the move in lowercase.
    """
    print(f"DEBUG: Fetching move details for {move_name}...")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/move/{move_name}/")
        if r.status_code != 200:
            return f"Error: HTTP {r.status_code}"

        j = r.json()

        name = next(
            (n["name"] for n in j["names"] if n["language"]["name"] == "en"), move_name
        )
        effect = next(
            (
                e["short_effect"]
                for e in j["effect_entries"]
                if e["language"]["name"] == "en"
            ),
            "No effect description.",
        )

        accuracy = j.get("accuracy", "—")
        power = j.get("power", "—")
        pp = j.get("pp", "—")
        priority = j.get("priority", 0)

        return f"""\
Move: {name}
Type: {j["type"]["name"].capitalize()}
Category: {j["damage_class"]["name"].capitalize()}
Power: {power}
Accuracy: {accuracy}
PP: {pp}
Priority: {priority}
Effect: {effect}"""
    except Exception as e:
        return f"Error: {e}"


@tool
def fetch_pokemon(pokemon_name: str) -> str:
    """Fetch comprehensive information about a Pokémon.
    This combines basic info, stats, and abilities into one response.

    Args:
        pokemon_name (str): the name of the Pokémon in lowercase.
    """
    print(f"DEBUG: Fetching comprehensive info for {pokemon_name}...")
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/")
        if r.status_code != 200:
            return f"Error: HTTP {r.status_code}"

        j = r.json()
        name = j["name"].capitalize()
        types = [t["type"]["name"] for t in j["types"]]
        abilities = [a["ability"]["name"] for a in j["abilities"]]
        height = j["height"] / 10
        weight = j["weight"] / 10

        stats = {s["stat"]["name"]: s["base_stat"] for s in j["stats"]}
        total_stats = sum(stats.values())

        # Get first few abilities with descriptions
        ability_details = []
        for ability_name in abilities[:3]:
            try:
                r = requests.get(f"https://pokeapi.co/api/v2/ability/{ability_name}/")
                if r.status_code == 200:
                    aj = r.json()
                    effect = next(
                        (
                            e["short_effect"]
                            for e in aj["effect_entries"]
                            if e["language"]["name"] == "en"
                        ),
                        "No description.",
                    )
                    ability_details.append(f"  - {ability_name}: {effect}")
            except:
                ability_details.append(f"  - {ability_name}")

        return f"""\
{name}
Types: {", ".join(types)}
Height: {height}m | Weight: {weight}kg

Base Stats:
  HP: {stats.get("hp", 0)} | Attack: {stats.get("attack", 0)} | Defense: {stats.get("defense", 0)}
  Sp. Attack: {stats.get("special-attack", 0)} | Sp. Defense: {stats.get("special-defense", 0)} | Speed: {stats.get("speed", 0)}
  Total: {total_stats}

Abilities:
{chr(10).join(ability_details)}"""
    except Exception as e:
        return f"Error: {e}"
