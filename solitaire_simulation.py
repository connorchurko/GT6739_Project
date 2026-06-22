from Solitaire import Solitaire

game = Solitaire()

game.generate_deck()
game.shuffle_deck()

print(game.deck['ad'])