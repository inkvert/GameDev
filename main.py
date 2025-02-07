
"""GameDev - a loot rolling RPG, by Vader and ink."""

import random
import json
from datetime import date
from enemies.enemies import DRAGON_AGE, DRAGON_PREFIXES
from items.item_constants import (item_prefixes, item_suffixes, item_materials,
                                  armour_types, jewellery_types, weapon_types, item_types)
from config.game_constants import VERSION, MIN_WEIGHT, MAX_WEIGHT, MIN_POWER, MAX_POWER, SAVE_FILE
from config import save_utils

# =============================
#         MONSTER LOGIC
# =============================

def generate_monster(player):
    """Generates a random dragon monster."""
    monster_level = player["level"] + random.randint(0, 1)
    return {
        "name": f"{random.choice(DRAGON_AGE)} {random.choice(DRAGON_PREFIXES)} Dragon",
        "level": monster_level,
        "max_health": (monster_level*10)+90,
        "health": (monster_level*10)+90,
        "base_damage":  monster_level+9,
        "base_armour": monster_level,
        "base_crit_chance": 5,
        "base_crit_bonus": 50,
        "gold_drop": int(((random.randint(300, 500))/100)*(100+(monster_level*10))),
        "xp_reward": int(((random.randint(300, 500))/100)*(100+(monster_level*10))),
        "equipped_items": {
            "weapon": {
                "name": "None",
                "power": 0
            },
            "armour": {
                "name": "None",
                "power": 0
            },
            "jewellery": {
                "name": "None",
                "power": 0
            }
        }
    }

# =============================
#         COMBAT SYSTEM
# =============================

def roll_damage(attacker):
    """Calculates total damage based on base stats, equipped weapon and a random roll."""
    base_damage = attacker["base_damage"]
    weapon_power = attacker["equipped_items"]["weapon"]["power"]
    random_power = random.randint(0, int(weapon_power))
    random_base = random.randint(0, 10)
    return base_damage + random_power + random_base

def roll_defence(defender):
    """Calculates total damage reduction based on equipped armour."""
    base_defence = defender["base_armour"]
    armour_power = defender["equipped_items"]["armour"]["power"]
    random_power = random.randint(0, int(armour_power))
    return base_defence + random_power

def crit_chance (attacker):
    """Calculates critical hit chance."""
    base_crit_chance = attacker["base_crit_chance"]
    jewellery_power = attacker["equipped_items"]["jewellery"]["power"]
    jewellery_crit_chance = int(jewellery_power/3)
    return base_crit_chance + jewellery_crit_chance

def crit_bonus (attacker):
    """Calculates critical hit nous."""
    base_crit_bonus = attacker["base_crit_bonus"]
    jewellery_power = attacker["equipped_items"]["jewellery"]["power"]
    jewellery_crit_bonus = int(jewellery_power)
    return base_crit_bonus + jewellery_crit_bonus

def attack(attacker, defender):
    """Handles an attack from one character to another, and checks for critical hit/bonus."""
    crit_roll = crit_chance(attacker) + random.randint(1, 100)
    if crit_roll >= 100:
        damage_before_armour = int(((roll_damage(attacker))*(100+crit_bonus(attacker)))/100)
        damage = damage_before_armour - roll_defence(defender)
        if damage >= 0:
            pass
        else:
            damage = 0
        defender["health"] -= damage
        print(f"\n{attacker['name']} CRITS {defender['name']} "
              f"and deals \033[31m{damage:,}\033[0m damage!")
        print(f"{defender['name']} has "
              f"\033[32m{max(defender['health'], 0):,}\033[0m health remaining.")
        return defender["health"] <= 0  # Returns True if defender dies
    damage_before_armour = roll_damage(attacker)
    damage = damage_before_armour - roll_defence(defender)
    if damage >= 0:
        pass
    else:
        damage = 0
    defender["health"] -= damage
    print(f"\n{attacker['name']} attacks {defender['name']} "
            f"and deals \033[31m{damage:,}\033[0m damage!")
    print(f"{defender['name']} has "
          f"\033[32m{max(defender['health'], 0):,}\033[0m health remaining.")
    return defender["health"] <= 0  # Returns True if defender dies

