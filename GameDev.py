"""
GameDev project - name TBD

A player attacks a monster, and the monster attacks back.

Some ideas to add:
1) Turn into an afk/idle game
2) Monster gives gold and exp
3) Clock aspect, day/night cycles
4) Stats affect dice rolls
5) Implemewnt buffs and stuff

"""

import random

# Program version and tagline
VERSION = "V1"

def main():

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
    # Declares player health as global and defines initial value
    global player_health
    player_health = 100
    # Defines player base attack damage (before modifications and rolling)
    base_player_damage = 10

    # Defines the name of the monster
    monster_name = "Bob the Monster"
    # Defines monster level (starts at level 1)
    monster_level = 1
    # Declarees monster health as global and defines initial value
    global monster_health
    monster_health = 100
    # Defines monster base attack damage (before modifications and rolling)
    base_monster_damage = 10

    while input("Attack the monster?") == "":

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
            player_health = player_health - monster_damage  # Update the global variable
            return player_health

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
            global player_health
            damage_dealt = total_monster_damage()
            player_health = player_health - damage_dealt
            print(f"{monster_name} attacks {player_name}! {monster_name} deals {damage_dealt} damage to {player_name}!")
            print(f"{player_name} has {player_health} health remaining!")

        # First combat message
        player_combat_message()
        # Check monster death right after player's attack
        if monster_health <= 0:
            print(f"{monster_name} has been defeated!")
            break
        monster_combat_message()
        # Check player death right after monster's attack
        if player_health <= 0:
            print(f"{player_name} has been defeated!")
            break
if __name__ == "__main__":
    main()
