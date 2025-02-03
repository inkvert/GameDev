import random
import json
from datetime import date
from enemies.enemies import DRAGON_AGE, DRAGON_PREFIXES
from items.item_constants import (
    item_prefixes, item_suffixes, item_materials, armour_types, jewellery_types, weapon_types, item_types
)
from config.game_constants import VERSION, MIN_WEIGHT, MAX_WEIGHT, MIN_POWER, MAX_POWER, SAVE_FILE
from config import save_utils



# =============================
#         MONSTER LOGIC
# =============================

def generate_monster():
    """Generates a random dragon monster."""
    return {
        "name": f"{random.choice(DRAGON_AGE)} {random.choice(DRAGON_PREFIXES)} Dragon",
        "level": 1,
        "health": 100,
        "base_damage": 10,
        "gold_drop": random.randint(50, 500),
        "xp_reward": random.randint(50, 500)
    }

# =============================
#         COMBAT SYSTEM
# =============================

def roll_damage(base_damage):
    """Calculates total damage based on base stats and a random roll."""
    return base_damage + random.randint(1, 10)

def attack(attacker, defender):
    """Handles an attack from one character to another."""
    damage = roll_damage(attacker["base_damage"])
    defender["health"] -= damage
    print(f"\n{attacker['name']} attacks {defender['name']} and deals \033[31m{damage}\033[0m damage!")
    print(f"{defender['name']} has \033[32m{max(defender['health'], 0)}\033[0m health remaining.")
    return defender["health"] <= 0  # Returns True if defender dies

def fight_monster(player):
    """Handles the fight loop between the player and a monster."""
    monster = generate_monster()
    print(f"\n{player['name']} encounters {monster['name']}!")

    while player["health"] > 0 and monster["health"] > 0:
        input("\nPress Enter to attack...")

        # Player attacks first
        if attack(player, monster):
            print(f"\n{monster['name']} has been defeated!\n")
            player["gold"] += monster["gold_drop"]
            player["xp"] += monster["xp_reward"]
            player["health"] += player["regen"]
            print(f"{player['name']} gained \033[33m{monster['gold_drop']}\033[0m gold and \033[35m{monster['xp_reward']}\033[0m XP.")
            print(f"{player['name']} regenerates \033[32m{player['regen']}\033[0m health.\n")
            item = generate_random_item()
            item_type = random.choice(["Weapon", "Armour", "Jewellery"])
            rolled_item = item[item_type]
            print(f"{player['name']} received \033[36m{rolled_item['name']}\033[0m as a drop!\n")
            player["inventory"].append({
                "name" : rolled_item["name"],
                "type" : item_type,
                "power" : rolled_item["power"]
            })
            return
        
        # Monster retaliates
        if attack(monster, player):
            print(f"\n{player['name']} has been defeated! Returning to Main Menu.\n")
            player["health"] = 100  # Reset player health after defeat
            return

# =============================
#        ITEM GENERATION
# =============================

def roll_item(dic):
    """Randomly rolls an item from a given dictionary with weighted probabilities."""
    roll = random.randint(MIN_WEIGHT, MAX_WEIGHT)
    cumulative = 0
    for item, details in dic.items():
        cumulative += details["weight"]
        if roll <= cumulative:
            return item, details["power"]
    return None, 0

def generate_random_item():
    """Generates a random weapon, armor, or jewelry with properties."""
    prefix, prefix_value = roll_item(item_prefixes)
    material, material_value = roll_item(item_materials)
    weapon, weapon_value = roll_item(weapon_types)
    armour, armour_value = roll_item(armour_types)
    jewellery, jewellery_value = roll_item(jewellery_types)
    suffix, suffix_value = roll_item(item_suffixes)
    
    random_power = random.randint(1, 10)
    
    # Generate full item names
    weapon_name = f"{prefix} {material} {weapon} of the {suffix}"
    armour_name = f"{prefix} {material} {armour} of the {suffix}"
    jewellery_name = f"{prefix} {material} {jewellery} of the {suffix}"

    return {
        "Weapon": {"name": weapon_name, "power": prefix_value + material_value + weapon_value + suffix_value + random_power},
        "Armour": {"name": armour_name, "power": prefix_value + material_value + armour_value + suffix_value + random_power},
        "Jewellery": {"name": jewellery_name, "power": prefix_value + material_value + jewellery_value + suffix_value + random_power}
    }