def check_level_up(player):
    """Checks if conditions are met for player to level up and returns boolean."""
    xp_required = (player['level']**2)*100
    return player["xp"] >= xp_required

def level_up(player):
    """Performs changes required to level up player."""
    player["level"] += 1
    player["xp"] = 0
    print(f"{player['name']} levels up! {player["name"]} is now level {player["level"]:,}.\n")
    player["regen"] += 10
    player["base_damage"] += 1
    player["max_health"] += 10
    player["health"] =  player["max_health"]

def fight_monster(player):
    """Handles the fight loop between the player and a monster."""
    monster = generate_monster(player)
    print(f"\n{player['name']} encounters a level {monster['level']} {monster['name']}!")

    while player["health"] > 0 and monster["health"] > 0:
        input("\nPress Enter to attack...")
        # Player attacks first
        if attack(player, monster):
            print(f"\n{monster['name']} has been defeated!\n")
            player["gold"] += monster["gold_drop"]
            player["xp"] += monster["xp_reward"]
            health_regen = player["regen"]+random.randint (1, 10)
            player["health"] += health_regen
            if player["health"] > player["max_health"]:
                player["health"] = player["max_health"]
            print(f"{player['name']} gained \033[33m{monster['gold_drop']:,}\033[0m gold"
                  f" and \033[35m{monster['xp_reward']:,}\033[0m XP.")
            print(f"{player['name']} regenerates \033[32m{health_regen:,}\033[0m health.\n")
            item = generate_random_item(monster)
            item_type = random.choice(["Weapon", "Armour", "Jewellery"])
            rolled_item = item[item_type]
            print(f"{player['name']} received \033[36m{rolled_item['name']}\033[0m as a drop!")
            player["inventory"].append({
                "name" : rolled_item["name"],
                "type" : item_type,
                "power" : rolled_item["power"]
            })
            check_level_up(player)
            if check_level_up(player):
                level_up(player)
            return

        # Monster retaliates
        if attack(monster, player):
            print(f"\n{player['name']} has been defeated! Returning to Main Menu.\n")
            player["health"] = player["max_health"]  # Reset player health after defeat
            return

# =============================
#        ITEM GENERATION
# =============================

def roll_item(dic, monster):
    """Randomly rolls an item from a given dictionary with weighted probabilities."""
    roll = random.randint(MIN_WEIGHT, MAX_WEIGHT) + (monster["level"]*5)
    cumulative = 0
    for item, details in dic.items():
        cumulative += details["weight"]
        if roll <= cumulative:
            return item, details["power"]
    for item, details in dic.items():
        if details["weight"] == 1:
            return item, details["power"]
    return None, 0

def generate_random_item(monster):
    """Generates a random weapon, armor, or jewelry with properties."""
    prefix, prefix_value = roll_item(item_prefixes, monster)
    material, material_value = roll_item(item_materials, monster)
    weapon, weapon_value = roll_item(weapon_types, monster)
    armour, armour_value = roll_item(armour_types, monster)
    jewellery, jewellery_value = roll_item(jewellery_types, monster)
    suffix, suffix_value = roll_item(item_suffixes, monster)
    random_power = random.randint(MIN_POWER, MAX_POWER)

    # Generate full item names
    weapon_name = f"{prefix} {material} {weapon} of the {suffix}"
    armour_name = f"{prefix} {material} {armour} of the {suffix}"
    jewellery_name = f"{prefix} {material} {jewellery} of the {suffix}"

    return {
        "Weapon": {"name": weapon_name,
                   "power": prefix_value + material_value +
                            weapon_value + suffix_value + random_power},
        "Armour": {"name": armour_name,
                   "power": prefix_value + material_value +
                            armour_value + suffix_value + random_power},
        "Jewellery": {"name": jewellery_name,
                      "power": prefix_value + material_value +
                               jewellery_value + suffix_value + random_power}
    }

