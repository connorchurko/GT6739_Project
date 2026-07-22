import numpy as np
import pandas as pd

class Solitaire:
    # This class is a simulated game of Solitaire
    
    def __init__(self,selected_seed):
        self.strategy = 'greedy'
        self.seed = selected_seed
        self.move_list = []
        self.move_count = 0
        self.last_t2t = ''
        self.game_over = False
        self.result = 'ACTIVE'
        
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
        
        # Add to move list
        self.move_list.extend(['reset'])
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
        
        # 0a. Check Win Criteria
        won = self.check_win()
        if won:
            self.game_over = True
            self.result = "WON"
            return
        
        # 0b. Check Loss Criteria
        lost = self.check_loss()
        if lost:
            self.game_over = True
            self.result = "LOST"
            return
        
        # 1a. Player checks if stockpile is empty. If yes, reset stockpile from wastepile
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        if len(stock.keys())==0:
            self.reset_stockpile()
            
        # 1b. King Check (check if a King can be placed into an empty tableau pile)
        self.king_check()
        
        # 2. Player pulls stockpile card
        cardID = self.deck.keys()[self.deck.loc['stockID'] == self.deck.loc['stockID'].max()][0] 
        card_data = self.deck[cardID] 
        #out = {cardID:'none'} # set default behavior to wastepile
        
        # 3. Player checks stockpile to foundation placement
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
        
            if len(found_card.keys())>0:
                self.stockpile_to_foundation(cardID)
                return
        
        # Step 4: Player checks if any top level tableau cards can go to foundation
        moved = self.tableau_to_foundation()
        if moved:
            return
        
        # Step 5: Check to see tableau piles can be moved to make space to move to foundation
        moved = self.tableau_move_for_foundation()
        if moved:
            return
        
        # Step 6: Player checks if stockpile card can go to any upwards facing tableau cards
        ### MUST BE CONFIGURED SMARTER TO FOLLOW STEP ABOVE
        tab_card = self.check_stockpile_to_tableau(cardID)
        if len(tab_card.keys())>0:
            self.stockpile_to_tableau(cardID)
            return
        
        # Step 7: Check to see tableau piles can be moved to make space for stockpile card
        
        
        # Step 8: Check for general tableau swap as last chance
        moved = self.tableau_move2()
        if moved:
            return
        
        # Step 9: Place card in wastepile
        moved = self.stockpile_to_wastepile(cardID)
        if moved:
            return
    
        # Debug Line
        if True:
            print('error in card placement')
        
    def king_check(self):
        tabIDs = self.find_top_tab('up')
        find_kings = [idx for idx in tabIDs if self.deck[idx]['name']=='king']
        
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
        
        # Update move list
        self.move_list.extend(['waste'])
        self.move_count+=1

        print(f"{cardID} moved from stockpile to wastepile")
        self.top_stockpile()
        return True
        
    def stockpile_to_foundation(self,cardID: str):
        # Move top stockpile card to wastepile (update foundationID, make stockID = 0)
        self.deck[cardID]['foundationID'] = cardID
        self.deck[cardID]['stockID'] = 0
        
        # Reset stockpile and flip
        self.deck.loc['direction'][(self.deck.loc['stockID']!='00') & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
        
        self.move_list.extend(['foundation'])
        self.move_count+=1
        
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
            if row!=0: # dont flip if top card
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
                cid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tid)-1)]
                if len(cid)>0:
                    cid=cid[0]
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
                
                self.move_list.extend(['tableau'])
                self.move_count+=1
                
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
        
        self.move_list.extend(['tableau'])
        self.move_count+=1
        
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
                
                self.move_list.extend(['foundation'])
                self.move_count+=1
                
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
                    
                    self.move_list.extend(['foundation'])
                    self.move_count+=1
                    
                    # Flip opened card
                    if tabID[-1]!=0:
                        nid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tabID)-1)][0]
                        self.deck[nid]['direction']='up'
    
    # Function must work if moving group of cards to new pile
    def tableau_move(self): 
        card_moved = False
        TabIDs = self.find_top_tab('up') # Find top-most, down tableau cards
        for tid in TabIDs:
            for childID in TabIDs:
                if tid!=childID:
                    if (childID!=self.last_t2t) & (self.move_list[-1]!='tableau-tableau'):
                        # Checks for tableau placement
                        rank_cond = self.deck[tid]['rank']==str(int(self.deck[childID]['rank'])+1) # Step 1: Determine if cards of rank+1 are in tableau
                        dir_cond = self.deck[tid]['direction']=='up' # Step 2: Determine if rank+1 card is face up
                        clr_cond = self.deck[tid]['color']!=self.deck[childID]['color'] # Step 3: Determine if rank+1, face up card is opposite color
                        col_cond = self.deck[tid]['tableauID'][0]!=self.deck[childID]['tableauID'][0]
                        if rank_cond & dir_cond & clr_cond & col_cond:
                            card_moved = True
                            oldID = self.deck[childID]['tableauID']
                            newID = str(int(self.deck[tid]['tableauID'])+1)
                            self.last_t2t = childID # head card
                            
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
    def tableau_move2(self):
        card_moved = False
        TabIDs = self.find_top_tab('up')  # Top-most, face-up card in each tableau column (valid destinations)
    
        # All face-up cards currently in the tableau — any of these can be the "head"
        # of a group, not just the exposed top card of a column.
        # (Swap this out for an existing helper if you have one, e.g. self.find_all_tab('up'))
        AllUpIDs = [cid for cid in self.deck.keys()
                    if (self.deck[cid]['direction']=='up') and (self.deck[cid]['tableauID']!='00')]
    
        for tid in TabIDs:
            for childID in AllUpIDs:
                if tid == childID:
                    continue
    
                # Checks for tableau placement (based on the head card of the group, childID)
                rank_cond = self.deck[tid]['rank'] == str(int(self.deck[childID]['rank']) + 1)  # Step 1
                dir_cond = self.deck[tid]['direction'] == 'up'                                   # Step 2
                clr_cond = self.deck[tid]['color'] != self.deck[childID]['color']                 # Step 3
                col_cond = self.deck[tid]['tableauID'][0] != self.deck[childID]['tableauID'][0]
    
                if rank_cond & dir_cond & clr_cond & col_cond:
                    # --- Determine the full group riding along with childID ---
                    src_col = self.deck[childID]['tableauID'][0]
                    child_row = int(self.deck[childID]['tableauID'][1:])
    
                    group_ids = [
                        cid for cid in AllUpIDs
                        if self.deck[cid]['tableauID'][0] == src_col
                        and int(self.deck[cid]['tableauID'][1:]) >= child_row
                    ]
                    group_ids.sort(key=lambda cid: int(self.deck[cid]['tableauID'][1:]))  # bottom (childID) first
    
                    # --- Safety check: confirm it's actually a valid, unbroken sequence ---
                    valid_group = True
                    for i in range(1, len(group_ids)):
                        prev_id, curr_id = group_ids[i - 1], group_ids[i]
                        same_col = self.deck[curr_id]['tableauID'][0] == self.deck[prev_id]['tableauID'][0]
                        next_row = int(self.deck[curr_id]['tableauID'][1:]) == int(self.deck[prev_id]['tableauID'][1:]) + 1
                        rank_seq = self.deck[curr_id]['rank'] == str(int(self.deck[prev_id]['rank']) - 1)
                        alt_clr = self.deck[curr_id]['color'] != self.deck[prev_id]['color']
                        if not (same_col and next_row and rank_seq and alt_clr):
                            valid_group = False
                            break
    
                    if not valid_group:
                        continue
    
                    card_moved = True
                    oldID = self.deck[childID]['tableauID']  # childID's original (lowest-row) position
    
                    # --- Move every card in the group, preserving relative order ---
                    base_row = int(self.deck[tid]['tableauID'][1:]) + 1
                    dest_col = self.deck[tid]['tableauID'][0]
                    prev_landing = tid
                    for offset, cid in enumerate(group_ids):
                        newID = f"{dest_col}{base_row + offset}"
                        print(f"{cid} moved from tableau onto {prev_landing} in tableau")
                        self.update_tableau_visual(cid, newID, 'move')  # update visual
                        self.deck[cid]['tableauID'] = newID             # update value
                        prev_landing = cid
    
                    # --- Flip the newly exposed card in the source column, if any ---
                    if child_row != 0:
                        nid = self.deck.keys()[self.deck.loc['tableauID'] == f"{src_col}{child_row - 1}"][0]
                        self.deck[nid]['direction'] = 'up'
    
        return card_moved                        
    
    # Function must work if moving group of cards to new pile
    def tableau_move_for_foundation(self):   
        card_moved = False

        # 1. Check to see if any cards above moveable tableau cards can move to foundation
        foundIDs = self.find_top_foundation() # Find top foundation cards
        dTabIDs = self.find_top_tab('down') # Find top-most, down tableau cards
        idxs = []
        for tid in dTabIDs:
            if self.deck[tid]['name']=='ace':
                idxs.extend([tid])
            for fid in foundIDs:
                if tid in idxs:
                    continue
                val_cond = self.deck[tid].loc['value']==self.deck[fid].loc['value']+1
                suit_cond = self.deck[tid].loc['suit']==self.deck[fid].loc['suit']
                if (val_cond) & (suit_cond):
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
                    
                    self.move_list.extend(['tableau-tableau'])
                    self.move_count+=1
                    
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
            
    def check_win(self):
        
        numStock = sum(S.deck.loc['stockID']!=0) # number in stockpile
        numTab   = sum(S.deck.loc['tableauID']!='00') # number in tableau
        numWaste = sum(S.deck.loc['wasteID']!=0) # number in wastepile
        numFound = sum(S.deck.loc['foundationID']!='00') # number in foundation
        total_cards = numStock+numTab+numWaste+numFound
        if total_cards!=52:
            raise ValueError(f"Error: Missing Cards. Total cards with valid IDs = {total_cards}")
        cards_on_board = numStock+numTab+numWaste
        if (cards_on_board==0) and (numFound==52):
            return True
            #print("GAME WON")
        return False
        
    def check_loss(self):
        # On a stockpile reset, check running move list. If move list has two restes, and only 
        # consists on tableau-tableau moves or wastepile moves, then lose.
        loss = False
        
        # Index of second to last reset
        indices = [i for i, x in enumerate(self.move_list) if x == 'reset']
        if len(indices)<2:
            return loss
        reset_idx = indices[-2]
        move_subset = self.move_list[reset_idx:]
        
        num_resets = move_subset.count('reset')
        if num_resets < 2:
            return loss
        num_waste = move_subset.count('waste')
        num_tab2tab = move_subset.count('tableau-tableau')
        if num_resets+num_waste+num_tab2tab==len(move_subset):
            loss = True
            #print("GAME LOST")
        return loss
        
        
            
            
        
# Direct code execution
if __name__ == "__main__":
    selected_seed = 50
    S = Solitaire(selected_seed)
    #S.player() # first move
    #while len(S.deck.keys()[S.deck.loc['stockID']!=0])>0:
    #S.player()
    for i in range(1,35):
        if S.game_over:
            print(f"\nGame {S.result} in {S.move_count} moves.")
            break
        S.player()
        
    # replace player() function with strategy ("greedy","random")
