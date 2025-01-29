"""
GameDev project - name TBD

A player attacks a monster, and the monster attacks back.

Some ideas to add:
1) Turn into an afk/idle game
2) Save game state and items
3) Clock aspect, day/night cycles
4) Stats affect dice rolls
5) Implement buffs and stuff

"""

import random
import json
import os
from datetime import date


# Program version and tagline
VERSION = "V1.2"

# Sets the minimum and maximum range for item weighting rolls
MIN_WEIGHT = 1
MAX_WEIGHT = 10000

# Sets the minimum and maximum range for random power added to items
MIN_POWER = 1
MAX_POWER = 5

def main():

    # Dictionary which lists item types and assigns them a number
    item_types = {
        "Weapon": 1, "Armour": 2, "Jewellery": 3
    }
    # Dictionary which records equipped items
    equipped_items = {
        "weapon_name": "0", "weapon_power": 0,
        "armour_name": "0", "armour_power": 0,
        "jewellery_name": "0", "jewellery_power": 0
    }
    # Dictionary which contains item prefixes and their associated power and drop weight (out of 10,000)
    item_prefixes = {
        "Trusty": {"tier": 1, "power": 1, "weight": 5000},
        "Fortunate": {"tier": 2, "power": 2, "weight": 3000},
        "Lucky": {"tier": 3, "power": 3, "weight": 1250},
        "Uncanny": {"tier": 4, "power": 4, "weight": 640},
        "Weighted": {"tier": 5, "power": 5, "weight": 100},
        "Blessed": {"tier": 6, "power": 10, "weight": 10},
        "Destined": {"tier": 7, "power": 20, "weight": 1}
    }
    # Dictionary which contains material types and their associated power and drop weight (out of 10,000)
    item_materials = {
        "Copper": {"tier": 1, "power": 1, "weight": 5000},
        "Bronze": {"tier": 2, "power": 2, "weight": 3000},
        "Iron": {"tier": 3, "power": 3, "weight": 1250},
        "Steel": {"tier": 4, "power": 4, "weight": 640},
        "Obsidian": {"tier": 5, "power": 5, "weight": 100},
        "Mythril": {"tier": 6, "power": 10, "weight": 10},
        "Titanium": {"tier": 7, "power": 20, "weight": 1}
    }
    # Dictionary which contains weapon types and their associated power and drop weight (out of 10,000)
    weapon_types = {
        "Sword": {"tier": 1, "power": 1, "weight": 5000},
        "Axe": {"tier": 2, "power": 2, "weight": 3000},
        "Mace": {"tier": 3, "power": 3, "weight": 1250},
        "Longbow": {"tier": 4, "power": 4, "weight": 640},
        "Katana": {"tier": 5, "power": 5, "weight": 100},
        "Staff": {"tier": 6, "power": 10, "weight": 9},
        "Tachi": {"tier": 7, "power": 20, "weight": 1}
    }
    # Dictionary which contains armour types and their associated power and drop weight (out of 10,000)
    armour_types = {
        "Garb": {"tier": 1, "power": 1, "weight": 5000},
        "Tunic": {"tier": 2, "power": 2, "weight": 3000},
        "Cuirass": {"tier": 3, "power": 3, "weight": 1250},
        "Hauberk": {"tier": 4, "power": 4, "weight": 640},
        "Mail": {"tier": 5, "power": 5, "weight": 100},
        "Plate": {"tier": 6, "power": 10, "weight": 9},
        "Gosoku": {"tier": 7, "power": 20, "weight": 1},
    }
    # Dictionary which contains jewellery types and their associated power and drop weight (out of 10,000)
    jewellery_types = {
        "Bangle": {"tier": 1, "power": 1, "weight": 5000},
        "Bracelet": {"tier": 2, "power": 2, "weight": 3000},
        "Earring": {"tier": 3, "power": 3, "weight": 1250},
        "Ring": {"tier": 4, "power": 4, "weight": 640},
        "Amulet": {"tier": 5, "power": 5, "weight": 100},
        "Crown": {"tier": 6, "power": 10, "weight": 10},
        "Brooch": {"tier": 7, "power": 20, "weight": 1}
    }
    # Dictionary which contains item suffixes and their associated power and drop weight (out of 10,000)
    item_suffixes = {
        "Mouse": {"tier": 1, "power": 1, "weight": 5000},
        "Rabbit": {"tier": 2, "power": 2, "weight": 3000},
        "Dog": {"tier": 3, "power": 3, "weight": 1250},
        "Cat": {"tier": 4, "power": 4, "weight": 640},
        "Parrot": {"tier": 5, "power": 5, "weight": 100},
        "Dragon": {"tier": 6, "power": 10, "weight": 10},
        "Basilisk": {"tier": 7, "power": 20, "weight": 1}
    }

    # Words which are placed at the start of dragon monster name, e.g ELDER Volcano Dragon (currently 5 ages)
    DRAGON_AGE = [
        "Hatchling",
        "Juvenile",
        "Mature",
        "Elder",
        "Ancient",
    ]

    # Words which are placed after the age in the dragon monster name, e.g Elder VOLCANO Dragon (currently 8 prefixes)
    DRAGON_PREFIXES = [
        "Volcano",
        "Thunder",
        "Frozen",
        "Tempest",
        "Mountain",
        "Arcane",
        "Shadow",
        "Eldritch",
    ]

    # Prints a welcome message
    print(end='\n')
    print("Welcome to GameDev Project, Version", VERSION)
    print("---------------------------------------------------")
    print(end='\n')

    # Defines the name of the player
    player_name = input("Enter your character's name: ")
    # Defines player level (starts at level 1)
    player_level = 1
    # Defines player experience (xp) points
    player_xp = 0
    # Defines player gold coins
    player_gold = 0
    # Declares current player health as global and defines initial value
    global current_player_health
    current_player_health = 100
    # Declares another player health value which will act as a default to return to upon defeat
    default_player_health = 100
    # Defines player base attack damage (before modifications and rolling)
    base_player_damage = 10
    # Defines how much the player heals between fights
    player_regen = 80+(random.randint(1,10))


    while True:

        # Pulls a random monster age from DRAGON_AGE
        random_monster_age = random.choice(DRAGON_AGE)
        # Pulls a random dragon prefix from DRAGON_PREFIXES
        random_monster_prefix = random.choice(DRAGON_PREFIXES)
        # Randomly rolls a dragon name, formatted as an f-string
        monster_name = (f'{random_monster_age} {random_monster_prefix} Dragon')
        # Defines monster level (starts at level 1)
        monster_level = 1
        # Declarees monster health as global and defines initial value
        global monster_health
        monster_health = 100
        # Defines monster base attack damage (before modifications and rolling)
        base_monster_damage = 10
        # Calculates a random amount of gold dropped by the enemy, scaled by monster_level
        gold_dropped = (random.randint(50, 500) * monster_level)
        # Calculates a random amount of xp given by the enemy, scaled by monster_level
        xp_given = (random.randint(50, 500) * monster_level)

        while input("Press enter to attack the monster.") == "":

            # Adds player's base damage to a random dice roll to calculate total damage
            def total_player_damage():
                player_damage_roll = random.randint(1,10)
                calculate_player_damage = base_player_damage + player_damage_roll
                return calculate_player_damage

            # Adds monster's base damage to a random dice roll to calculate total damage
            def total_monster_damage():
                monster_damage_roll = random.randint(1,10)
                calculate_monster_damage = base_monster_damage + monster_damage_roll
                return calculate_monster_damage

            # The player attacks the monster, removing their damage from its health
            def player_attacks():
                global monster_health  # Tell the function we want to modify the global variable
                player_damage = total_player_damage()
                monster_health = monster_health - player_damage  # Update the global variable
                return monster_health

            # The monster attacks the monster, removing its damage their health
            def monster_attacks():
                global player_health  # Tell the function we want to modify the global variable
                monster_damage = total_monster_damage()
                current_player_health = current_player_health - monster_damage  # Update the global variable
                return current_player_health

            # Prints the player's combat message
            def player_combat_message():
                global monster_health
                damage_dealt = total_player_damage()
                monster_health = monster_health - damage_dealt
                print(f"{player_name} attacks {monster_name}! {player_name} deals {damage_dealt} damage to {monster_name}!")
                print(f"{monster_name} has {monster_health} health remaining!")
                print(end='\n')

            # Prints the monster's combat message
            def monster_combat_message():
                global current_player_health
                damage_dealt = total_monster_damage()
                current_player_health = current_player_health - damage_dealt
                print(f"{monster_name} attacks {player_name}! {monster_name} deals {damage_dealt} damage to {player_name}!")
                print(f"{player_name} has {current_player_health} health remaining!")

            def roll_item(dic):
                # Roll a random number between defined weight range
                roll = random.randint(MIN_WEIGHT, MAX_WEIGHT)

                # Create cumulative weights
                cumulative = 0
                cumulative_weights = []

                for item, details in dic.items():
                    cumulative += details['weight']
                    cumulative_weights.append((cumulative, item, details['power']))

                for cumulative_weight, item, power in cumulative_weights:
                    if roll <= cumulative_weight:
                        return item, power

            prefix, prefix_value = roll_item(item_prefixes)
            material, material_value = roll_item(item_materials)
            weapon, weapon_value = roll_item(weapon_types)
            armour, armour_value = roll_item(armour_types)
            jewellery, jewellery_value = roll_item(jewellery_types)
            suffix, suffix_value = roll_item(item_suffixes)

            # Generate complete names for items
            raw_weapon_name = (prefix, material, weapon, "of the", suffix)
            weapon_name = ' '.join(raw_weapon_name)

            raw_armour_name = (prefix, material, armour, "of the", suffix)
            armour_name = ' '.join(raw_armour_name)

            raw_jewellery_name = (prefix, material, jewellery, "of the", suffix)
            jewellery_name = ' '.join(raw_jewellery_name)

            # Random power value to be added to item power
            random_power = random.randint(1, 10)

            # Compute combined powers for each item
            weapon_power = prefix_value + material_value + weapon_value + suffix_value + random_power
            armour_power = prefix_value + material_value + armour_value + suffix_value + random_power
            jewellery_power = prefix_value + material_value + jewellery_value + suffix_value + random_power

            # Picks an item type
            rolled_item_type = random.choice(list(item_types.keys()))

            # Defines the function which prints the resulting item
            def print_final_item():
                if rolled_item_type == "Weapon":
                    print(end='\n')
                    print(weapon_name)
                    print("Item type:", rolled_item_type)
                    print("Power level:", weapon_power)
                    print(end='\n')
                    print("(", prefix, prefix_value, "+", material, material_value, "+", weapon, weapon_value, "+",
                          suffix, suffix_value, "+", "Random Power (", MIN_POWER, "-", MAX_POWER, ")",
                          random_power, "=", weapon_power, ")")

                elif rolled_item_type == "Armour":
                    print(end='\n')
                    print(armour_name)
                    print("Item type:", rolled_item_type)
                    print("Power level:", armour_power)
                    print(end='\n')
                    print("(", prefix, prefix_value, "+", material, material_value, "+", armour, armour_value, "+",
                          suffix, suffix_value, "+", "Random Power (", MIN_POWER, "-", MAX_POWER, ")",
                          random_power, "=", armour_power, ")")

                elif rolled_item_type == "Jewellery":
                    print(end='\n')
                    print(jewellery_name)
                    print("Item type:", rolled_item_type)
                    print("Power level:", jewellery_power)
                    print(end='\n')
                    print("(", prefix, prefix_value, "+", material, material_value, "+", jewellery, jewellery_value, "+",
                          suffix, suffix_value, "+", "Random Power (", MIN_POWER, "-", MAX_POWER, ")",
                          random_power, "=", jewellery_power, ")")

            # First combat message
            player_combat_message()
            # Check monster death right after player's attack and generates rewards
            if monster_health <= 0:
                player_gold += gold_dropped
                player_xp += xp_given
                current_player_health += player_regen
                print(end='\n')
                print(f"{monster_name} has been defeated!")
                print(end='\n')
                print("You obtain:")
                print_final_item()
                print(end='\n')
                print (f"...you also receive {gold_dropped} gold pieces." 
                       f" Your total gold is now {player_gold} pieces.")
                print(end='\n')
                print(f"{player_name} receives {xp_given} experience points." 
                       f" {player_name} now has {player_xp} XP.")
                print(end='\n')
                print(f"{player_name} rests and regenerates {player_regen} health.")
                break
            monster_combat_message()
            # Check player death right after monster's attack
            if current_player_health <= 0:
                print(f"{player_name} has been defeated!")
                #Resets player health to a default value
                current_player_health = default_player_health
                break

        play_again = input("Would you like to play again? (yes/no): ").lower()

        if play_again != "yes":
            print("Thank you for playing! Farewell!")
            break

if __name__ == "__main__":
    main()