def show_inventory(player):
    """Displays player's inventory items."""
    while True:
        print("\n=== Player Inventory ===")
        if not player["inventory"]:
            print("\nYour inventory is empty.")
            return
        sorted_inventory = sorted(player["inventory"], key=lambda x: x['power'], reverse=True)
        for index, item in enumerate(sorted_inventory, start=1):
            print(f"{index}. {item['name']} (Type: {item['type']}, Power: {item['power']})")
        print(f"\nEquipped Weapon:\033[36m {player['equipped_items']['weapon']['name']}\033[0m "
              f"(Power: {player['equipped_items']['weapon']['power']})")
        print(f"Equipped Armour:\033[36m {player['equipped_items']['armour']['name']}\033[0m "
              f"(Power: {player['equipped_items']['armour']['power']})")
        print(f"Equipped Jewellery:\033[36m {player['equipped_items']['jewellery']['name']}\033[0m "
              f"(Power: {player['equipped_items']['jewellery']['power']})\n")
        print("Enter the number of an item to equip it, or press Enter to go back.\n")
        choice = input("Choose an item: ")
        if choice == "":
            break
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(sorted_inventory):
                item_to_equip = sorted_inventory[index]
                original_index = player["inventory"].index(item_to_equip)
                equip_item(player, original_index)
            else:
                print("Invalid selection.")

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

    print("\n----------------------------------------------------")
    print("Welcome to GameDev Project, Version", VERSION)
    print("----------------------------------------------------")
    print("    __ ,                                            ")
    print("  ,-| ~                        -_____               ")
    print(" ('||/__,   _                    ' | -,        ;    ")
    print("(( |||  |  < /, ////////  _-_   /| |  |`  _-_  // / ")
    print("(( |||==|  /-|| || || || || //  || |==|| || // || | ")
    print(" ( / |  , (( || || || || ||/   ~|| |  |, ||/   || | ")
    print("  -____/   //// // // // //,/   ~-____,  //,/  ///  ")
    print("                               (                    ")
    print("----------------------------------------------------")

    while True:
        print("\n=== Main Menu ===")
        print("1. Fight Monster")
        print("2. Player Stats")
        print("3. Inventory")
        print("4. Merchant")
        print("5. Disenchanter")
        print("6. Daily Reward")
        print("7. Change Name")
        print("8. Save Game")
        print("9. Save and Exit")

        choice = input("\nChoose an option (or press Enter to fight): ")

        if choice in ["1", ""]:
            fight_monster(player)
        elif choice == "2":
            show_stats(player)
        elif choice == "3":
            show_inventory(player)
        elif choice == "4":
            item_merchant(player)
        elif choice == "5":
            disenchanter(player)
        elif choice == "6":
            collect_daily_reward(player)
        elif choice == "7":
            change_name(player)
        elif choice == "8":
            save_utils.save_player(player)
            print("\nGame saved.\n")
        elif choice == "9":
            save_utils.save_player(player)
            print("\nGame saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def item_merchant(player):
    """Opens the item merchant."""
    print("\n=== Item Merchant ===")
    print("\nYou approach the hooded figure.")
    merchant_cost = 10000
    print(f"\nYou have \033[33m{player['gold']:,}\033[0m gold. "
          f"Buying an item costs \033[33m{merchant_cost:,}\033[0m gold.")
    while True:
        print("\n1. Yes")
        print("2. No (Return to menu)\n")
        choice = input("'Oh, stranger... are you buyin'?'")
        if choice == "2":
            return
        if choice != "1":
            print("\nInvalid choice. Please try again.")
            continue
        while True:
            if player['gold'] < merchant_cost:
                print("\n'Not enough gold, stranger...'")
                print("\nReturning to menu.\n")
                return
            player['gold'] -= merchant_cost
            monster = generate_monster(player)
            item = generate_random_item(monster)
            item_type = random.choice(["Weapon", "Armour", "Jewellery"])
            rolled_item = item[item_type]
            print("\n'Excellent choice, stranger... here you go.'")
            print(f"\n{player['name']} received \033[36m{rolled_item['name']}\033[0m!")
            print(f"\nYou now have \033[33m{player['gold']:,}\033[0m gold.")
            player["inventory"].append({
                "name": rolled_item["name"],
                "type": item_type,
                "power": rolled_item["power"]
            })
            print("\n1. Yes")
            print("2. No (Return to menu)")
            choice = input("\n'Are you buyin' again, stranger?'")
            if choice == "2":
                return
            if choice != "1":
                print("\nInvalid choice. Please try again.")
                break

def show_stats(player):
    """Displays the player's stats."""
    print("\n=== Player Stats ===")
    print(f"Name: {player['name']}")
    print(f"Level: \033[34m{player['level']:,}\033[0m")
    print(f"Health: \033[32m{player['health']:,}\033[0m")
    print(f"EXP: \033[35m{player['xp']:,}\033[0m")
    print(f"Gold: \033[33m{player['gold']:,}\033[0m\n")

    print(f"Base Damage: {player["equipped_items"]["weapon"]["power"] + player["base_damage"]}")
    print(f"Crit Chance: {crit_chance(player)}%")
    print(f"Crit Bonus: {crit_bonus(player)}%")
    print(f"Armour: {player["equipped_items"]["armour"]["power"]}\n")
    print(f"Equipped Weapon:\033[36m {player['equipped_items']['weapon']['name']}\033[0m "
          f"(Power: {player['equipped_items']['weapon']['power']})")
    print(f"Equipped Armour:\033[36m {player['equipped_items']['armour']['name']}\033[0m "
          f"(Power: {player['equipped_items']['armour']['power']})")
    print(f"Equipped Jewellery:\033[36m {player['equipped_items']['jewellery']['name']}\033[0m "
          f"(Power: {player['equipped_items']['jewellery']['power']})")
    print("--------------------------")

def disenchanter(player):
    """Opens the disenchanter."""
    print("\n=== Item Merchant ===")
    print("\nYou approach the old wizard.")
    while True:
        print("\n1. Yes")
        print("2. No (Return to menu)\n")
        choice = input("'Yes, yes, hello young one. Shall I disenchant your inventory?'")
        if choice == "1":
            total_power = sum(item["power"] for item in player["inventory"])
            items_count = len(player["inventory"])
            gold_reward = total_power*20
            player["gold"] += gold_reward
            player["inventory"].clear()
            print("\nThe wizard casts a spell, "
                  "and your items have been transmuted into a pile of gold coins.")
            print(f"\nYou received \033[33m{gold_reward:,}\033[0m gold "
                  f"for \033[36m{items_count:,}\033[0m disenchanted items!")
            print(f"\nYou now have \033[33m{player['gold']:,}\033[0m gold.")
            print("\nReturning to menu.")
            return
        if choice == "2":
            return
        print("\nInvalid choice. Please try again.")

def collect_daily_reward(player):
    """Grants a daily reward if not already collected today."""
    print("\n=== Daily Reward ===")
    today = date.today().isoformat()
    if player.get("last_daily") != today:
        daily_gold = 1000
        player["gold"] += daily_gold
        player["last_daily"] = today
        print(f"\nDaily reward collected! +\033[33m{daily_gold:,}\033[0m Gold\n")
    else:
        print("\nYou have already collected today's reward.")

def change_name(player):
    """Prompts player input to change player name."""
    print("\n=== Change Name ===")
    while True:
        print("\n1. Yes")
        print("2. No (Return to menu)\n")
        choice = input(f"Your current names is {player['name']}. Would you like to change it?\n")
        if choice == "1":
            new_name =  input("What would like your name to be?\n")
            player["name"] = new_name
            print(f"Your new names is {player['name']}. "
                  f"Godspeed, {player['name']}. Returning to Main Menu.")
            break
        if choice == "2":
            break
        print("Invalid choice. Please try again.")

# =============================
#        ENTRY POINT
# =============================

if __name__ == "__main__":
    main()
