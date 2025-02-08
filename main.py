"""GameDev - a loot rolling RPG, by Vader and ink."""

import random
from datetime import date
from enemies.enemies import DRAGON_AGE, DRAGON_PREFIXES
from items.item_constants import (item_prefixes, item_suffixes, item_materials,
                                  armour_types, jewellery_types, weapon_types)
from config.game_constants import VERSION, MIN_WEIGHT, MAX_WEIGHT, MIN_POWER, MAX_POWER
from config import save_utils

# =============================
#         MONSTER LOGIC
# =============================

def generate_monster(player):
    """Generates a random dragon monster."""
    monster_level = player['level'] + random.randint(0, 1)
    return {
        'name': f"{random.choice(DRAGON_AGE)} {random.choice(DRAGON_PREFIXES)} Dragon",
        'level': monster_level,
        'max_health': (monster_level*10)+90,
        'health': (monster_level*10)+90,
        'base_damage': int((monster_level*2)+5),
        'base_armour': int(monster_level*1.5),
        'base_crit_chance': 5,
        'base_crit_bonus': 50,
        'gold_drop': int(((random.randint(300, 500))/100)*
                         (100+(monster_level*10)+(player['gold_find']*10))),
        'xp_reward': int(((random.randint(300, 500))/100)*(100+(monster_level*10))),
        'equipped_items': {
            'weapon': {
                'name': 'None',
                'power': 0
            },
            'armour': {
                'name': 'None',
                'power': 0
            },
            'jewellery': {
                'name': 'None',
                'power': 0
            }
        }
    }

# =============================
#         COMBAT SYSTEM
# =============================

def roll_damage(attacker):
    """Calculates total damage based on base stats, equipped weapon and a random roll."""
    base_damage = attacker['base_damage']
    weapon_power = attacker['equipped_items']['weapon']['power']
    random_power = random.randint(0, int(weapon_power))
    random_base = random.randint(0, 10)
    return base_damage + random_power + random_base

def roll_defence(defender):
    """Calculates total damage reduction based on equipped armour."""
    base_defence = defender['base_armour']
    armour_power = defender['equipped_items']['armour']['power']
    random_power = random.randint(0, int(armour_power))
    return base_defence + random_power

def crit_chance (attacker):
    """Calculates critical hit chance."""
    base_crit_chance = attacker['base_crit_chance']
    jewellery_power = attacker['equipped_items']['jewellery']['power']
    jewellery_crit_chance = int(jewellery_power/3)
    return base_crit_chance + jewellery_crit_chance

def crit_bonus (attacker):
    """Calculates critical hit bonus."""
    base_crit_bonus = attacker['base_crit_bonus']
    jewellery_power = attacker['equipped_items']['jewellery']['power']
    jewellery_crit_bonus = int(jewellery_power/2)
    return base_crit_bonus + jewellery_crit_bonus

def attack(attacker, defender):
    """Handles an attack from one character to another, and checks for critical hit/bonus."""
    crit_roll = crit_chance(attacker) + random.randint(1, 100)
    if crit_roll >= 100:
        damage_before_armour = int((roll_damage(attacker)/100)*(100+crit_bonus(attacker)))
        damage = damage_before_armour - roll_defence(defender)
        if damage >= 0:
            pass
        else:
            damage = 0
        defender['health'] -= damage
        print(f"\n{attacker['name']} CRITS {defender['name']} "
              f"and deals {damage:,} damage!")
        print(f"{defender['name']} has "
              f"{max(defender['health'], 0):,} health remaining.")
        return defender['health'] <= 0  # Returns True if defender dies
    damage_before_armour = roll_damage(attacker)
    damage = damage_before_armour - roll_defence(defender)
    if damage >= 0:
        pass
    else:
        damage = 0
    defender['health'] -= damage
    print(f"\n{attacker['name']} attacks {defender['name']} "
            f"and deals {damage:,} damage!")
    print(f"{defender['name']} has "
          f"{max(defender['health'], 0):,} health remaining.")
    return defender['health'] <= 0  # Returns True if defender dies

def check_level_up(player):
    """Checks if conditions are met for player to level up and returns boolean."""
    xp_required = (player['level']**2)*100
    return player['xp'] >= xp_required

