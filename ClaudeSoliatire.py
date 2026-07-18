"""
Klondike Solitaire - Greedy Auto-Player
=========================================

Plays a full game of Klondike Solitaire automatically using a greedy
strategy, printing the tableau state as a pandas DataFrame after every
single move ("turn").

Greedy strategy priority order (evaluated fresh every turn):
    1. Move any available card (from a tableau pile top or the waste
       pile) to a foundation, if legal.
    2. Move a face-up tableau sequence onto another tableau pile if it
       reveals ("flips") a new face-down card.
    3. Move the top of the waste pile onto a tableau pile, if legal.
    4. Move a face-up tableau sequence onto an empty column, if doing
       so uncovers a face-down card in the source pile.
    5. Draw a card from the stock onto the waste pile.
    6. If the stock is empty, recycle the waste pile back into the
       stock (face down) and keep going.

The game ends when either all 52 cards reach the foundations (a win),
a turn limit is hit, or the game reaches a stalemate (a full pass
through the stock produces no progress at all).

Run directly:  python klondike_greedy.py
"""

import random
from dataclasses import dataclass, field
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)

RANKS = list(range(1, 14))  # 1 = Ace ... 13 = King
SUITS = ["S", "H", "D", "C"]  # Spades, Hearts, Diamonds, Clubs
RED_SUITS = {"H", "D"}
BLACK_SUITS = {"S", "C"}

RANK_CHAR = {1: "A", 10: "T", 11: "J", 12: "Q", 13: "K"}


def rank_char(rank: int) -> str:
    return RANK_CHAR.get(rank, str(rank))


@dataclass
class Card:
    rank: int
    suit: str
    face_up: bool = False

    @property
    def color(self) -> str:
        return "R" if self.suit in RED_SUITS else "B"

    def label(self) -> str:
        return f"{rank_char(self.rank)}{self.suit}"

    def __repr__(self):
        return self.label() if self.face_up else "??"


