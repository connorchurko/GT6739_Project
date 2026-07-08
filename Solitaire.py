import numpy as np
import pandas as pd

class Solitaire:
    # This class is a simulated game of Solitaire
    
    def __init__(self):
        self.initiate_solitaire_board()
        self.strategy = 'greedy'
        
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
            self.deck[str(key)]['stockID'] = idx+1
            self.deck[str(key)]['wasteID'] = 0
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
        self.deck.loc['direction'][self.deck.loc['stockID']==self.deck.loc['stockID'].max()] = 'up'  

        
    def top_stockpile(self):
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        if len(stock.keys())==0:
            print("Stockpile is empty. Needs reset.")
            return 
        else:  
            cardID = self.deck.keys()[self.deck.loc['stockID'] == self.deck.loc['stockID'].max()][0]
            print(f"The top of the stockpile is {cardID}")
            return cardID
            
            
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
        
        # Flip Top Stockpile Card
        self.top_stockpile()
        
    def reset_stockpile(self):
        # Move cards from wastepile to stockpile
        #waste = self.deck[self.deck.keys()[self.deck.loc['wasteID']!=0]]
        
        # Set stockIDs based on wasteIDs
        self.deck.loc['stockID'][self.deck.loc['wasteID']!=0] = abs(self.deck.loc['wasteID']-self.deck.loc['wasteID'].max())+1
        self.deck.loc['direction'][self.deck.loc['stockID']==self.deck.loc['stockID'].max()] = 'up'  
        
        # Set WasteIDs to Zero
        self.deck.loc['wasteID'] = 0
        
        print('Reseting stockpile from wastepile')
    
    def check_placement(self):
        # Stockpile status
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        if len(stock.keys())==0:
            self.reset_stockpile()
        
        # Determine top card
        cardID = self.deck.keys()[self.deck.loc['stockID'] == self.deck.loc['stockID'].max()][0]        
        card_data = self.deck[cardID]            
        
        
        ####### TABLEAU PLACEMENT #######
        # Find all cards in tableau 
        tab = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='00']]
        
        # Step 1: Determine if cards of rank+1 are in tableau
        rank_cond = tab.loc['rank']==str(int(card_data['rank'])+1)
        
        # Step 2: Determine if rank+1 card is face up
        dir_cond = tab.loc['direction']=='up'
        
        # Step 3: Determine if rank+1, face up card is opposite color
        clr_cond = tab.loc['color']!=card_data['color']
        
        # Find available tableau card
        tab_card = tab[tab.keys()[rank_cond & dir_cond & clr_cond]]
        
        # Confirm possible cards are at end of tableau
        endIDs = self.find_top_tab()
        validIDs = [id for id in tab_card.keys() if tab_card[id]['tableauID'] in endIDs]
        tab_card = tab_card[validIDs]
        
        ####### FOUNDATION PLACEMENT #######
        # Dependent on strategy. Baseline placing aces into foundation automatically.
        # Must determine if card of rank-1 and same suit exists in foundation already.
        goToFoundation = False
        if card_data['name'] =='ace': # Aces auto foundation
            goToFoundation = True
        else: # if not ace, not foundation possibility
            found = self.deck[self.deck.keys()[self.deck.loc['foundationID']!='00']]
            # Step 1: Determine if rank-1 exists in foundation
            rank_cond = found.loc['rank']==int(card_data['rank'])-1
            
            # Step 2: Determine if rank-1 card has the same suit
            suit_cond = found.loc['suit']==card_data['suit']
            
            # Select foundation opening
            found_card = found[found.keys()[rank_cond & suit_cond]]    
                
            if self.strategy == 'greedy' and len(found_card.keys())>0:
                goToFoundation = True
            elif self.strategy == 'other':
                goToFoundation = True
        
        # NEED LOGIC IF BOTH ARE TRUE? PRIOTIZE BASED ON STRATEGY?
        out = {cardID:'waste'} # default to wastepile
        if len(tab_card.keys())>0:
            out[cardID] = 'tableau' # set flag to tableau if card available
        elif goToFoundation:    
            out[cardID] = 'foundation'
            
        return out
    
    def player(self):
        place = self.check_placement()
        cardID = list(place)[0]
        if 'waste' in place.values():
            self.stockpile_to_wastepile(cardID)
        elif 'foundation' in place.values():
            self.stockpile_to_foundation(cardID)
        elif 'tableau' in place.values():
            self.stockpile_to_tableau(cardID)
    
    def stockpile_to_wastepile(self,cardID: str):
        # Move top stockpile card to wastepile (update wasteID, make stockID = 0)
        self.deck[cardID]['wasteID'] = int(self.deck.loc['wasteID'].max())+1
        self.deck[cardID]['stockID'] = 0
        
        # Reset stockpile and flip
        self.deck.loc['direction'][self.deck.loc['stockID']==self.deck.loc['stockID'].max()] = 'up'
        
        print(f"{cardID} moved to wastepile")
        self.top_stockpile()
            
    def stockpile_to_foundation(self,cardID: str):
        # Move top stockpile card to wastepile (update foundationID, make stockID = 0)
        self.deck[cardID]['foundationID'] = cardID
        self.deck[cardID]['stockID'] = 0
        
        # Reset stockpile and flip
        self.deck.loc['direction'][self.deck.loc['stockID']==self.deck.loc['stockID'].max()] = 'up'
        
        print(f"{cardID} moved to foundation")
        self.top_stockpile()
        
    def find_top_tab(self):  
        tab = tab = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='00']]
        tabs = [int(a) for a in tab.loc['tableauID']]
        tabs = np.array(tabs)
        
        cols = tabs//10 # floor division
        rows = tabs % 10
        
        endIDs = []
        for c in np.unique(cols):
            max_row = rows[cols==c].max()
            endIDs.extend([str(c)+str(max_row)])
            
        return endIDs
    
    
    def stockpile_to_tableau(self, cardID: str):
        '''
        Function: Move a single card from the deck to a pile.
        
        !!!!!!MUST HAVE A CHECK TO CONFIRM THAT THE CARD CAN BE MOVED!!!!

        Args:
            pileID1: To Be OrderID of card within pile 
            cardID:  Card ID (qh = queen of hearts) 
    
        Returns:
            dictionary: 
        '''
        card_data = self.deck[cardID]
        
        # Find all cards in tableau 
        tab = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='00']]
        
        # Step 1: Determine if cards of rank+1 are in tableau
        rank_cond = tab.loc['rank']==str(int(card_data['rank'])+1)
        
        # Step 2: Determine if rank+1 card is face up
        dir_cond = tab.loc['direction']=='up'
        
        # Step 3: Determine if rank+1, face up card is opposite color
        clr_cond = tab.loc['color']!=card_data['color']
        
        # Find available tableau card
        open_card = tab[tab.keys()[rank_cond & dir_cond & clr_cond]]
        
        # Confirm possible cards are at end of tableau
        endIDs = self.find_top_tab()
        validIDs = [id for id in open_card.keys() if open_card[id]['tableauID'] in endIDs]
        open_card = open_card[validIDs]

        # CHOOSE FIRST OPTION (TO BE UPDATED WITH STRATEGIES)
        chosen_card = open_card[open_card.keys()[0]]
        
        # Move top stockpile card to chosen card in tableau (update tableauID, make stockID = 0)
        self.deck[cardID]['tableauID'] = int(chosen_card['tableauID'])+1
        self.deck[cardID]['stockID'] = 0
        
        # Reset stockpile and flip
        self.deck.loc['direction'][self.deck.loc['stockID']==self.deck.loc['stockID'].max()] = 'up'
        
        print(f"{cardID} placed onto {chosen_card.name} in tableau")
        self.top_stockpile()
            
    def tableau_to_foundation(self):
        pass      
                   
    # Function must work if moving group of cards to new pile
    def tableau_pile_to_tableau_pile(self, pileID1: str, pileID2: str, cardID: str):
        pass
        
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
    

# Direct code execution
if __name__ == "__main__":
    S = Solitaire()
    S.player() # first move
    #while len(S.deck.keys()[S.deck.loc['stockID']!=0])>0:
        #S.player()
    #for i in range(1,100):
        #S.player()

        
        
        
    