def level_up(player):
    """Performs changes required to level up player."""
    player['level'] += 1
    player['xp'] = 0
    print(f"\n{player['name']} levels up! {player['name']} "
          f"is now level {player['level']:,}.")
    player['regen'] += 10
    player['base_damage'] += 1
    player['max_health'] += 10
    player['health'] =  player['max_health']

def fight_monster(player):
    """Handles the fight loop between the player and a monster."""
    monster = generate_monster(player)
    print(f"\n{player['name']} encounters a level "
          f"{monster['level']} {monster['name']}!")

    while player['health'] > 0 and monster['health'] > 0:
        input("\nPress Enter to attack...")
        # Player attacks first
        if attack(player, monster):
            print(f"\n{monster['name']} has been defeated!\n")
            player['gold'] += monster['gold_drop']
            player['xp'] += monster['xp_reward']
            health_regen = player['regen']+random.randint (1, 10)
            player['health'] += health_regen
            if player['health'] > player['max_health']:
                player['health'] = player['max_health']
            print(f"{player['name']} gained {monster['gold_drop']:,} gold"
                  f" and {monster['xp_reward']:,} XP.")
            print(f"{player['name']} regenerates {health_regen:,} health.\n")
            item = generate_random_item(monster, player)
            item_type = random.choice(['Weapon', 'Armour', 'Jewellery'])
            rolled_item = item[item_type]
            print(f"{player['name']} received {rolled_item['name']} "
                  f"(Power: {rolled_item['power']}) as a drop!")
            player['inventory'].append({
                'name' : rolled_item['name'],
                'type' : item_type,
                'power' : rolled_item['power']
            })
            check_level_up(player)
            if check_level_up(player):
                level_up(player)
            return

        # Monster retaliates
        if attack(monster, player):
            print(f"\n{player['name']} has been defeated! Returning to Main Menu.")
            player['health'] = player['max_health']  # Reset player health after defeat
            return

# =============================
#        ITEM GENERATION
# =============================

def roll_item(dic, monster, player):
    """Randomly rolls an item from a given dictionary with weighted probabilities."""
    roll = random.randint(MIN_WEIGHT, MAX_WEIGHT) + (monster['level']*5) + player['magic_find']
    cumulative = 0
    for item, details in dic.items():
        cumulative += details['weight']
        if roll <= cumulative:
            return item, details['power']
    for item, details in dic.items():
        if details['weight'] == 1:
            return item, details['power']
    return None, 0

def generate_random_item(monster, player):
    """Generates a random weapon, armor, or jewelry with properties."""
    prefix, prefix_value = roll_item(item_prefixes, monster, player)
    material, material_value = roll_item(item_materials, monster, player)
    weapon, weapon_value = roll_item(weapon_types, monster, player)
    armour, armour_value = roll_item(armour_types, monster, player)
    jewellery, jewellery_value = roll_item(jewellery_types, monster, player)
    suffix, suffix_value = roll_item(item_suffixes, monster, player)
    random_power = random.randint(MIN_POWER, MAX_POWER)

    # Generate full item names
    weapon_name = f"{prefix} {material} {weapon} of the {suffix}"
    armour_name = f"{prefix} {material} {armour} of the {suffix}"
    jewellery_name = f"{prefix} {material} {jewellery} of the {suffix}"

    return {
        'Weapon': {'name': weapon_name,
                   'power': prefix_value + material_value +
                            weapon_value + suffix_value + random_power},
        'Armour': {'name': armour_name,
                   'power': prefix_value + material_value +
                            armour_value + suffix_value + random_power},
        'Jewellery': {'name': jewellery_name,
                      'power': prefix_value + material_value +
                               jewellery_value + suffix_value + random_power}
    }

def show_inventory(player):
    """Displays player's inventory items."""
    while True:
        print("\n=== Player Inventory ===")
        if not player['inventory']:
            print("\nYour inventory is empty.")
            return
        sorted_inventory = sorted(player['inventory'], key=lambda x: x['power'], reverse=True)
        for index, item in enumerate(sorted_inventory, start=1):
            print(f"{index}. {item['name']} (Type: {item['type']}, Power: {item['power']})")
        print(f"\nEquipped Weapon: {player['equipped_items']['weapon']['name']} "
              f"(Power: {player['equipped_items']['weapon']['power']})")
        print(f"Equipped Armour: {player['equipped_items']['armour']['name']} "
              f"(Power: {player['equipped_items']['armour']['power']})")
        print(f"Equipped Jewellery: {player['equipped_items']['jewellery']['name']} "
              f"(Power: {player['equipped_items']['jewellery']['power']})\n")
        print("Enter the number of an item to equip it, or press Enter to go back.\n")
        choice = input("Choose an item:")
        if choice == '':
            break
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(sorted_inventory):
                item_to_equip = sorted_inventory[index]
                original_index = player['inventory'].index(item_to_equip)
                equip_item(player, original_index)
            else:
                print("Invalid selection.")

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(player['inventory']):
            equip_item(player, index)
        else:
            print("Invalid selection.")

