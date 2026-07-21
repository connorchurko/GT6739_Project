import numpy as np
import pandas as pd

class Solitaire:
    # This class is a simulated game of Solitaire
    
    def __init__(self,selected_seed):
        self.strategy = 'greedy'
        self.seed = selected_seed
        
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
        rng = np.random.default_rng(seed=self.seed)
        
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
        
        # Initialize NaN DataFrame
        self.tableau = pd.DataFrame(
            np.nan,
            index=range(13),
            columns=[f'column{i}' for i in range(1, 8)]
            )
        
        # Create visual representation of tableau
        tableau_df = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='00']]
        for cid in tableau_df.keys():
            tid = tableau_df[cid]['tableauID']
            col = int(str(tid)[0])
            row = int(str(tid)[1])
            dir = tableau_df[cid]['direction']
            self.tableau.iloc[row,col-1] = f'{cid}({dir[0]})'
        print(self.tableau)
     
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
        
        print('Welcome... Board Initialized')
        
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
    
    def player(self):
        '''
        Returns
        -------
        out : TYPE
            DESCRIPTION.


        Logic Sequence (Foundation First -> Greedy)
        1. Player checks if stockpile is empty
            if yes, reset stockpile from waste
            if no, go to 2
        2. Player pulls card from stockpile, got to 3
        3. Player checks foundation placement valid
            if yes, place card in foundation, go to 1
            if no, go to 4
        4. Player checks tableau to foundation placement valid
            if yes, place card into foundation, go to 1 
            if no, go to 5
        5. Player checks if any up facing cards allow stockpile card to place
            if yes, 
                if top card, place stockpile pile card, go to 1
                if middle card, player checks if tableau pile can move to tableau pile for room
                    if yes, move tableau pile, place stockile card, go to 1
                    if no, go to 6,7
        (MAYBE???) 6. Players checks if top of foundation can go to tableau & stockpile can go to moved card
            if yes, move foundation to tableau, then stockpile to tableau, got to 1
            if no, go to 7
        7. Player places stockpile card into wastepile
        


        '''
        
        # 1a. Player checks if stockpile is empty. If yes, reset stockpile from wastepile
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        if len(stock.keys())==0:
            self.reset_stockpile()
            
        # 1b. King Check (check if a King can be placed into an empty tableau pile)
        self.king_check()
        
        # 2. Player pulls stockpile card
        cardID = self.deck.keys()[self.deck.loc['stockID'] == self.deck.loc['stockID'].max()][0] 
        card_data = self.deck[cardID] 
        out = {cardID:'none'} # set default behavior to wastepile
        
        # 3. Player checks stockpile to foundation placement
        # Dependent on strategy. Baseline placing aces into foundation automatically.
        # Must determine if card of rank-1 and same suit exists in foundation already.
        #goToFoundation = False
        if card_data['name'] =='ace': # Aces auto foundation
            #goToFoundation = True
            self.stockpile_to_foundation(cardID)
            return
        else: # if not ace, not foundation possibility
            found = self.deck[self.deck.keys()[self.deck.loc['foundationID']!='00']]
            # Step 1: Determine if rank-1 exists in foundation
            rank_cond = found.loc['rank']==str(int(card_data['rank'])-1)
            
            # Step 2: Determine if rank-1 card has the same suit
            suit_cond = found.loc['suit']==card_data['suit']
            
            # Select foundation opening
            found_card = found[found.keys()[rank_cond & suit_cond]] 
        
            if self.strategy == 'greedy' and len(found_card.keys())>0:
                #goToFoundation = True
                self.stockpile_to_foundation(cardID)
                return
            elif self.strategy == 'other':
                #goToFoundation = True
                self.stockpile_to_foundation(cardID)
                return
        
        # 4. Player checks if any top level tableau cards can go to foundation
        self.tableau_to_foundation()
        
        # 5. Player checks if stockpile card can go to any upwards facing tableau cards
        ### MUST BE CONFIGURED SMARTER TO FOLLOW STEP ABOVE
        tab_card = self.check_stockpile_to_tableau(cardID)
        if len(tab_card.keys())>0:
            self.stockpile_to_tableau(cardID)
            return
        
        # Step 6: Check to see tableau piles can be moved to make space to move to foundation
        moved = self.tableau_move_for_foundation()
        '''if moved:
            # see if stockpile card can move directly into
            tab_card = self.check_stockpile_to_tableau(cardID)
            if len(tab_card.keys())>0:
                out[cardID] = 'tableau' # set flag to tableau if card available
                return out'''
        
        # Step 7: Check to see tableau piles can be moved to make space for stockpile card
        
        
        # Step 8: Check for general tableau swap as last chance
        moved = self.tableau_move()
        '''if moved:
            # see if stockpile card can move directly into
            tab_card = self.check_stockpile_to_tableau(cardID)
            if len(tab_card.keys())>0:
                out[cardID] = 'tableau' # set flag to tableau if card available
                return out'''
        
        # Step 9: Place card in wastepile
        self.stockpile_to_wastepile(cardID)
        return
    
        # Debug Line
        if out[cardID]=='none':
            print('error in card placement')
        
    def king_check(self):
        tabIDs = self.find_top_tab('up')
        find_kings = [idx for idx in tabIDs if S.deck[idx]['name']=='king']
        
        tab = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='00']]
        tabs = np.array([int(a) for a in tab.loc['tableauID']])
        cols = tabs//10 # floor division
        empty_cols = [i for i in range(1,8) if i not in cols]
        
        num_move = max([len(find_kings),len(empty_cols)])
        if len(find_kings)+len(empty_cols)>1:
            for j in range(num_move):
                # Move King to Empty Slot
                cardID = find_kings[j]
                oldID = self.deck[cardID]['tableauID']
                newID = f"{empty_cols[j]}0"
                # Move Tableau card (MUST BE UPDATED TO MOVE FULL PILE)
                print(f"{cardID} moved from tableau into column {empty_cols[j]} in tableau")
                self.update_tableau_visual(cardID,newID,'move') # update visual
                self.deck[cardID]['tableauID'] = newID # update value
                # Flip opened card
                if int(oldID[-1])!=0:
                    nid = self.deck.keys()[self.deck.loc['tableauID']==str(int(oldID)-1)][0]
                    self.deck[nid]['direction']='up'
    
    def stockpile_to_wastepile(self,cardID: str):
        # Move top stockpile card to wastepile (update wasteID, make stockID = 0)
        self.deck[cardID]['wasteID'] = int(self.deck.loc['wasteID'].max())+1
        self.deck[cardID]['stockID'] = 0
        
        # Reset stockpile and flip
        self.deck.loc['direction'][(self.deck.loc['stockID']!='00') & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
        
        print(f"{cardID} moved from stockpile to wastepile")
        self.top_stockpile()
        
    def stockpile_to_foundation(self,cardID: str):
        # Move top stockpile card to wastepile (update foundationID, make stockID = 0)
        self.deck[cardID]['foundationID'] = cardID
        self.deck[cardID]['stockID'] = 0
        
        # Reset stockpile and flip
        self.deck.loc['direction'][(self.deck.loc['stockID']!='00') & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
        
        print(f"{cardID} moved from stockpile to foundation")
        self.top_stockpile()
        
    def find_top_tab(self, direction: str): 
        tab = self.deck[self.deck.keys()[(self.deck.loc['tableauID']!='00') & (self.deck.loc['direction']==direction)]]
        tabs = [int(a) for a in tab.loc['tableauID']]
        tabs = np.array(tabs)
        
        cols = tabs//10 # floor division
        rows = tabs % 10
        
        # Determine Tableau ID for top cards
        endIDs = []
        for c in np.unique(cols):
            max_row = rows[cols==c].max()
            endIDs.extend([str(c)+str(max_row)])
        
        # Convert tableauIDs into cardIDs
        tabIDs = [tid for tid in self.deck.keys() if str(self.deck[tid]['tableauID']) in endIDs]
        return tabIDs
    
    def find_top_foundation(self):
        found = self.deck[self.deck.keys()[self.deck.loc['foundationID']!='00']]
        foundIDs = []
        for sid in self.suits:
            suit_cards = found.loc['rank'][found.loc['suit']==sid]
            if len(suit_cards.keys())>0:
                cardID = suit_cards.keys()[suit_cards==max(suit_cards)][0]
                foundIDs.extend([cardID])
        return foundIDs
    
    def update_tableau_visual(self, cardID: str, tabID: int, action: str):
        # Must be called before updating the tableauID
        col = int(str(tabID)[0])
        row = int(str(tabID)[1])
        if action=='add':
            direction = self.deck[cardID]['direction']
            self.tableau.iloc[row,col-1] = f'{cardID}({direction[0]})'
        elif action=='remove':
            self.tableau.iloc[row,col-1] = np.nan
            # Flip new card
            if not row!=0: # dont flip if top card
                cid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tabID)-1)][0]
                tid = self.deck[cid]['tableauID']
                ncol = int(str(tid)[0])
                nrow = int(str(tid)[1])
                self.tableau.iloc[nrow,ncol-1] = f'{cid}(u)'
        elif action=='move':
            # Add card to new location
            direction = self.deck[cardID]['direction']
            self.tableau.iloc[row,col-1] = f'{cardID}({direction[0]})'
            # Remove card from old location
            tid = self.deck[cardID]['tableauID']
            ncol = int(str(tid)[0])
            nrow = int(str(tid)[1])
            self.tableau.iloc[nrow,ncol-1] = np.nan
            # Flip new card
            if nrow!=0: # dont flip if top card
                cid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tid)-1)][0]
                tid = self.deck[cid]['tableauID']
                ncol = int(str(tid)[0])
                nrow = int(str(tid)[1])
                self.tableau.iloc[nrow,ncol-1] = f'{cid}(u)'
        else:
            print('Invalid Input to Update Tableau Visual')
        print(self.tableau)
        
    def check_stockpile_to_tableau(self, cardID: str):
        card_data = self.deck[cardID]
        
        # Find all cards in tableau 
        tab = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='00']]
        
        # Step 5.1: Determine if cards of rank+1 are in tableau
        rank_cond = tab.loc['rank']==str(int(card_data['rank'])+1)
        
        # Step 5.2: Determine if rank+1 card is face up
        dir_cond = tab.loc['direction']=='up'
        
        # Step 5.3: Determine if rank+1, face up card is opposite color
        clr_cond = tab.loc['color']!=card_data['color']
        
        # Step 5.4: Find available tableau card
        tab_card = tab[tab.keys()[rank_cond & dir_cond & clr_cond]]
        
        # Step 5.5: Confirm possible cards are at end of tableau
        endIDs = self.find_top_tab('up')
        validIDs = [tid for tid in tab_card.keys() if tab_card[tid].name in endIDs]
        tab_card = tab_card[validIDs]
        
        return tab_card
    
    def stockpile_to_tableau(self, cardID: str):
        '''
        Function: Move a single card from the deck to a pile.
        
        !!!!!!MUST HAVE A CHECK TO CONFIRM THAT THE CARD CAN BE MOVED!!!!
        
        Args:
        pileID1: To Be OrderID of card within pile 
        cardID: Card ID (qh = queen of hearts) 
        
        Returns:
        dictionary: 
        '''
        card_data = self.deck[cardID]
        
        if card_data['name']=='king':
            # Check if Empty Column to place king
            tab = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='00']]
            tabs = np.array([int(a) for a in tab.loc['tableauID']])
            cols = tabs//10 # floor division
            empty_cols = [i for i in range(1,8) if i not in cols]
            if len(empty_cols)>0:
                newID = f"{empty_cols[0]}0"
                print(f"{cardID} moved from stockpile into column {empty_cols[0]} in tableau")
                # Move top stockpile card to chosen card in tableau (update tableauID, make stockID = 0)
                self.deck[cardID]['tableauID'] = newID
                self.deck[cardID]['stockID'] = 0
                
                # Reset stockpile and flip
                self.deck.loc['direction'][(self.deck.loc['stockID']!='00') & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
                
                print(f"{cardID} moved from stockpile into column {empty_cols[0]} in tableau")
                self.update_tableau_visual(cardID, newID,'add') # Update tableau visual
                self.top_stockpile()
                return
        
        
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
        endIDs = self.find_top_tab('up')
        validIDs = [tid for tid in open_card.keys() if open_card[tid].name in endIDs]
        open_card = open_card[validIDs]
        
        # CHOOSE FIRST OPTION (TO BE UPDATED WITH STRATEGIES)
        chosen_card = open_card[open_card.keys()[0]]
        
        # Move top stockpile card to chosen card in tableau (update tableauID, make stockID = 0)
        tid = int(chosen_card['tableauID'])+1
        self.deck[cardID]['tableauID'] = str(tid)
        self.deck[cardID]['stockID'] = 0
        
        # Reset stockpile and flip
        self.deck.loc['direction'][(self.deck.loc['stockID']!='00') & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
        
        print(f"{cardID} moved from stockpile onto {chosen_card.name} in tableau")
        self.update_tableau_visual(cardID, tid,'add') # Update tableau visual
        self.top_stockpile()
        return
    
    def tableau_to_foundation(self):
        # Find positions of top most cards of tableau
        tabIDs = self.find_top_tab('up')
        
        # Find top foundation cards
        foundIDs = self.find_top_foundation()
        
        # Automatically move aces in tableau to foundation
        aces = [id for id in self.deck[tabIDs] if self.deck[id].loc['value']==1]
        if len(aces)>0:
            for cid in aces:
                print(f"{cid} moved from tableau into foundation")
                tabID = self.deck[cid]['tableauID']
                self.update_tableau_visual(cid,tabID,'remove')
                self.deck[cid]['foundationID'] = cid
                self.deck[cid]['tableauID'] = '00'
                # Flip opened card
                nid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tabID)-1)][0]
                self.deck[nid]['direction']='up'

        # Check tableau for potential foundation placements
        #cards = [tid for tid in self.deck[tabIDs] for fid in self.deck[foundIDs] if (S.deck[tid].loc['value']==S.deck[fid].loc['value']+1) & (S.deck[tid].loc['suit']==S.deck[fid].loc['suit'])]
        for tid in self.deck[tabIDs]:
            for fid in self.deck[foundIDs]:
                if (self.deck[tid].loc['value']==self.deck[fid].loc['value']+1) & (self.deck[tid].loc['suit']==self.deck[fid].loc['suit']):
                    print(f"{tid} moved from tableau onto {fid} in foundation")
                    tabID = self.deck[tid]['tableauID']
                    self.update_tableau_visual(tid,tabID,'remove')
                    self.deck[tid]['foundationID'] = tid
                    self.deck[tid]['tableauID'] = '00'
                    # Flip opened card
                    if not tabID[-1]<0:
                        nid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tabID)-1)][0]
                        self.deck[nid]['direction']='up'
    
    # Function must work if moving group of cards to new pile
    def tableau_move(self): 
        card_moved = False
        TabIDs = self.find_top_tab('up') # Find top-most, down tableau cards
        for tid in TabIDs:
            for childID in TabIDs:
                if tid!=childID:
                    # Checks for tableau placement
                    rank_cond = self.deck[tid]['rank']==str(int(self.deck[childID]['rank'])+1) # Step 1: Determine if cards of rank+1 are in tableau
                    dir_cond = self.deck[tid]['direction']=='up' # Step 2: Determine if rank+1 card is face up
                    clr_cond = self.deck[tid]['color']!=self.deck[childID]['color'] # Step 3: Determine if rank+1, face up card is opposite color
                    col_cond = self.deck[tid]['tableauID'][0]!=self.deck[childID]['tableauID'][0]
                    if rank_cond & dir_cond & clr_cond & col_cond:
                        card_moved = True
                        oldID = self.deck[childID]['tableauID']
                        newID = str(int(self.deck[tid]['tableauID'])+1)
                        
                        # Move Tableau card (MUST BE UPDATED TO MOVE FULL PILE)
                        print(f"{childID} moved from tableau onto {tid} in tableau")
                        self.update_tableau_visual(childID,newID,'move') # update visual
                        self.deck[childID]['tableauID'] = newID # update value
                        # Flip opened card
                        if int(oldID[-1])!=0:
                            nid = self.deck.keys()[self.deck.loc['tableauID']==str(int(oldID)-1)][0]
                            self.deck[nid]['direction']='up'
        return card_moved
                            
    
    # Function must work if moving group of cards to new pile
    def tableau_move_for_foundation(self):   
        card_moved = False

        # 1. Check to see if any cards above moveable tableau cards can move to foundation
        foundIDs = self.find_top_foundation() # Find top foundation cards
        dTabIDs = self.find_top_tab('down') # Find top-most, down tableau cards
        idxs = []
        for tid in dTabIDs:
            for fid in foundIDs:
                val_cond = self.deck[tid].loc['value']==self.deck[fid].loc['value']+1
                suit_cond = self.deck[tid].loc['suit']==self.deck[fid].loc['suit']
                ace_cond = self.deck[tid]['name']=='ace'
                dup_cond = tid in idxs
                if ((val_cond) & (suit_cond)) or ace_cond:
                    if not dup_cond:
                        idxs.extend([tid])
        canFoundation = self.deck[idxs] 
        
        # 2. Check if parent card can be moved to other tableau pile
        uTabIDs = self.find_top_tab('up') 
        for fid in canFoundation:
            childID = self.deck.keys()[self.deck.loc['tableauID']==str(int(self.deck[fid]['tableauID'])+1)][0]
            for tid in uTabIDs:
                # Checks for tableau placement
                rank_cond = self.deck[tid]['rank']==str(int(self.deck[childID]['rank'])+1) # Step 1: Determine if cards of rank+1 are in tableau
                dir_cond = self.deck[tid]['direction']=='up' # Step 2: Determine if rank+1 card is face up
                clr_cond = self.deck[tid]['color']!=self.deck[childID]['color'] # Step 3: Determine if rank+1, face up card is opposite color
                col_cond = self.deck[tid]['tableauID'][0]!=self.deck[childID]['tableauID'][0]
                if rank_cond & dir_cond & clr_cond & col_cond:
                    #oldID = self.deck[tid]['tableauID']
                    newID = str(int(self.deck[tid]['tableauID'])+1)
                    
                    # Move Tableau card (MUST BE UPDATED TO MOVE FULL PILE)
                    print(f"{childID} moved from tableau onto {tid} in tableau")
                    self.update_tableau_visual(childID,newID,'move') # update visual
                    self.deck[childID]['tableauID'] = newID # update value
                    self.deck[fid]['direction'] = 'up' # flip card
                    
                    # Move Opened Cards to Foundation
                    self.tableau_to_foundation()
                    card_moved = True
                    
        return card_moved

    # Function must work if moving group of cards to new pile
    def tableau_move_for_stockpile(self, cardID: str):  
        # 3. Check to see if stockpile card can move onto open tableau card
        card_data = S.deck[cardID] # Get current stock card data
        
        # Determine up facing tableau cards
        tab = S.deck[S.deck.keys()[(S.deck.loc['tableauID']!='00') & (S.deck.loc['direction']=='up')]]
            
            
            
            
        
# Direct code execution
if __name__ == "__main__":
    selected_seed = 50
    S = Solitaire(selected_seed)
    #S.player() # first move
    #while len(S.deck.keys()[S.deck.loc['stockID']!=0])>0:
    #S.player()
    for i in range(1,24):
        S.player()
