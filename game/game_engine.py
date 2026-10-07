import pygame
from game.deck import Deck


class GameEngine:
    REVEAL_MS = 1200      # Task 4: how long both cards stay on screen
    MAX_MULTIPLIER = 5    # Task 2: cap so the score can't explode

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.deck = Deck()

        self.current_card = self.deck.draw()
        self.next_card = None
        self.score = 0
        self.streak = 0                 # Task 2
        self.revealing = False          # Task 4
        self.reveal_started = 0         # Task 4
        self.status_msg = "Will the next card be HIGHER or LOWER?"
        self.status_color = (220, 220, 220)

        btn_w, btn_h = 140, 48
        self.btn_higher = pygame.Rect(width // 2 - btn_w - 20, height - 90, btn_w, btn_h)
        self.btn_lower = pygame.Rect(width // 2 + 20, height - 90, btn_w, btn_h)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 30)
        self.font_small = pygame.font.SysFont(None, 24)

    @property
    def multiplier(self):
        # streak 0-1 -> x1, 2 -> x2, ... capped at MAX_MULTIPLIER
        return max(1, min(self.streak, self.MAX_MULTIPLIER))

    def evaluate_guess(self, guess):
        """Draws next card and evaluates prediction."""
        self.next_card = self.deck.draw()
        new, old = self.next_card, self.current_card

        # Task 1: compare numeric value, not the rank string ("10" < "2", "K" < "Q" as strings)
        if new.numeric_rank == old.numeric_rank:
            # Task 3: tie -> push, score and streak untouched
            self.status_msg = f"PUSH! {new.rank_str} ties {old.rank_str} - score and streak kept"
            self.status_color = (230, 200, 90)
        else:
            if guess == "HIGHER":
                correct = new.numeric_rank > old.numeric_rank
            else:
                correct = new.numeric_rank < old.numeric_rank

            if correct:
                # Task 2: escalating reward for consecutive wins
                self.streak += 1
                points = self.multiplier
                self.score += points
                self.status_msg = f"CORRECT! {new.rank_str} vs {old.rank_str}  +{points} (streak {self.streak})"
                self.status_color = (80, 220, 80)
            else:
                self.streak = 0
                self.score = max(0, self.score - 1)
                self.status_msg = f"WRONG! {new.rank_str} vs {old.rank_str}  streak reset"
                self.status_color = (235, 75, 75)

        # Task 4: don't snap - hold both cards on screen, advance in update()
        self.revealing = True
        self.reveal_started = pygame.time.get_ticks()

    def handle_event(self, event):
        if self.revealing:
            return  # ignore clicks during the reveal so guesses can't stack
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_higher.collidepoint(event.pos):
                self.evaluate_guess("HIGHER")
            elif self.btn_lower.collidepoint(event.pos):
                self.evaluate_guess("LOWER")

    def update(self):
        if self.revealing and pygame.time.get_ticks() - self.reveal_started >= self.REVEAL_MS:
            self.current_card = self.next_card
            self.next_card = None
            self.revealing = False

    def _draw_button(self, screen, rect, color, label):
        if self.revealing:
            color = tuple(c // 2 for c in color)  # dim while locked
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (220, 220, 220), rect, width=2, border_radius=8)
        surf = self.font_medium.render(label, True, (255, 255, 255))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))

    def render(self, screen):
        screen.fill((25, 80, 45))

        title_surf = self.font_title.render("High-Low Card Predictor", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (30, 30))

        streak_surf = self.font_small.render(f"Streak: {self.streak}  (x{self.multiplier})", True, (255, 220, 80))
        screen.blit(streak_surf, (30, 60))

        rem_surf = self.font_small.render(f"Deck: {self.deck.remaining} left", True, (210, 210, 210))
        screen.blit(rem_surf, (self.width - rem_surf.get_width() - 30, 35))

        card_w, card_h, gap, card_y = 130, 180, 40, 100
        if self.revealing:
            left_x = self.width // 2 - card_w - gap // 2
            right_x = self.width // 2 + gap // 2
            self.current_card.render(screen, left_x, card_y, card_w, card_h)
            self.next_card.render(screen, right_x, card_y, card_w, card_h)
            for label, cx in (("Previous", left_x), ("New", right_x)):
                s = self.font_small.render(label, True, (210, 210, 210))
                screen.blit(s, (cx + card_w // 2 - s.get_width() // 2, card_y - 22))
        else:
            self.current_card.render(screen, self.width // 2 - card_w // 2, card_y, card_w, card_h)

        status_surf = self.font_small.render(self.status_msg, True, self.status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, 310))

        self._draw_button(screen, self.btn_higher, (40, 140, 60), "HIGHER")
        self._draw_button(screen, self.btn_lower, (170, 50, 50), "LOWER")