def equip_item(player, item_index):
    """Equips an item from the player's inventory."""
    item = player['inventory'].pop(item_index)  # Remove from inventory
    item_type = item['type']

    # Equip the item in the correct slot
    player['equipped_items'][item_type.lower()] = {'name': item['name'], 'power': item['power']}
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
        print("6. Magic Eater")
        print("7. Gold Eater")
        print("8. Daily Reward")
        print("9. Change Name")
        print("10. Save Game")
        print("11. Save and Exit")

        choice = input("\nChoose an option (or press Enter to fight): ")

        if choice in ['1', '']:
            fight_monster(player)
        elif choice == '2':
            show_stats(player)
        elif choice == '3':
            show_inventory(player)
        elif choice == '4':
            item_merchant(player)
        elif choice == '5':
            disenchanter(player)
        elif choice == '6':
            magic_eater(player)
        elif choice == '7':
            gold_eater(player)
        elif choice == '8':
            collect_daily_reward(player)
        elif choice == '9':
            change_name(player)
        elif choice == '10':
            save_utils.save_player(player)
            print("\nGame saved.")
        elif choice == '11':
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
    print(f"\nYou have {player['gold']:,} gold. "
          f"Buying an item costs {merchant_cost:,} gold.")
    while True:
        print("\n1. Yes")
        print("2. No (Return to menu)\n")
        choice = input("'Oh, stranger... are you buyin'?'")
        if choice == '2':
            return
        if choice != '1':
            print("\nInvalid choice. Please try again.")
            continue
        while True:
            if player['gold'] < merchant_cost:
                print("'\n'Not enough gold, stranger...'")
                print("\nReturning to menu.")
                return
            player['gold'] -= merchant_cost
            monster = generate_monster(player)
            item = generate_random_item(monster, player)
            item_type = random.choice(['Weapon', 'Armour', 'Jewellery'])
            rolled_item = item[item_type]
            print("\n'Excellent choice, stranger... here you go.'")
            print(f"\n{player['name']} received {rolled_item['name']} "
                  f"(Power: {rolled_item['power']})!")
            print(f"\nYou now have {player['gold']:,} gold.")
            player['inventory'].append({
                'name': rolled_item['name'],
                'type': item_type,
                'power': rolled_item['power']
            })
            print("\n1. Yes")
            print("2. No (Return to menu)")
            choice = input("\n'Are you buyin' again, stranger?'")
            if choice == '2':
                return
            if choice != '1':
                print("\nInvalid choice. Please try again.")
                break

