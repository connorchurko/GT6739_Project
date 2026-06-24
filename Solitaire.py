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
        self.suits = ['spades', 'clubs', 'diamonds', 'hearts']
        self.ranks = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
        self.names = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
        
        # Create the deck as a dictionary using double list comprehension
        self.deck = {
            f"{name[0]}{suit[0]}": {
                "rank": self.ranks[self.names.index(name)],
                "name": name,
                "suit": suit,
                "color": 'red' if suit in ['diamonds','hearts'] else 'black',
                "value": 10 if name in ['jack', 'queen', 'king'] else (1 if name == 'ace' else int(name))
            }
            for suit in self.suits
            for name in self.names
            }
        
        # Initialize Order ID 
        for idx,key in enumerate(self.deck.keys()):
            self.deck[str(key)]['order_id'] = idx+1
        
    def initiate_piles(self):
        # Create the empty piles as dictionaries
        self.pile = {'1':{},'2':{},'3':{},'4':{}}
    
    def valid_placement(self, childCard: dict, parentCard: dict):
        '''
        Function: Checks if the card's rank and suit will allow placement.
        
        Args:
            childCard: Dictionary expression of child card (moving card).
            parentCard: Dictionary expression of parent card (stationary/capturing card).
    
        Returns:
            bool: 
        '''
        # Check Number Differences
        numCheck = False
        if (parentCard.rank - childCard.rank == 1):
            numCheck = True
        
        # Check Suit Differences
        suitCheck = False
        if (parentCard.color != childCard.color):
            suitCheck = True
            
        # Confirm Both Checks Pass
        valid = False
        if (numCheck & suitCheck):
            valid = True
        return valid
    
    def deck_to_pile(self, pileID1: str, cardID: str):
        '''
        Function: Move a single card from the deck to a pile.
        
        !!!!!!MUST HAVE A CHECK TO CONFIRM THAT THE CARD CAN BE MOVED!!!!

        Args:
            pileID1: To Be OrderID of card within pile 
            cardID:  Card ID (qh = queen of hearts) 
    
        Returns:
            dictionary: 
        '''
        order_id = len(self.pile[pileID1])+1 # determine order_id within pile
        
        valid = False
        if len(self.pile[pileID1]>0):
            valid = self.valid_placement(self.deck[cardID], self.pile[pileID1][order_id])
        else:
            valid = True
        
        if (valid):
            self.pile[pileID1]={cardID:self.deck[cardID]} 
            self.pile[pileID1][cardID]['order_id'] = order_id
        else:
            print('Card Unable to Move to Chosen Location')
                    
        
    # Function must work if moving group of cards to new pile
    def pile_to_pile(self, pileID1: str, pileID2: str, cardID: str):
        '''
        Function: Move cards between piles. 
        
        !!!!!!MUST BE CONFIGURED TO MOVE GROUP OF CARDS BETWEEN PILES AND UPDATE ORDER ID!!!!!!!

        Args:
            pileID1: OrderID of card within start pile 
            pileID2: To Be OrderID of card within end pile 
            cardID:  Card ID (qh = queen of hearts)
    
        Returns:
            dictionary: 
        '''
        order_id = len(self.pile[pileID2])+1 # determine order_id within pile
        self.pile[pileID2]=self.pile[pileID1]
        self.pile[pileID2][cardID]['order_id'] = order_id
    
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
        
    