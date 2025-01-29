from config.game_constants import SAVE_FILE

# Load game state from file
def load_state():
    global player
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as file:
                player.update(json.load(file))
        except json.JSONDecodeError:
            print("Error reading save file. Resetting game state.")
            save_state()
    else:
        save_state()

# Save game state to file
def save_state():
    with open(SAVE_FILE, "w") as file:
        json.dump(player, file)