def show_stats(player):
    """Displays the player's stats."""
    next_level = int(player['level']+1)
    xp_next_level = (next_level**2)*100
    try:
        percentage_to_level = int((player['xp']/xp_next_level)*100)
    except ZeroDivisionError:
        percentage_to_level = 0
    print("\n=== Player Stats ===")
    print(f"Name: {player['name']}")
    print(f"Level: {player['level']:,}")
    print(f"Health: {player['health']:,}")
    print(f"EXP: {player['xp']:,}")
    print(f"Next level: {xp_next_level:,}")
    print(f"Next level %: {percentage_to_level:,}%")
    print(f"Gold: {player['gold']:,}\n")
    print(f"Crit Chance: {crit_chance(player)}%")
    print(f"Crit Bonus: {crit_bonus(player)}%")
    print(f"Base Damage: {player['equipped_items']['weapon']['power']
                                  + player['base_damage']}")
    print(f"Total Armour: {player['equipped_items']['armour']['power']}\n")
    print(f"Magic Eater Power: {player['magic_find']}")
    print(f"Gold Eater Power: {player['gold_find']}\n")
    print(f"Equipped Weapon: {player['equipped_items']['weapon']['name']} "
          f"(Power: {player['equipped_items']['weapon']['power']})")
    print(f"Equipped Armour: {player['equipped_items']['armour']['name']} "
          f"(Power: {player['equipped_items']['armour']['power']})")
    print(f"Equipped Jewellery: {player['equipped_items']['jewellery']['name']} "
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
        if choice == '1':
            total_power = sum(item['power'] for item in player['inventory'])
            items_count = len(player['inventory'])
            gold_reward = total_power*20
            player['gold'] += gold_reward
            player['inventory'].clear()
            print("\nThe wizard casts a spell, "
                  "and your items have been transmuted into a pile of gold coins.")
            print(f"\nYou received {gold_reward:,} gold "
                  f"for {items_count:,} disenchanted items!")
            print(f"\nYou now have {player['gold']:,} gold.")
            print("\nReturning to menu.")
            return
        if choice == '2':
            return
        print("\nInvalid choice. Please try again.")

def magic_eater(player):
    """Opens the magic eater."""
    print("\n=== Magic Eater ===")
    print("\nA small, fluffy creature stands before you.")
    while True:
        print("\n1. Yes")
        print("2. No (Return to menu)\n")
        choice = input("The Magic Eater wants to eat your inventory. Will you let it?")
        if choice == '1':
            total_power = sum(item['power'] for item in player['inventory'])
            items_count = len(player['inventory'])
            food_gained = int(total_power/200)
            print("\n1. Yes")
            print("2. No (Return to menu)")
            choice = input(f"\nEating your inventory will grant the Magic Eater "
                           f"{food_gained} power. Are you sure?")
            if choice == '1':
                player['magic_find'] += food_gained
                player['inventory'].clear()
                print("\nThe Magic Eater hungrily devours your inventory.")
                print(f"\nThe Magic Eater gains {food_gained} power "
                      f"for {items_count:,} eaten items!")
                print(f"\nThe Magic Eater now has {player['magic_find']} power.")
                print("\nReturning to menu.")
                return
            if choice == '2':
                return
        if choice == '2':
            return
        print("\nInvalid choice. Please try again.")

def gold_eater(player):
    """Opens the gold eater."""
    print("\n=== Gold Eater ===")
    print("\nA lazy, plump creature sits before you.")
    while True:
        print("\n1. Yes")
        print("2. No (Return to menu)\n")
        choice = input("The Gold Eater wants to eat all your gold. Will you let it?")
        if choice == '1':
            gold_before = player['gold']
            food_gained = int(player['gold']/10000)
            print("\n1. Yes")
            print("2. No (Return to menu)")
            choice = input(f"\nEating your gold will grant the Gold Eater "
                           f"{food_gained} power. Are you sure?")
            if choice == '1':
                player['gold_find'] += food_gained
                player['gold'] = 0
                print("\nThe Gold Eater feasts upon your coins.")
                print(f"\nThe Gold Eater gains {food_gained} power "
                      f"for {gold_before:,} eaten gold!")
                print(f"\nThe Gold Eater now has {player['gold_find']} power.")
                print(f"\nYou now have {player['gold']:,} gold.")
                print("\nReturning to menu.")
                return
            if choice == '2':
                return
        if choice == '2':
            return
        print("\nInvalid choice. Please try again.")

def collect_daily_reward(player):
    """Grants a daily reward if not already collected today."""
    print("\n=== Daily Reward ===")
    today = date.today().isoformat()
    if player.get('last_daily') != today:
        daily_gold = 1000*player['level']
        player['gold'] += daily_gold
        player['last_daily'] = today
        print(f"\nDaily reward collected! +{daily_gold:,} Gold")
    else:
        print("\nYou have already collected today's reward.")

def change_name(player):
    """Prompts player input to change player name."""
    print("\n=== Change Name ===")
    while True:
        print("\n1. Yes")
        print("2. No (Return to menu)\n")
        choice = input(f"Your current names is {player['name']}. Would you like to change it?\n")
        if choice == '1':
            new_name =  input("\nWhat would like your name to be?\n")
            player['name'] = new_name
            print(f"Your new names is {player['name']}. "
                  f"Godspeed, {player['name']}. Returning to Main Menu.")
            break
        if choice == '2':
            break
        print("Invalid choice. Please try again.")

# =============================
#        ENTRY POINT
# =============================

if __name__ == '__main__':
    main()
