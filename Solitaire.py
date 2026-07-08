import numpy as np
import pandas as pd

class Solitaire:
    # This class is a simulated game of Solitaire.
    
    def __init__(self):
        self.initiate_solitaire_board()
        
    def generate_deck(self):
        '''
        Function: Generate Simulated Deck of Cards. 

        Args:
            none
    
        Returns:
            DataFrame: deck[<Card Code>] = {rank, suit, value, order_id}
                ex. deck['as'] = {ace, spade, 1, 1} (ace of spades)
        '''
        
        # Initialize possible suits and ranks of cards
        self.suits = ['spades', 'clubs', 'diamonds', 'hearts']
        self.ranks = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']
        self.names = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', 'ten', 'jack', 'queen', 'king']
        
        # Create the deck as a dictionary using double list comprehension
        self.deck = {
            f"{name[0]}{suit[0]}": {
                "rank": self.ranks[self.names.index(name)],
                "name": name,
                "suit": suit,
                "color": 'red' if suit in ['diamonds','hearts'] else 'black',
                "value": 10 if name in ['ten','jack', 'queen', 'king'] else (1 if name == 'ace' else int(name)),
                "direction":"down"
            }
            for suit in self.suits
            for name in self.names
            }
        
        # Initialize Order ID 
        for idx,key in enumerate(self.deck.keys()):
            self.deck[str(key)]['stockID'] = str(idx+1)
            self.deck[str(key)]['wasteID'] = '0'
            self.deck[str(key)]['foundationID'] = '00'
            self.deck[str(key)]['tableauID'] = '00'
            
        # Convert Dictionary to Dataframe
        self.deck = pd.DataFrame(self.deck)
        
        # Create stockpile
        sobj = pd.DataFrame(self.deck.loc['stockID'][self.deck.loc['stockID']!=0])
        sorted_cards = sobj.sort_values(by='stockID').index.tolist()
        self.stockpile = pd.DataFrame(sorted_cards,columns=['column1'])
        
        
    def shuffle_deck(self):
        '''
        Function: Given a randomized set of integers from 0-51, reogranize the generated stockpile of cards.

        Args:
            none
    
        Returns:
            DataFrame: deck[<Card Code>] = {rank, suit, value, order_id}
                ex. deck['as'] = {ace, spade, 1, n} (ace of spades)
        '''
        # Initialize the recommended NumPy random generator
        rng = np.random.default_rng()
        
        # Generate unique random integers using choice
        unique_array = rng.choice(np.arange(1, 53), size=52, replace=False)
        
        # Apply random order to deck
        self.deck.loc['stockID'] = unique_array
        
        
    def initiate_tableau(self):
        card_index = 1
        
        for pile in range(1, 8):    
            for position in range(pile):
                card_name = self.deck.columns[self.deck.loc['stockID']==card_index].tolist()[0]
                
                self.deck[card_name].stockID = 0 # reset to zero, no longer in stockpile
                self.deck[card_name].tableauID = str(pile)+str(position) # update tableauID in stockpile
        
                # Last card in each pile is face up
                if position == pile - 1:
                    self.deck[card_name].direction = 'up'
                else:
                    self.deck[card_name].direction = 'down'
        
                card_index += 1
        
        # Reset stockIDs in deck
        self.deck.loc['stockID'][self.deck.loc['stockID']!=0] = self.deck.loc['stockID'][self.deck.loc['stockID']!=0]-28

            
    def initiate_solitaire_board(self):
        '''
        Function: 
            Run all initiating functions, set up solitaire board. To be called upon init.

        Args:
            none
    
        Returns:
            none
        '''
        # Initiate Stockpile
        self.generate_deck()
        self.shuffle_deck()
        
        # Initiate tableau
        self.initiate_tableau()
        

# Direct code execution
if __name__ == "__main__":
    S = Solitaire()
        

        
        
        
    