@dataclass
class Game:
    tableau: list = field(default_factory=lambda: [[] for _ in range(7)])
    foundations: dict = field(default_factory=lambda: {s: [] for s in SUITS})
    stock: list = field(default_factory=list)
    waste: list = field(default_factory=list)
    turn_count: int = 0

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def deal(self, seed=None):
        rng = random.Random(seed)
        deck = [Card(r, s) for s in SUITS for r in RANKS]
        rng.shuffle(deck)

        for i in range(7):
            for j in range(i, 7):
                card = deck.pop()
                card.face_up = (j == i)  # only the last card dealt is face up
                self.tableau[j].append(card)

        for card in deck:
            card.face_up = False
        self.stock = deck  # remaining 24 cards, face down

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def is_won(self) -> bool:
        return all(len(pile) == 13 for pile in self.foundations.values())

    def foundation_top_rank(self, suit: str) -> int:
        pile = self.foundations[suit]
        return pile[-1].rank if pile else 0

    def can_go_to_foundation(self, card: Card) -> bool:
        return card.face_up and card.rank == self.foundation_top_rank(card.suit) + 1

    def movable_sequence_starts(self, pile_idx: int):
        """Return list of indices i such that pile[i:] is a valid,
        all-face-up, descending-alternating-color sequence that could be
        moved together onto another pile."""
        pile = self.tableau[pile_idx]
        starts = []
        n = len(pile)
        if n == 0:
            return starts
        # Walk backward from the top while the run stays a valid sequence.
        i = n - 1
        if not pile[i].face_up:
            return starts
        starts.append(i)
        while i > 0:
            upper, lower = pile[i - 1], pile[i]
            if (upper.face_up and upper.color != lower.color
                    and upper.rank == lower.rank + 1):
                i -= 1
                starts.append(i)
            else:
                break
        return starts

    def can_place_sequence(self, card: Card, target_idx: int) -> bool:
        target = self.tableau[target_idx]
        if not target:
            return card.rank == 13  # only Kings go on empty columns
        top = target[-1]
        return top.face_up and top.color != card.color and top.rank == card.rank + 1

    # ------------------------------------------------------------------
    # Actions (each of these represents one "turn")
    # ------------------------------------------------------------------
    def move_card_to_foundation(self, card: Card, source_desc: str):
        self.foundations[card.suit].append(card)
        self.turn_count += 1
        print(f"Turn {self.turn_count}: Move {card.label()} from {source_desc} "
              f"to foundation ({card.suit}).")

    def move_sequence(self, src_idx: int, start: int, dst_idx: int):
        seq = self.tableau[src_idx][start:]
        del self.tableau[src_idx][start:]
        self.tableau[dst_idx].extend(seq)
        flipped = False
        if self.tableau[src_idx] and not self.tableau[src_idx][-1].face_up:
            self.tableau[src_idx][-1].face_up = True
            flipped = True
        self.turn_count += 1
        labels = ", ".join(c.label() for c in seq)
        msg = (f"Turn {self.turn_count}: Move [{labels}] from tableau pile "
               f"{src_idx + 1} to pile {dst_idx + 1}.")
        if flipped:
            msg += f" Flipped {self.tableau[src_idx][-1].label()} face up."
        print(msg)

    def move_waste_to_tableau(self, dst_idx: int):
        card = self.waste.pop()
        self.tableau[dst_idx].append(card)
        self.turn_count += 1
        print(f"Turn {self.turn_count}: Move {card.label()} from waste to "
              f"tableau pile {dst_idx + 1}.")

    def draw_from_stock(self):
        card = self.stock.pop()
        card.face_up = True
        self.waste.append(card)
        self.turn_count += 1
        print(f"Turn {self.turn_count}: Draw {card.label()} from stock to waste.")

    def recycle_waste_into_stock(self):
        self.stock = list(reversed(self.waste))
        for c in self.stock:
            c.face_up = False
        self.waste = []
        self.turn_count += 1
        print(f"Turn {self.turn_count}: Recycle waste pile back into stock "
              f"({len(self.stock)} cards).")

    # ------------------------------------------------------------------
    # Greedy strategy
    # ------------------------------------------------------------------
    def try_foundation_moves(self) -> bool:
        """Send every currently-eligible card to a foundation. Returns True
        if at least one move was made."""
        made_move = False
        progress = True
        while progress:
            progress = False
            # Waste top card
            if self.waste and self.can_go_to_foundation(self.waste[-1]):
                self.move_card_to_foundation(self.waste.pop(), "waste")
                progress = made_move = True
                continue
            # Tableau top cards
            for idx, pile in enumerate(self.tableau):
                if pile and self.can_go_to_foundation(pile[-1]):
                    self.move_card_to_foundation(pile.pop(), f"tableau pile {idx + 1}")
                    progress = made_move = True
                    break
        return made_move

    def try_revealing_tableau_move(self) -> bool:
        """Move a tableau sequence to another (non-empty) pile if it flips
        a face-down card in the source pile."""
        for src_idx, pile in enumerate(self.tableau):
            if len(pile) < 2:
                continue
            if not any(not c.face_up for c in pile):
                continue  # nothing hidden left to reveal in this pile
            starts = self.movable_sequence_starts(src_idx)
            for start in starts:
                if start == 0:
                    continue  # moving whole pile reveals nothing
                if pile[start - 1].face_up:
                    continue  # card below sequence already face up
                card = pile[start]
                for dst_idx in range(7):
                    if dst_idx == src_idx or not self.tableau[dst_idx]:
                        continue
                    if self.can_place_sequence(card, dst_idx):
                        self.move_sequence(src_idx, start, dst_idx)
                        return True
        return False

    def try_waste_to_tableau(self) -> bool:
        if not self.waste:
            return False
        card = self.waste[-1]
        for dst_idx in range(7):
            if self.can_place_sequence(card, dst_idx):
                self.move_waste_to_tableau(dst_idx)
                return True
        return False

    def try_empty_column_move(self) -> bool:
        """Move a King (or a sequence headed by a King) onto an empty
        column, only if it reveals a face-down card in the source pile."""
        empty_targets = [i for i, p in enumerate(self.tableau) if not p]
        if not empty_targets:
            return False
        for src_idx, pile in enumerate(self.tableau):
            if not pile:
                continue
            starts = self.movable_sequence_starts(src_idx)
            for start in starts:
                if start == 0:
                    continue  # would just move the pile into another empty spot
                if pile[start].rank != 13:
                    continue
                if pile[start - 1].face_up:
                    continue  # doesn't reveal anything new
                dst_idx = empty_targets[0]
                self.move_sequence(src_idx, start, dst_idx)
                return True
        return False

    def take_turn(self) -> bool:
        """Perform exactly one greedy action. Returns False if the game is
        completely stuck (no legal action of any kind, including drawing)."""
        if self.try_foundation_moves():
            return True
        if self.try_revealing_tableau_move():
            return True
        if self.try_waste_to_tableau():
            return True
        if self.try_empty_column_move():
            return True
        if self.stock:
            self.draw_from_stock()
            return True
        if self.waste:
            self.recycle_waste_into_stock()
            return True
        return False

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    def tableau_dataframe(self) -> pd.DataFrame:
        columns = {f"Pile {i + 1}": [str(c) for c in pile]
                   for i, pile in enumerate(self.tableau)}
        max_len = max((len(v) for v in columns.values()), default=0)
        for col in columns:
            columns[col] += [""] * (max_len - len(columns[col]))
        df = pd.DataFrame(columns)
        df.index = [f"row {i}" for i in range(max_len)]
        return df

    def print_state(self):
        print(self.tableau_dataframe())
        foundation_str = " | ".join(
            f"{s}: {rank_char(self.foundations[s][-1].rank) if self.foundations[s] else '-'}"
            for s in SUITS
        )
        waste_str = self.waste[-1].label() if self.waste else "-"
        print(f"Foundations -> {foundation_str}")
        print(f"Waste top -> {waste_str}   Stock remaining -> {len(self.stock)}")
        print("-" * 100)


def foundation_count(game: Game) -> int:
    return sum(len(p) for p in game.foundations.values())


def play_game(seed=None, max_turns=1000, stalemate_cycles=3):
    game = Game()
    game.deal(seed=seed)

    print("Initial deal:")
    game.print_state()

    cycles_without_progress = 0
    last_progress_marker = foundation_count(game)

    while game.turn_count < max_turns:
        stock_was_empty_and_waste_present = (not game.stock) and bool(game.waste)

        moved = game.take_turn()
        if not moved:
            print("No legal moves remain. Game is stuck (stalemate).")
            break

        game.print_state()

        if game.is_won():
            print(f"\nSOLVED in {game.turn_count} turns! All 52 cards are on the foundations.")
            return game

        # Detect a full unproductive cycle through the stock/waste.
        if stock_was_empty_and_waste_present:
            current_progress = foundation_count(game)
            if current_progress == last_progress_marker:
                cycles_without_progress += 1
            else:
                cycles_without_progress = 0
                last_progress_marker = current_progress
            if cycles_without_progress >= stalemate_cycles:
                print("No progress after several passes through the stock. "
                      "Declaring stalemate.")
                break

    if not game.is_won():
        print(f"\nGame ended after {game.turn_count} turns without a full win. "
              f"Cards on foundations: {foundation_count(game)}/52.")
    return game


if __name__ == "__main__":
    play_game(seed=21)