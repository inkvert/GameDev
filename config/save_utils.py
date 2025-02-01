from config.game_constants import SAVE_FILE
import os
import json
import random


def load_player():
    """Loads player data from a save file or initializes default stats."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Save file is corrupted. Resetting player data.")
    
    # Default player stats if no save file exists
    return {
        "name": input("Enter your character's name: "),
        "level": 1,
        "xp": 0,
        "gold": 0,
        "health": 100,
        "base_damage": 10,
        "regen": 80 + random.randint(1, 10),
        "equipped_items": {
            "weapon": {"name": "None", "power": 0},
            "armour": {"name": "None", "power": 0},
            "jewellery": {"name": "None", "power": 0}
        },
        "inventory" : []
        
    }

def save_player(player):
    """Saves player data to a JSON file."""
    with open(SAVE_FILE, "w") as file:
        json.dump(player, file, indent=4)