from poker import Player, Deck, BotPlayer
from GameEngine import GameEngine
from gui import PokerGUI
import tkinter as tk
import random

if __name__ == "__main__":
    deck = Deck()

    human_player = Player(1000, "Human Player")

    num_bots = random.randint(2, 5)  
    bot_names = ["Bot Alpha", "Bot Beta", "Bot Gamma", "Bot Delta", "Bot Epsilon"]
    bots = []
    for i in range(num_bots):
        name = bot_names[i % len(bot_names)]
        bots.append(BotPlayer(1000, name))

    players = [human_player] + bots

    print("--- Players in this game ---")
    for p in players:
        print(f"- {p.name} (Stack: {p.stack})")
    print("----------------------------")

    root = tk.Tk()
    game_engine = GameEngine(players, deck, gui=None)
    gui = PokerGUI(root, game_engine)
    game_engine.set_gui(gui)

    root.mainloop()

    print("\n--- Final Stacks ---")
    for player in players:
        print(f"{player.name} stack: {player.get_stack_amount()}")
    print("--------------------")