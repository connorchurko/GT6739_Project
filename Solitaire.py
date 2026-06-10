import numpy as np
import pandas as pd

class Solitaire:
    # This class is a simulated game of Solitaire.
    
    def __init__(self):
        self.deck = dict()
        
    def generate_deck(self):
        '''
        Function: Generate Simulated Deck of Cards. 

        Args:
            none
    
        Returns:
            dictionary: deck[<Card Code>] = {rank, suit, value, order_id}
                ex. deck['as'] = {ace, spade, 1, 1} (ace of spades)
        '''
        
        # Initialize possible suits and ranks of cards
        suits = ['spades', 'clubs', 'diamonds', 'hearts']
        ranks = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
        
        # Create the deck as a dictionary using double list comprehension
        self.deck = {
            f"{rank[0]}{suit[0]}": {
                "rank": rank,
                "suit": suit,
                "value": 10 if rank in ['jack', 'queen', 'king'] else (1 if rank == 'ace' else int(rank))
            }
            for suit in suits
            for rank in ranks
            }
        
        # Initialize Order ID 
        for idx,key in enumerate(self.deck.keys()):
            self.deck[str(key)]['order_id'] = idx+1
        
    def shuffle_deck(self):
        '''
        Function: Given a randomized set of integers from 0-51, reogranize the generated deck of cards.

        Args:
            none
    
        Returns:
            dictionary: deck[<Card Code>] = {rank, suit, value, order_id}
                ex. deck['as'] = {ace, spade, 1, n} (ace of spades)
        '''
        # Initialize the recommended NumPy random generator
        rng = np.random.default_rng()
        
        # Generate unique random integers using choice
        unique_array = rng.choice(np.arange(1, 53), size=52, replace=False)
        
        # Apply random order to deck
        for idx,key in enumerate(self.deck.keys()):
            self.deck[str(key)]['order_id'] = unique_array[idx]
        
    