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
        
    def initiate_tableau(self):
           
        self.tableau = {}
        card_index = 1
        
        for pile in range(1, 8):    
            self.tableau[f'column{pile}'] = {}
        
            for position in range(pile):
                
                card_name = self.deck.columns[self.deck.loc['stockID']==card_index].tolist()[0]
                card_data = self.deck[card_name]
        
                # Copy the card so the original deck isn't modified
                self.tableau[f'column{pile}'][card_name] = card_data.copy()
        
                # Last card in each pile is face up
                if position == pile - 1:
                    self.tableau[f'column{pile}'][card_name]['direction'] = 'up'
                else:
                    self.tableau[f'column{pile}'][card_name]['direction'] = 'down'
        
                card_index += 1
                
        # Initialize NaN DataFrame
        tableau_df = pd.DataFrame(
            np.nan,
            index=range(13),
            columns=[f'column{i}' for i in range(1, 8)]
            )
        
        # Convert tableau dictionary to DataFrame
        for col in self.tableau.keys():
            idx = 0
            for item in self.tableau[col]:
                 tableau_df.loc[idx,col] = item
                 self.deck[item].stockID = 0 # reset to zero, no longer in stockpile
                 self.deck[item].tableauID = int(col[-1]+str(idx)) # update tableauID in stockpile
                 idx += 1
        
        # Resave tableau into class attribute
        self.tableau = tableau_df
        
        # Reset stockIDs in deck
        self.deck.loc['stockID'][self.deck.loc['stockID']!=0]-28
        
        # Remove cards within tableau from stockpile
        #for col_name,col_data in self.tableau.items():
            #for cid in col_data:
                #if(cid.isin(self.stockpile)):
                    # use df.dop to remove tableau items.
        
        
    def initiate_foundation_piles(self):
        # Create the empty stacks 
        self.foundation_pile = {f"{suit}":{} for suit in ['spades', 'clubs', 'diamonds', 'hearts']}
        self.foundation_pile = pd.DataFrame(self.foundation_pile)
    
    def valid_placement(self, childCard: dict, parentCard: dict, move_type: str):
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
            
        # Check Card Face Direction
        directionCheck = False
        if (parentCard.direction != childCard.direction):
            directionCheck = True
            
        # Confirm Both Checks Pass
        valid = False
        if (numCheck & suitCheck & directionCheck):
            valid = True
        return valid
    
    def stockpile_to_wastepile(self):
        pass
    
    def tableau_to_foundation(self):
        pass
    
    def stockpile_to_foundation(self):
        pass
    
    def stockpile_to_tableau(self, pileID1: str, cardID: str):
        '''
        Function: Move a single card from the deck to a pile.
        
        !!!!!!MUST HAVE A CHECK TO CONFIRM THAT THE CARD CAN BE MOVED!!!!
        
        Args:
            pileID1: To Be OrderID of card within pile 
            cardID:  Card ID (qh = queen of hearts) 
        
        Returns:
            dictionary: 
        '''
        order_id = str(len(self.tableau[pileID1])+1) # determine order_id within pile
        
        valid = False
        if len(self.tableau[pileID1]>0):
            valid = self.valid_placement(self.stockpile[cardID], self.tableau[pileID1][order_id])
        else:
            valid = True
        
        if (valid):
            self.tableau[pileID1]={cardID:self.stockpile[cardID]} 
            self.tableau[pileID1][cardID]['stockID'] = order_id
        else:
            print('Card Unable to Move to Chosen Location')
                    
        
    # Function must work if moving group of cards to new pile
    def tableau_pile_to_tableau_pile(self, pileID1: str, pileID2: str, cardID: str):
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
        order_id = str(len(self.tableau[pileID2])+1) # determine order_id within pile
        self.tableau[pileID2]=self.tableau[pileID1]
        self.tableau[pileID2][cardID]['stockID'] = order_id
        
    def initiate_wastepile(self):
        pass
    
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
        for idx,key in enumerate(self.deck.keys()):
            self.deck[str(key)]['stockID'] = unique_array[idx]
            
        self.stockpile['column1'] = self.deck.loc['stockID'].sort_values().keys().tolist()    
            
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
        
        # Initiate Foundation piles
        self.initiate_foundation_piles()
        
        # Inititate Wastepile
        self.initiate_wastepile()
        
        # Initiate tableau
        self.initiate_tableau()
        

        
        
        
    