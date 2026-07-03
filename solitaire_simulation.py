from Solitaire import Solitaire

game = Solitaire()

game.initiate_tableau

print(game.tableau)


# Need to define player attributes and strategy choices

# Strategy 1: Greedy player
# This player will play cards as soon as a move becomes from the stock pile to the tableau or foundation piles
# Look to play to tablaeu first, then look to play to foundation if can't play to foundation, then look to next card


# Strategy 2: Focus on revealing face down cards (+ Greedy strategy)
# This player will look to try and move face up cards on the tableau to other available positions to be able to reveal face down cards
# This will mean the player will have to evaluate each column face up card against the other columns (and the inverse relationship)
# as well as against the current state of the foundation pile
# If nothing can be moved on the tableau, then it turns attention to the stockpile

# Strategy 3: Look through and memorize the stockpile (+ Greedy strategy + revealing face down card)
# This player will use it's first moves to look through the stockpile and take into account what cards are available
# This strategy will combine all three of the strategies as well as moving kings to available columns