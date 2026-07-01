import numpy as np
import pandas as pd

class Solitaire:
    # This class is a simulated game of Solitaire.
    
    def __init__(self):
        self.initiate_solitaire_board()
        
    def generate_stockpile(self):
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
            self.deck[str(key)]['foundationID'] = '0'
            self.deck[str(key)]['tablaeuID'] = '00'
            
        # Convert Dictionary to Dataframe
        self.stockpile = pd.DataFrame(self.deck)
        
    def initiate_tablaeu(self):
        # !!!! NEEDS TO BE FILLED WITH CARDS... SHOULD NOT BE EMPTY
        tablaeu_pileIDs = [1,2,3,4,5,6,7]
        self.tablaeu = {f"pileID{str(stack_num)}":{} for stack_num in tablaeu_pileIDs}
        #scol = self.stockpile.columns[self.stockpile.loc['stockID'].between(1,28)].tolist()
        
        for pid in tablaeu_pileIDs:
            scol = self.stockpile.columns[self.stockpile.loc['stockID']==str(pid)].tolist()[0]
            self.tablaeu[f"pileID{str(pid)}"] = self.stockpile[scol]
        
        
    def initiate_foundation_piles(self):
        # Create the empty stacks 
        self.foundation_pile = {f"{suit}":{} for suit in ['spades', 'clubs', 'diamonds', 'hearts']}
        self.foundation_pile = pd.DataFrame(self.foundation_pile)
    
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
    
    def tablaeu_to_foundation(self):
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
    
    def shuffle_stockpile(self):
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
        for idx,key in enumerate(self.stockpile.keys()):
            self.stockpile[str(key)]['stockID'] = unique_array[idx]
            
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
        self.generate_stockpile()
        self.shuffle_stockpile()
        
        # Initiate Foundation piles
        self.initiate_foundation_piles()
        
        # Initiate Tablaeu
        self.initiate_tablaeu()
        

        
        
        
    