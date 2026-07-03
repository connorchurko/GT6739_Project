from Solitaire import Solitaire

game = Solitaire()

game.initiate_tableau

print(game.tableau)


# Need to define player attributes and strategy choices

# Strategy 1: Greedy player
# Greedy which has 4 priorities in ranked order, move cards to foundation pile, expose face down cards in tableau, create empty columns, place kings in empty 

# Strategy 2: Build Foundation  (+ Greedy strategy)
# Foundation builder, which prioritizes building the foundation piles over everything else

# Strategy 3: Look through and memorize the stockpile (+ Greedy strategy + revealing face down card)
# Tableau player, this prioritizes cleaning up the tableau and making moves there, last resort is to put cards in foundation piles