def show_inventory(player):
    """Displays player's inventory items."""
    print("\n=== Player Inventory ===")
    if not player["inventory"]:
        print("Your inventory is empty.")
        return

    for index, item in enumerate(player["inventory"], start=1):
        print(f"{index}. {item['name']} (Type: {item['type']}, Power: {item['power']})")
    
    print("\nEnter the number of an item to equip it, or press Enter to go back.")
    choice = input("Choose an item: ")

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(player["inventory"]):
            equip_item(player, index)
        else:
            print("Invalid selection.")


def equip_item(player, item_index):
    """Equips an item from the player's inventory."""
    item = player["inventory"].pop(item_index)  # Remove from inventory
    item_type = item["type"]

    # Equip the item in the correct slot
    player["equipped_items"][item_type.lower()] = {"name": item["name"], "power": item["power"]}
    print(f"\nEquipped {item['name']}! (Power: {item['power']})")

# =============================
#        GAME LOOP
# =============================

def main():
    """Main game loop with menu-driven options."""
    player = save_utils.load_player()

    print("\nWelcome to GameDev Project, Version", VERSION)
    print("---------------------------------------------------\n")
    print("   __ ,                                             ")
    print("  ,-| ~                        -_____               ")
    print(" ('||/__,   _                    ' | -,        ;    ")
    print("(( |||  |  < \, \\\/\\\/\\\  _-_   /| |  |`  _-_  \\\/\ ")
    print("(( |||==|  /-|| || || || || \\\  || |==|| || \\\ || | ")
    print(" ( / |  , (( || || || || ||/   ~|| |  |, ||/   || | ")
    print("  -____/   \/\\\ \\\ \\\ \\\ \\\,/   ~-____,  \\\,/  \\\/  ")
    print("                               (                    ")
    print("---------------------------------------------------\n")

    while True:
        print("=== Main Menu ===")
        print("1. Fight a Monster")
        print("2. Check Player Stats")
        print("3. Check Inventory")
        print("4. Collect Daily Reward")
        print("5. Change Name")
        print("6. Exit Game")

        choice = input("\nChoose an option: ")

        if choice == "1":
            fight_monster(player)
        elif choice == "2":
            show_stats(player)
        elif choice == "3":
            show_inventory(player)
        elif choice == "4":
            collect_daily_reward(player)
        elif choice == "5":
            change_name(player)
        elif choice == "6":
            save_utils.save_player(player)
            print("Game saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def show_stats(player):
    """Displays the player's stats."""
    print("\n=== Player Stats ===")
    print(f"Name: {player['name']}")
    print(f"Health: \033[32m{player['health']}\033[0m")
    print(f"Level: \033[34m{player['level']}\033[0m")
    print(f"EXP: \033[35m{player['xp']}\033[0m")
    print(f"Gold: \033[33m{player['gold']}\033[0m")
    print(f"Equipped Weapon: {player['equipped_items']['weapon']['name']} (Power: {player['equipped_items']['weapon']['power']})")
    print(f"Equipped Armour: {player['equipped_items']['armour']['name']} (Power: {player['equipped_items']['armour']['power']})")
    print(f"Equipped Jewellery: {player['equipped_items']['jewellery']['name']} (Power: {player['equipped_items']['jewellery']['power']})")
    print("--------------------------\n")

def collect_daily_reward(player):
    """Grants a daily reward if not already collected today."""
    today = date.today().isoformat()

    if player.get("last_daily") != today:
        player["gold"] += 20
        player["last_daily"] = today
        print("Daily reward collected! \033[33m+20\033[0m Gold")
    else:
        print("You have already collected today's reward.")

def change_name(player):
    """Prompts player input to change player name."""
    while True:
        print("1. Yes")
        print("2. No (Return to menu)")
        choice = input(f"Your current names ia {player['name']}. Would you like to change it?")
        if choice == "1":
            new_name =  input("What would like your name to be?")
            player["name"] = new_name
            print(f"Your new names is {player['name']}. Godspeed, {player['name']}. Returning to Main Menu.")
            break
        elif choice == "2":
            break
        else:
            print("Invalid choice. Please try again.")

# =============================
#        ENTRY POINT
# =============================

if __name__ == "__main__":
    main()