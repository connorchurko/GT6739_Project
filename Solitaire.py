import numpy as np
import pandas as pd
import openpyxl

from collections import Counter

class Solitaire:
    # This class is a simulated game of Solitaire
    
    def __init__(self, strategy_in, seed_in):
        self.strategy = strategy_in # greedy, random, foundation_first
        self.seed = seed_in
        self.move_list = ['start']
        self.move_count = 0
        self.last_t2t = []
        self.game_over = False
        self.result = 'ACTIVE'
        self.SWflag = False
        self.system_error = False
        self.max_moves = 500
        
        # Begin Game
        self.initiate_solitaire_board()
        self.player()
        
    def player(self):
        # Function acts like a player choosing strategy, making moves, and evalutaing ending criteria
        # Controlled For loop
        '''for i in range(1,250):
            if self.game_over:
                print(f"\nGame {self.result} in {self.move_count} moves.")
                break
            elif self.system_error:
                break
            self.vibe()'''
        
        # While Loop (may becoeme infinite... use with cauition Must have good boundaries)
        while not self.game_over:
            if self.system_error:
                print("Game LOST: No more available moves.")
                break
            elif self.move_count >= self.max_moves:
                self.result = 'LOST'
                print(f"Game Over: Reached maximum allowable number of moves: {self.max_moves}")
                break
            else:
                match self.strategy:
                    case 'foundation_first':
                        self.foundation_first()
                    case 'greedy':
                        self.greedy()
                    case 'random':
                        self.random()
                    case unknwon_value:
                        print(f"Strategy '{unknwon_value}' is not a valid strategy. Try again.")
                        break
                
        if self.game_over:
            print(f"\nGame {self.result} in {self.move_count} moves.")
            
    def greedy(self):
        # Check Win Criteria
        game_win = self.check_win()
        if game_win:
            self.game_over = True
            self.result = "WON"
            return
        
        # Check Loss Criteria
        lost = self.check_loss()
        if lost:
            self.game_over = True
            self.result = "LOST"
            return
        
        # Player checks if stockpile is empty. If yes, reset stockpile from wastepile
        self.reset_stockpile()
            
        # King Check (check if a King can be placed into an empty tableau pile)
        self.tableau_to_empty_move()
        
        # Check for general tableau swap as last chance
        moved = self.tableau_to_tableau()
        if moved:
            return
        
        # Player checks if any top level tableau cards can go to foundation
        moved = self.tableau_to_foundation()
        if moved:
            self.last_t2t = []
            return
        
        #  Player checks stockpile to foundation placement
        moved = self.stockpile_to_foundation()
        if moved:
            self.last_t2t = []
            return       
        
        # Player checks if stockpile card can go to any upwards facing tableau cards
        moved = self.stockpile_to_tableau()
        if moved:
            self.last_t2t = []
            return
        
        # Place card in wastepile
        moved = self.stockpile_to_wastepile()
        if moved:
            self.last_t2t = []
            return
    
        # Debug Line
        if True:
            self.system_error = True
            self.result = "LOST"
            print('Stopping Play: Error in Card Placement')
            
    def random(self):
        # Check Win Criteria
        game_win = self.check_win()
        if game_win:
            self.game_over = True
            self.result = "WON"
            return
        
        # Check Loss Criteria
        lost = self.check_loss()
        if lost:
            self.game_over = True
            self.result = "LOST"
            return
        
        # Player checks if stockpile is empty. If yes, reset stockpile from wastepile
        self.reset_stockpile()
            
        # King Check (check if a King can be placed into an empty tableau pile)
        self.tableau_to_empty_move()
        
        # Create Methods List
        methods = [
            self.stockpile_to_foundation,
            self.tableau_to_foundation,
            self.stockpile_to_tableau,
            self.tableau_to_tableau,
            self.stockpile_to_wastepile
            ]
        
        # Randomized Methods List
        rng = np.random.default_rng()
        rng_array = rng.choice(np.arange(0,len(methods)), size=len(methods), replace=False)
        methods = [methods[i] for i in rng_array]
        
        # Run Randomized Order of Method
        for method in methods:
            moved = method()
            if moved:
                # Reset last tableau move
                if self.move_list[-1]!='tableau-tableau':
                    self.last_t2t = []
                break
        if moved:
            return
    
        # Debug Line
        if True:
            self.system_error = True
            self.result = "LOST"
            print('Stopping Play: Error in Card Placement')
        
        
    
    def foundation_first(self):   
        # Check Win Criteria
        game_win = self.check_win()
        if game_win:
            self.game_over = True
            self.result = "WON"
            return
        
        # Check Loss Criteria
        lost = self.check_loss()
        if lost:
            self.game_over = True
            self.result = "LOST"
            return
        
        # Player checks if stockpile is empty. If yes, reset stockpile from wastepile
        self.reset_stockpile()
            
        # King Check (check if a King can be placed into an empty tableau pile)
        self.tableau_to_empty_move()
        
        # Player checks stockpile to foundation placement
        moved = self.stockpile_to_foundation()
        if moved:
            self.last_t2t = []
            return
        
        # Player checks if any top level tableau cards can go to foundation
        moved = self.tableau_to_foundation()
        if moved:
            self.last_t2t = []
            return
        
        # Player checks if stockpile card can go to any upwards facing tableau cards
        moved = self.stockpile_to_tableau()
        if moved:
            self.last_t2t = []
            return
        
        # Check for general tableau swap as last chance
        moved = self.tableau_to_tableau()
        if moved:
            return
        
        # Place card in wastepile
        moved = self.stockpile_to_wastepile()
        if moved:
            self.last_t2t = []
            return
    
        # Debug Line
        if True:
            self.system_error = True
            self.result = "LOST"
            print('Stopping Play: Error in Card Placement')
            
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
            self.deck[str(key)]['tableauID'] = '000'
        
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
                self.deck[card_name].tableauID = f"{pile}{position:02}" # update tableauID in stockpile
                
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
            index=range(19),
            columns=[f'column{i}' for i in range(1, 8)]
            )
        
        # Create visual representation of tableau
        tableau_df = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='000']]
        for cid in tableau_df.keys():
            tid = tableau_df[cid]['tableauID']
            col = int(str(tid)[0])
            row = int(str(tid)[1:])
            dir = tableau_df[cid]['direction']
            self.tableau.iloc[row,col-1] = f'{cid}({dir[0]})'
        print(self.tableau)
     
    def top_stockpile(self):
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        waste = self.deck[self.deck.keys()[self.deck.loc['wasteID']!=0]]
        if not self.SWflag:
            if (len(waste.keys())==0 and len(stock.keys())==0):
                self.SWflag = True
                print("Stockpile and wastepile empty.")
                return
            elif len(stock.keys())==0:
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
        
        # Confirm cards left in stockpile and/or wastepile
        waste = self.deck[self.deck.keys()[self.deck.loc['wasteID']!=0]]
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        if (len(waste.keys())==0 and len(stock.keys())==0):
            return
        elif len(stock.keys())==0:
            # Set stockIDs based on wasteIDs
            self.deck.loc['stockID'][self.deck.loc['wasteID']!=0] = abs(self.deck.loc['wasteID']-self.deck.loc['wasteID'].max())+1
            self.deck.loc['direction'][self.deck.loc['stockID']==self.deck.loc['stockID'].max()] = 'up' 
            
            # Set WasteIDs to Zero
            self.deck.loc['wasteID'] = 0
            
            # Add to move list
            self.move_list.extend(['reset'])
            print('Reseting stockpile from wastepile')            
                    
    def tableau_to_empty_move(self):
        card_moved = False
    
        # --- Your empty-column search ---
        tab = self.deck[self.deck.keys()[self.deck.loc['tableauID'] != '000']]
        cols = np.array([int(a[0]) for a in tab.loc['tableauID']])
        empty_cols = [i for i in range(1, 8) if i not in cols]
    
        if not empty_cols:
            return card_moved  # no empty columns available, nothing to do
    
        # All face-up cards currently in the tableau (candidates to be a group "head")
        AllUpIDs = [cid for cid in self.deck.keys()
                    if self.deck[cid]['direction'] == 'up' and self.deck[cid]['tableauID'] != '000']
    
        # Only Kings can be placed into an empty column
        KingIDs = [cid for cid in AllUpIDs if self.deck[cid]['rank'] == '13']
    
        for childID in KingIDs:
            src_col = int(self.deck[childID]['tableauID'][0])
            child_row = int(self.deck[childID]['tableauID'][1:]) 
    
            # Guard: skip if this King is already alone at the bottom of its column
            # (row 0) — moving it to another empty column would be a pointless no-op.
            if child_row == 0:
                continue
    
            # --- Build the group riding on top of the King (same logic as before) ---
            group_ids = [
                cid for cid in AllUpIDs
                if int(self.deck[cid]['tableauID'][0]) == src_col
                and int(self.deck[cid]['tableauID'][1:]) >= child_row
            ]
            group_ids.sort(key=lambda cid: int(self.deck[cid]['tableauID'][1:]))  # King first, then descending ranks
    
            # --- Validate it's an unbroken King-high sequence ---
            valid_group = True
            for i in range(1, len(group_ids)):
                prev_id, curr_id = group_ids[i - 1], group_ids[i]
                same_col = (int(self.deck[curr_id]['tableauID'][0]) ==
                            int(self.deck[prev_id]['tableauID'][0]))
                next_row = (int(self.deck[curr_id]['tableauID'][1:]) ==
                            int(self.deck[prev_id]['tableauID'][1:]) + 1)
                rank_seq = self.deck[curr_id]['rank'] == str(int(self.deck[prev_id]['rank']) - 1)
                alt_clr = self.deck[curr_id]['color'] != self.deck[prev_id]['color']
                if not (same_col and next_row and rank_seq and alt_clr):
                    valid_group = False
                    break
    
            if not valid_group:
                continue
    
            dest_col = empty_cols[0]  # pick the first available empty column
            card_moved = True
            #oldID = self.deck[childID]['tableauID']
    
            # --- Move every card in the group into the empty column ---
            prev_landing = None
            for offset, cid in enumerate(group_ids):
                newID = f"{dest_col}{offset:02}"
                print(f"{cid} moved from tableau onto empty column {dest_col}"
                      if prev_landing is None else f"{cid} moved from tableau onto {prev_landing} in tableau")
                self.update_tableau_visual(cid, newID, 'move')  # update visual
                self.deck[cid]['tableauID'] = newID             # update value
                prev_landing = cid
    
            # --- Flip the newly exposed card in the source column, if any ---
            if child_row != 0:
                nid = self.deck.keys()[self.deck.loc['tableauID'] == f"{src_col}{child_row - 1:02}"][0]
                self.deck[nid]['direction'] = 'up'
    
            empty_cols.pop(0)  # that column is no longer empty
            if not empty_cols:
                break  # no more empty columns left to fill
    
        return card_moved
    
    def stockpile_to_wastepile(self):
        # Check Stockpile Empty
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        if (len(stock.keys())==0):
            return False
        
        cardID = self.deck.keys()[self.deck.loc['stockID'] == self.deck.loc['stockID'].max()][0] 
        
        # Move top stockpile card to wastepile (update wasteID, make stockID = 0)
        self.deck[cardID]['wasteID'] = int(self.deck.loc['wasteID'].max())+1
        self.deck[cardID]['stockID'] = 0
        
        # Reset stockpile and flip
        self.deck.loc['direction'][(self.deck.loc['stockID']!=0) & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
        
        # Update move list
        self.move_list.extend(['waste'])
        self.move_count+=1

        print(f"{cardID} moved from stockpile to wastepile")
        self.top_stockpile()
        return True
        
    def stockpile_to_foundation(self):
        # Check Stockpile Empty
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        if (len(stock.keys())==0):
            return False
        cardID = self.deck.keys()[self.deck.loc['stockID'] == self.deck.loc['stockID'].max()][0] 
        card_data = self.deck[cardID] 
        if card_data['name'] =='ace': # Aces auto foundation
            self.deck[cardID]['foundationID'] = cardID# Move top stockpile card to wastepile (update foundationID, make stockID = 0)
            self.deck[cardID]['stockID'] = 0
            
            # Reset stockpile and flip
            self.deck.loc['direction'][(self.deck.loc['stockID']!=0) & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
            
            self.move_list.extend(['foundation'])
            self.move_count+=1
            
            print(f"{cardID} moved from stockpile to foundation")
            self.top_stockpile()
            return True
        else: # if not ace, not foundation possibility
            found = self.deck[self.deck.keys()[self.deck.loc['foundationID']!='00']]
            # Step 1: Determine if rank-1 exists in foundation
            rank_cond = found.loc['rank']==str(int(card_data['rank'])-1)
            
            # Step 2: Determine if rank-1 card has the same suit
            suit_cond = found.loc['suit']==card_data['suit']
            
            # Select foundation opening
            found_card = found[found.keys()[rank_cond & suit_cond]] 
        
            if len(found_card.keys())>0:
                # Move top stockpile card to wastepile (update foundationID, make stockID = 0)
                self.deck[cardID]['foundationID'] = cardID
                self.deck[cardID]['stockID'] = 0
                
                # Reset stockpile and flip
                self.deck.loc['direction'][(self.deck.loc['stockID']!=0) & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
                
                self.move_list.extend(['foundation'])
                self.move_count+=1
                
                print(f"{cardID} moved from stockpile to foundation")
                self.top_stockpile()
                return True
        return False
            
    def find_top_tab(self, direction: str): 
        tab = self.deck[self.deck.keys()[(self.deck.loc['tableauID']!='000') & (self.deck.loc['direction']==direction)]]
        cols = np.array([int(c[0]) for c in tab.loc['tableauID']])
        rows = np.array([int(c[1:]) for c in tab.loc['tableauID']])
        
        # Determine Tableau ID for top cards
        endIDs = []
        for c in np.unique(cols):
            max_row = rows[cols==c].max()
            endIDs.extend([f"{c}{max_row:02}"])
        
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
        row = int(str(tabID)[1:])
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
                nrow = int(str(tid)[1:])
                self.tableau.iloc[nrow,ncol-1] = f'{cid}(u)'
        elif action=='move':
            # Add card to new location
            direction = self.deck[cardID]['direction']
            self.tableau.iloc[row,col-1] = f'{cardID}({direction[0]})'
            # Remove card from old location
            tid = self.deck[cardID]['tableauID']
            ncol = int(str(tid)[0])
            nrow = int(str(tid)[1:])
            self.tableau.iloc[nrow,ncol-1] = np.nan
            # Flip new card
            if nrow!=0: # dont flip if top card
                cid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tid)-1)]
                if len(cid)>0:
                    cid=cid[0]
                    tid = self.deck[cid]['tableauID']
                    ncol = int(str(tid)[0])
                    nrow = int(str(tid)[1:])
                    self.tableau.iloc[nrow,ncol-1] = f'{cid}(u)'
        else:
            print('Invalid Input to Update Tableau Visual')
        print(self.tableau)
    
    def stockpile_to_tableau(self):
        '''
        Function: Move a single card from the deck to a pile.
        
        !!!!!!MUST HAVE A CHECK TO CONFIRM THAT THE CARD CAN BE MOVED!!!!
        
        Args:
        pileID1: To Be OrderID of card within pile 
        cardID: Card ID (qh = queen of hearts) 
        
        Returns:
        dictionary: 
        '''
        # Check Stockpile Empty
        stock = self.deck[self.deck.keys()[self.deck.loc['stockID']!=0]]
        if (len(stock.keys())==0):
            return False
        
        cardID = self.deck.keys()[self.deck.loc['stockID'] == self.deck.loc['stockID'].max()][0] 
        card_data = self.deck[cardID] 
        
        if card_data['name']=='king':
            # Check if Empty Column to place king
            tab = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='000']]
            cols = [int(a[0]) for a in tab.loc['tableauID']]            
            empty_cols = [i for i in range(1,8) if i not in cols]
            if len(empty_cols)>0:
                newID = f"{empty_cols[0]}00"
                # Move top stockpile card to chosen card in tableau (update tableauID, make stockID = 0)
                self.deck[cardID]['tableauID'] = newID
                self.deck[cardID]['stockID'] = 0
                
                self.move_list.extend(['tableau'])
                self.move_count+=1
                
                # Reset stockpile and flip
                self.deck.loc['direction'][(self.deck.loc['stockID']!=0) & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
                
                print(f"{cardID} moved from stockpile into column {empty_cols[0]} in tableau")
                self.update_tableau_visual(cardID, newID,'add') # Update tableau visual
                self.top_stockpile()
                return True

        # Check to Confirm There is a card suitable in tableau
        # Find all cards in tableau 
        tab = self.deck[self.deck.keys()[self.deck.loc['tableauID']!='000']]
        
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
        open_card = tab_card[validIDs]
        
        if len(open_card.keys())==0:
            return False
        
        # CHOOSE FIRST OPTION (TO BE UPDATED WITH STRATEGIES)
        chosen_card = open_card[open_card.keys()[0]]
        
        # Move top stockpile card to chosen card in tableau (update tableauID, make stockID = 0)
        tid = int(chosen_card['tableauID'])+1
        self.deck[cardID]['tableauID'] = str(tid)
        self.deck[cardID]['stockID'] = 0
        
        self.move_list.extend(['tableau'])
        self.move_count+=1
        
        # Reset stockpile and flip
        self.deck.loc['direction'][(self.deck.loc['stockID']!=0) & (self.deck.loc['stockID']==self.deck.loc['stockID'].max())] = 'up'
        print(f"{cardID} moved from stockpile onto {chosen_card.name} in tableau")
        self.update_tableau_visual(cardID, tid,'add') # Update tableau visual
        self.top_stockpile()
        return True
    
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
                self.deck[cid]['tableauID'] = '000'
                
                self.move_list.extend(['foundation'])
                self.move_count+=1
                
                # Flip opened card
                if tabID[1:]!='00':
                    print(tabID)
                    nid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tabID)-1)][0]
                    self.deck[nid]['direction']='up'
                return True

        # Check tableau for potential foundation placements
        #cards = [tid for tid in self.deck[tabIDs] for fid in self.deck[foundIDs] if (S.deck[tid].loc['value']==S.deck[fid].loc['value']+1) & (S.deck[tid].loc['suit']==S.deck[fid].loc['suit'])]
        for tid in self.deck[tabIDs]:
            for fid in self.deck[foundIDs]:
                if (self.deck[tid].loc['value']==self.deck[fid].loc['value']+1) & (self.deck[tid].loc['suit']==self.deck[fid].loc['suit']):
                    print(f"{tid} moved from tableau onto {fid} in foundation")
                    tabID = self.deck[tid]['tableauID']
                    self.update_tableau_visual(tid,tabID,'remove')
                    self.deck[tid]['foundationID'] = tid
                    self.deck[tid]['tableauID'] = '000'
                    
                    self.move_list.extend(['foundation'])
                    self.move_count+=1
                    
                    
                    # Flip opened card
                    if tabID[1:]!='00':
                        nid = self.deck.keys()[self.deck.loc['tableauID']==str(int(tabID)-1)][0]
                        self.deck[nid]['direction']='up'
                    return True    
        return False
    
    # Function must work if moving group of cards to new pile
    def tableau_to_tableau(self):
        TabIDs = self.find_top_tab('up')  # Top-most, face-up card in each tableau column (valid destinations)
    
        # All face-up cards currently in the tableau — any of these can be the "head"
        # of a group, not just the exposed top card of a column.
        # (Swap this out for an existing helper if you have one, e.g. self.find_all_tab('up'))
        AllUpIDs = [cid for cid in self.deck.keys()
                    if (self.deck[cid]['direction']=='up') and (self.deck[cid]['tableauID']!='000')]
    
        # First determine all valid tableau-tableau options
        move_options = []
        for tid in TabIDs:
            for childID in AllUpIDs:
                if tid == childID:
                    continue
                #if not ((childID==self.last_t2t) and (self.move_list[-1]=='tableau-tableau')):
                if (childID not in self.last_t2t) and (self.move_list[-1:]!='tableau-tableau'):
                    # Checks for tableau placement (based on the head card of the group, childID)
                    rank_cond = self.deck[tid]['rank'] == str(int(self.deck[childID]['rank']) + 1)  # Step 1
                    dir_cond = self.deck[tid]['direction'] == 'up'                                   # Step 2
                    clr_cond = self.deck[tid]['color'] != self.deck[childID]['color']                 # Step 3
                    col_cond = self.deck[tid]['tableauID'][0] != self.deck[childID]['tableauID'][0]
        
                    if rank_cond & dir_cond & clr_cond & col_cond:
                        move_options.append([tid,childID])
        
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
                    
        if len(move_options)==0:
            return False
        
        # Select highest card if two possible tableau-tableau moves are in the same column
        by_src_col = {}
        for tid, childID in move_options:
            src_col = self.deck[childID]['tableauID'][0]
            by_src_col.setdefault(src_col, []).append((tid, childID))
        selected_candidates = []
        for src_col, matches in by_src_col.items():
            best_tid, best_childID = max(
                matches, key=lambda pair: int(self.deck[pair[1]]['rank'])
            )
            selected_candidates.append([best_tid, best_childID])
            
        # Prioritize card where cards above are faced down
        direction_priority = []
        for sc in selected_candidates:
            spid = sc[0]
            scid = sc[1]
            scol = int(self.deck[scid]['tableauID'][0])
            srow = int(self.deck[scid]['tableauID'][1:])-1
            cids = self.deck.keys()[self.deck.loc['tableauID']==f"{scol}{srow:02}"]
            for n in cids:
                if self.deck[n]['direction']=='down':
                    direction_priority.append([spid, scid])       
                        
        # Replace selecetd candidates with priority                
        if len(direction_priority)>0:
            selected_candidates = direction_priority
            
        # Determine random choice
        rng = np.random.default_rng()
        rng_idx = int(rng.integers(low=0, high=len(selected_candidates), size=1))
        #print(selected_candidates)
        #print(rng_idx)
        tid = selected_candidates[rng_idx][0]
        childID = selected_candidates[rng_idx][1]
        
        # --- Determine the full group riding along with childID ---
        src_col = self.deck[childID]['tableauID'][0]
        child_row = int(self.deck[childID]['tableauID'][1:])

        # Given smaller sample size, redo group
        group_ids = [
            cid for cid in AllUpIDs
            if self.deck[cid]['tableauID'][0] == src_col
            and int(self.deck[cid]['tableauID'][1:]) >= child_row
        ]
        group_ids.sort(key=lambda cid: int(self.deck[cid]['tableauID'][1:]))  # bottom (childID) first

        # --- Move every card in the group, preserving relative order ---
        base_row = int(self.deck[tid]['tableauID'][1:]) + 1
        dest_col = self.deck[tid]['tableauID'][0]
        prev_landing = tid
        for offset, cid in enumerate(group_ids):
            newID = f"{dest_col}{base_row + offset:02}"
            print(f"{cid} moved from tableau onto {prev_landing} in tableau")
            self.update_tableau_visual(cid, newID, 'move')  # update visual
            self.deck[cid]['tableauID'] = newID             # update value
            prev_landing = cid
        self.move_list.extend(['tableau-tableau'])
        self.move_count+=1
        self.last_t2t.extend([childID])

        # --- Flip the newly exposed card in the source column, if any ---
        if child_row != 0:
            nid = self.deck.keys()[self.deck.loc['tableauID'] == f"{src_col}{child_row - 1:02}"][0]
            self.deck[nid]['direction'] = 'up'
        self.top_stockpile()
        return True                        
            
    def check_win(self):
        # Check win criteria to end game
        numStock = sum(self.deck.loc['stockID']!=0) # number in stockpile
        numTab   = sum(self.deck.loc['tableauID']!='000') # number in tableau
        numWaste = sum(self.deck.loc['wasteID']!=0) # number in wastepile
        numFound = sum(self.deck.loc['foundationID']!='00') # number in foundation
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
        
        if self.move_count >= 300:
            return True
        
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
    # Setup up of initial variables for simulation runs, plan is to run
    # three different strategies back to back to back. Will store required
    # info and output as a table
    
    n = 1000
    winRate = 0
    movesToWin = 0
    strategies = ['greedy', 'foundation_first', 'random']

    output_df = pd.DataFrame(columns = ['Strategy', 'wins', 'losses', 'winRate', 'avgMovesPerWin', 'move_std_Dev', 'avgMovesPerLoss'])

    data_df = pd.DataFrame(columns = ['Seed', 'Strategy', 'Result', 'moveCount', 't2t_count', 'tableau_count', 'waste_count', 'foundation_count', 'moveList'])


    for strat in strategies:
        wins = 0
        losses = 0
        moves_win = 0
        moves_loss = 0
        for i in range(n):
            S = Solitaire(strat,i)
            if S.result == "WON":
                wins += 1
                moves_win = moves_win + S.move_count
            elif S.result == "LOST":
                losses += 1
                moves_loss = moves_loss + S.move_count
            move_counts = Counter(S.move_list)
            t2t_count = move_counts.get('tableau-tableau', 0)
            tableau_count = move_counts.get('tableau', 0)
            waste_count = move_counts.get('waste', 0)
            foundation_count = move_counts.get('foundation', 0)
            data_df.loc[len(data_df)] = [S.seed, S.strategy, S.result, S.move_count, t2t_count, tableau_count, waste_count, foundation_count, S.move_list]

        # Adding a catch statement if there are somehow zero wins (for random strat)
        if wins == 0:
            avgMovesPerWin = 0
        else:
            avgMovesPerWin = moves_win/wins
        winRate = wins/n

        avgMovesPerLoss = moves_loss/losses
        move_count_arr = np.array(data_df.loc[data_df['Strategy'] == strat, 'moveCount'].tolist())
        move_std_dev = np.std(move_count_arr)
        output_df.loc[len(output_df)] = [S.strategy, wins, losses, winRate, avgMovesPerWin, move_std_dev, avgMovesPerLoss]      

    with pd.ExcelWriter('Solitaire Data.xlsx', engine='openpyxl') as writer:
        data_df.to_excel(writer, sheet_name='Move Data', index=False)
        output_df.to_excel(writer, sheet_name='Output Data', index=False)
    
