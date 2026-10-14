import pygame
import sys
import random
import time
import math

pygame.init()

# ── Constants ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 900, 700
GRID_COLS, GRID_ROWS = 5, 5
DOT_COLS = GRID_COLS + 1
DOT_ROWS = GRID_ROWS + 1

MARGIN_X, MARGIN_Y = 240, 80
CELL = 90
DOT_R = 7
LINE_W = 6
HOVER_W = 4
FPS = 60

# Colors
ACCENT1  = (0, 230, 180)
ACCENT2  = (255, 80, 120)
AI_COL   = (80, 160, 255)
DOT_COL  = (220, 220, 255)
GRID_COL = (40, 40, 70)
BOX_ALPHA = 140
WHITE    = (255, 255, 255)
YELLOW   = (255, 215, 0)
PANEL_BG = (18, 18, 36)

# Fonts
try:
    FONT_BIG   = pygame.font.SysFont("couriernew", 52, bold=True)
    FONT_MED   = pygame.font.SysFont("couriernew", 28, bold=True)
    FONT_SM    = pygame.font.SysFont("couriernew", 20)
    FONT_TITLE = pygame.font.SysFont("couriernew", 72, bold=True)
except:
    FONT_BIG   = pygame.font.SysFont(None, 52)
    FONT_MED   = pygame.font.SysFont(None, 28)
    FONT_SM    = pygame.font.SysFont(None, 20)
    FONT_TITLE = pygame.font.SysFont(None, 72)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DOTS & BOXES — vs AI")
clock = pygame.time.Clock()


# ── Helper ─────────────────────────────────────────────────────────────────
def dot_pos(r, c):
    return (MARGIN_X + c * CELL, MARGIN_Y + r * CELL)


# ── Game Class ─────────────────────────────────────────────────────────────
class Game:
    def __init__(self, player_initial):
        self.pi = player_initial.upper()[:1] or "P"
        self.ai_init = "AI"

        # h_lines[r][c] — horizontal line at row r between col c and c+1
        # dimensions: DOT_ROWS rows, GRID_COLS cols
        self.h_lines = [[False] * GRID_COLS for _ in range(DOT_ROWS)]

        # v_lines[c][r] — vertical line at col c between row r and r+1
        # dimensions: DOT_COLS cols, GRID_ROWS rows
        self.v_lines = [[False] * GRID_ROWS for _ in range(DOT_COLS)]

        self.boxes = [[None] * GRID_COLS for _ in range(GRID_ROWS)]
        self.player_score = 0
        self.ai_score = 0
        self.turn = "player"
        self.game_over = False
        self.winner = None
        self.particles = []
        self.ai_thinking = False
        self.ai_think_start = 0

    def total_lines(self):
        h = sum(1 for r in range(DOT_ROWS) for c in range(GRID_COLS) if self.h_lines[r][c])
        v = sum(1 for c in range(DOT_COLS) for r in range(GRID_ROWS) if self.v_lines[c][r])
        return h + v

    def max_lines(self):
        return GRID_COLS * DOT_ROWS + GRID_ROWS * DOT_COLS

    def check_complete(self):
        return self.total_lines() >= self.max_lines()

    def make_move(self, is_h, r, c, who):
        """Draw a line. Returns True if a box was closed (extra turn)."""
        if is_h:
            if self.h_lines[r][c]:
                return False
            self.h_lines[r][c] = True
        else:
            if self.v_lines[c][r]:
                return False
            self.v_lines[c][r] = True

        closed = self._find_new_boxes(who)
        earned = len(closed) > 0

        if who == "player":
            self.player_score += len(closed)
        else:
            self.ai_score += len(closed)

        for (br, bc) in closed:
            self.spawn_particles(br, bc, who)

        if self.check_complete():
            self.game_over = True
            if self.player_score > self.ai_score:
                self.winner = "player"
            elif self.ai_score > self.player_score:
                self.winner = "ai"
            else:
                self.winner = "draw"

        return earned

    def _find_new_boxes(self, who):
        """Scan for any newly completed boxes and mark them."""
        newly = []
        for br in range(GRID_ROWS):
            for bc in range(GRID_COLS):
                if self.boxes[br][bc] is None:
                    if (self.h_lines[br][bc] and self.h_lines[br + 1][bc] and
                            self.v_lines[bc][br] and self.v_lines[bc + 1][br]):
                        self.boxes[br][bc] = who
                        newly.append((br, bc))
        return newly

    def spawn_particles(self, br, bc, who):
        cx, cy = dot_pos(br, bc)
        cx += CELL // 2
        cy += CELL // 2
        col = ACCENT1 if who == "player" else AI_COL
        for _ in range(18):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(1.5, 4.5)
            life = random.randint(25, 50)
            self.particles.append({
                'x': cx, 'y': cy,
                'vx': speed * math.cos(angle),
                'vy': speed * math.sin(angle),
                'life': life, 'max_life': life,
                'col': col, 'r': random.randint(2, 5)
            })

    def update_particles(self):
        alive = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['life'] -= 1
            if p['life'] > 0:
                alive.append(p)
        self.particles = alive

    # ── AI: Minimax + Alpha-Beta Pruning ───────────────────────────────────
    def ai_move(self):
        move = self._minimax_choose()
        if move:
            is_h, r, c = move
            extra = self.make_move(is_h, r, c, "ai")
            #bonus move
            if extra and not self.game_over:
                self.ai_thinking = True
                self.ai_think_start = time.time()
            else:
                self.turn = "player"
        else:
            self.turn = "player"
#finds all moves and stores empty lines
    def _all_moves(self):
        moves = []
        for r in range(DOT_ROWS):
            for c in range(GRID_COLS):
                if not self.h_lines[r][c]:
                    moves.append((True, r, c))
        for c in range(DOT_COLS):
            for r in range(GRID_ROWS):
                if not self.v_lines[c][r]:
                    moves.append((False, r, c))
        return moves
#makes copy of current board
    def _state_snapshot(self):
        return {
            'h': [row[:] for row in self.h_lines],
            'v': [col[:] for col in self.v_lines],
            'boxes': [row[:] for row in self.boxes],
            'ai_score': self.ai_score,
            'player_score': self.player_score,
        }
#finds empty moves inside copy board
    def _state_moves(self, state):
        moves = []
        for r in range(DOT_ROWS):
            for c in range(GRID_COLS):
                if not state['h'][r][c]:
                    moves.append((True, r, c))
        for c in range(DOT_COLS):
            for r in range(GRID_ROWS):
                if not state['v'][c][r]:
                    moves.append((False, r, c))
        return moves
#copies board applies fake move checks boxes updates fake scores
    def _state_apply(self, state, is_h, r, c, is_maximizer):
        """
        Expand one node in the decision tree.
        Copies the state, applies the move, finds newly closed boxes.
        Returns (new_state, boxes_scored, extra_turn).
        """
        s = {
            'h': [row[:] for row in state['h']],
            'v': [col[:] for col in state['v']],
            'boxes': [row[:] for row in state['boxes']],
            'ai_score': state['ai_score'],
            'player_score': state['player_score'],
        }

        if is_h:
            s['h'][r][c] = True
        else:
            s['v'][c][r] = True

        scored = 0
        for br in range(GRID_ROWS):
            for bc in range(GRID_COLS):
                if s['boxes'][br][bc] is None:
                    if (s['h'][br][bc] and s['h'][br + 1][bc] and
                            s['v'][bc][br] and s['v'][bc + 1][br]):
                        s['boxes'][br][bc] = 'ai' if is_maximizer else 'player'
                        if is_maximizer:
                            s['ai_score'] += 1
                        else:
                            s['player_score'] += 1
                        scored += 1

        return s, scored, scored > 0
#is fake board complete for minmax 
    def _state_complete(self, state):
        h_cnt = sum(1 for r in range(DOT_ROWS) for c in range(GRID_COLS) if state['h'][r][c])
        v_cnt = sum(1 for c in range(DOT_COLS) for r in range(GRID_ROWS) if state['v'][c][r])
        return (h_cnt + v_cnt) >= self.max_lines()
#ai evaluates the points how to not give easy box wins to user and winning more points(+ai,-p)comparing scores and risky positions 
    def _heuristic(self, state):
        """
        Evaluate a board state from AI's perspective.
        Positive = AI winning. Negative = Player winning.
        """
        score = state['ai_score'] - state['player_score']
        # Penalise 3-sided boxes (gifts to the next player)
        for br in range(GRID_ROWS):
            for bc in range(GRID_COLS):
                if state['boxes'][br][bc] is None:
                    sides = (int(state['h'][br][bc]) + int(state['h'][br + 1][bc]) +
                             int(state['v'][bc][br]) + int(state['v'][bc + 1][br]))
                    if sides == 3:
                        score -= 0.5
        return score

    def _minimax(self, state, depth, alpha, beta, is_maximizer):
        """
        ┌─────────────────────────────────────────────────┐
        │   MINIMAX DECISION TREE + ALPHA-BETA PRUNING    │
        │                                                 │
        │  is_maximizer=True  → AI's turn   (MAX node)   │
        │  is_maximizer=False → Player's turn (MIN node) │
        │                                                 │
        │  alpha = best score MAX can guarantee so far   │
        │  beta  = best score MIN can guarantee so far   │
        │                                                 │
        │  Prune when beta <= alpha                      │
        └─────────────────────────────────────────────────┘
        """
        if self._state_complete(state) or depth == 0:
            return self._heuristic(state), None

        moves = self._state_moves(state)
        if not moves:
            return self._heuristic(state), None

        # Move ordering: box-closing moves first (improves pruning efficiency)
        def move_priority(m):
            ns, scored, _ = self._state_apply(state, *m, is_maximizer)
            return -scored
        moves.sort(key=move_priority)

        best_move = None

        if is_maximizer:
            max_eval = float('-inf')
            for move in moves:
                new_state, scored, extra_turn = self._state_apply(state, *move, True)
                # Scored a box → AI gets another turn → still maximizer
                next_is_max = True if extra_turn else False
                eval_score, _ = self._minimax(new_state, depth - 1, alpha, beta, next_is_max)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # ✂ Alpha cut-off
            return max_eval, best_move

        else:
            min_eval = float('inf')
            for move in moves:
                new_state, scored, extra_turn = self._state_apply(state, *move, False)
                # Scored a box → Player gets another turn → still minimizer
                next_is_max = False if extra_turn else True
                eval_score, _ = self._minimax(new_state, depth - 1, alpha, beta, next_is_max)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # ✂ Beta cut-off
            return min_eval, best_move

    def _minimax_choose(self):
        """Entry point — build the decision tree and return the best move."""
        state = self._state_snapshot()
        moves = self._state_moves(state)
        if not moves:
            return None

        remaining = len(moves)
        if remaining <= 8:
            depth = 8
        elif remaining <= 20:
            depth = 5
        else:
            depth = 3

        _, best_move = self._minimax(state, depth, float('-inf'), float('inf'), True)
        return best_move if best_move else random.choice(moves)


# ── Drawing ────────────────────────────────────────────────────────────────
def draw_gradient_bg():
    for y in range(HEIGHT):
        r = int(10 + 8 * (y / HEIGHT))
        g = int(10 + 5 * (y / HEIGHT))
        b = int(20 + 15 * (y / HEIGHT))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))


def draw_grid(game, hover_line):
    # Filled boxes
    for br in range(GRID_ROWS):
        for bc in range(GRID_COLS):
            who = game.boxes[br][bc]
            if who:
                x, y = dot_pos(br, bc)
                col = ACCENT1 if who == "player" else AI_COL
                surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                surf.fill((*col, BOX_ALPHA))
                screen.blit(surf, (x, y))
                init = game.pi if who == "player" else game.ai_init
                lbl = FONT_MED.render(init, True, WHITE)
                screen.blit(lbl, (x + CELL // 2 - lbl.get_width() // 2,
                                  y + CELL // 2 - lbl.get_height() // 2))

    # Ghost horizontal lines
    for r in range(DOT_ROWS):
        for c in range(GRID_COLS):
            if not game.h_lines[r][c]:
                x1, y1 = dot_pos(r, c)
                pygame.draw.line(screen, GRID_COL, (x1, y1), (x1 + CELL, y1), 2)

    # Ghost vertical lines
    for c in range(DOT_COLS):
        for r in range(GRID_ROWS):
            if not game.v_lines[c][r]:
                x1, y1 = dot_pos(r, c)
                pygame.draw.line(screen, GRID_COL, (x1, y1), (x1, y1 + CELL), 2)

    # Drawn horizontal lines
    for r in range(DOT_ROWS):
        for c in range(GRID_COLS):
            if game.h_lines[r][c]:
                x1, y1 = dot_pos(r, c)
                pygame.draw.line(screen, WHITE, (x1, y1), (x1 + CELL, y1), LINE_W)

    # Drawn vertical lines
    for c in range(DOT_COLS):
        for r in range(GRID_ROWS):
            if game.v_lines[c][r]:
                x1, y1 = dot_pos(r, c)
                pygame.draw.line(screen, WHITE, (x1, y1), (x1, y1 + CELL), LINE_W)

    # Hover highlight
    if hover_line:
        is_h, r, c = hover_line
        if is_h and not game.h_lines[r][c]:
            x1, y1 = dot_pos(r, c)
            pygame.draw.line(screen, ACCENT1, (x1, y1), (x1 + CELL, y1), HOVER_W)
        elif not is_h and not game.v_lines[c][r]:
            x1, y1 = dot_pos(r, c)
            pygame.draw.line(screen, ACCENT1, (x1, y1), (x1, y1 + CELL), HOVER_W)

    # Dots
    for r in range(DOT_ROWS):
        for c in range(DOT_COLS):
            x, y = dot_pos(r, c)
            pygame.draw.circle(screen, DOT_COL, (x, y), DOT_R)
            pygame.draw.circle(screen, ACCENT1, (x, y), DOT_R + 2, 1)


def draw_side_panel(game, left):
    pw, py = 180, 80
    px = 18 if left else WIDTH - 198
    ph = HEIGHT - 160

    surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
    surf.fill((18, 18, 36, 200))
    screen.blit(surf, (px, py))
    col = ACCENT1 if left else AI_COL
    pygame.draw.rect(screen, col, (px, py, pw, ph), 2, border_radius=8)

    name   = game.pi if left else game.ai_init
    score  = game.player_score if left else game.ai_score
    tag    = "YOU" if left else "CPU"
    active = (game.turn == "player") if left else (game.turn == "ai")

    if active and not game.game_over:
        pygame.draw.rect(screen, col, (px, py, pw, 5))
        label = "▶ YOUR TURN" if left else "▶ AI TURN"
        t = FONT_SM.render(label, True, col)
        screen.blit(t, (px + pw // 2 - t.get_width() // 2, py + 12))

    t = FONT_BIG.render(name, True, col)
    screen.blit(t, (px + pw // 2 - t.get_width() // 2, py + 50))

    t = FONT_SM.render(tag, True, (160, 160, 200))
    screen.blit(t, (px + pw // 2 - t.get_width() // 2, py + 105))

    pygame.draw.line(screen, col, (px + 20, py + 130), (px + pw - 20, py + 130), 1)

    t = FONT_SM.render("BOXES", True, (160, 160, 180))
    screen.blit(t, (px + pw // 2 - t.get_width() // 2, py + 140))

    t = FONT_TITLE.render(str(score), True, YELLOW)
    screen.blit(t, (px + pw // 2 - t.get_width() // 2, py + 165))

    total = GRID_ROWS * GRID_COLS
    t = FONT_SM.render(f"/ {total}", True, (120, 120, 160))
    screen.blit(t, (px + pw // 2 - t.get_width() // 2, py + 235))

    bx, by = px + 15, py + 270
    bw, bh = pw - 30, 12
    pygame.draw.rect(screen, (40, 40, 60), (bx, by, bw, bh), border_radius=6)
    fill = int(bw * score / max(total, 1))
    if fill > 0:
        pygame.draw.rect(screen, col, (bx, by, fill, bh), border_radius=6)


def draw_particles(game):
    for p in game.particles:
        alpha = int(255 * p['life'] / p['max_life'])
        surf = pygame.Surface((p['r'] * 2, p['r'] * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*p['col'], alpha), (p['r'], p['r']), p['r'])
        screen.blit(surf, (int(p['x']) - p['r'], int(p['y']) - p['r']))


RESTART_BTN = (WIDTH // 2 - 120, HEIGHT // 2 + 80,  220, 50)
QUIT_BTN    = (WIDTH // 2 - 120, HEIGHT // 2 + 145, 220, 50)


def is_button_click(mx, my, which):
    x, y, w, h = RESTART_BTN if which == "restart" else QUIT_BTN
    return x <= mx <= x + w and y <= my <= y + h


def draw_end_overlay(game):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    bx, by, bw, bh = WIDTH // 2 - 220, HEIGHT // 2 - 160, 440, 330
    pygame.draw.rect(screen, (15, 15, 30), (bx, by, bw, bh), border_radius=18)
    pygame.draw.rect(screen, YELLOW, (bx, by, bw, bh), 3, border_radius=18)

    if game.winner == "player":
        msg, col = "YOU  WIN!", ACCENT1
    elif game.winner == "ai":
        msg, col = "AI  WINS!", AI_COL
    else:
        msg, col = "IT'S A DRAW!", YELLOW

    t = FONT_BIG.render(msg, True, col)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + 25))

    t = FONT_MED.render(f"You: {game.player_score}   AI: {game.ai_score}", True, WHITE)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + 90))

    mx, my = pygame.mouse.get_pos()
    for rect, label, bcol in [
        (RESTART_BTN, "PLAY  AGAIN", ACCENT1),
        (QUIT_BTN,    "QUIT",        ACCENT2),
    ]:
        x, y, w, h = rect
        hover = x <= mx <= x + w and y <= my <= y + h
        pygame.draw.rect(screen, bcol if hover else (40, 40, 60), (x, y, w, h), border_radius=10)
        if not hover:
            pygame.draw.rect(screen, bcol, (x, y, w, h), 2, border_radius=10)
        t = FONT_MED.render(label, True, WHITE if hover else bcol)
        screen.blit(t, (x + w // 2 - t.get_width() // 2, y + h // 2 - t.get_height() // 2))

    t = FONT_SM.render("R = restart    Q = quit", True, (120, 120, 150))
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, by + bh - 35))


# ── Screens ────────────────────────────────────────────────────────────────
def get_hover(mx, my):
    thresh = 14
    for r in range(DOT_ROWS):
        for c in range(GRID_COLS):
            x1, y1 = dot_pos(r, c)
            if abs(my - y1) < thresh and x1 < mx < x1 + CELL:
                return (True, r, c)
    for c in range(DOT_COLS):
        for r in range(GRID_ROWS):
            x1, y1 = dot_pos(r, c)
            if abs(mx - x1) < thresh and y1 < my < y1 + CELL:
                return (False, r, c)
    return None


def input_screen():
    name = ""
    blink = 0
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.random()) for _ in range(80)]

    while True:
        clock.tick(FPS)
        blink += 1
        draw_gradient_bg()

        for sx, sy, sz in stars:
            br = int(80 + 120 * sz)
            pygame.draw.circle(screen, (br, br, br + 40), (sx, sy), int(1 + sz * 1.5))

        t = FONT_TITLE.render("DOTS & BOXES", True, ACCENT1)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 80))

        t = FONT_MED.render("vs  THE  MACHINE", True, AI_COL)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 155))

        box_x, box_y, box_w, box_h = WIDTH // 2 - 160, 290, 320, 70
        pygame.draw.rect(screen, PANEL_BG, (box_x - 4, box_y - 4, box_w + 8, box_h + 8), border_radius=12)
        pygame.draw.rect(screen, ACCENT1, (box_x, box_y, box_w, box_h), 2, border_radius=10)

        t = FONT_SM.render("ENTER YOUR INITIAL (1 letter):", True, WHITE)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 265))

        disp = name + ("|" if blink % 60 < 30 else " ")
        t = FONT_BIG.render(disp, True, YELLOW)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, box_y + 12))

        t = FONT_SM.render("Press  ENTER  to  start", True, (160, 160, 200))
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 390))

        rules = [
            "HOW TO PLAY:",
            "Click between dots to draw a line.",
            "Close a box to score + play again!",
            "Most boxes wins. Beat the AI!",
        ]
        for i, line in enumerate(rules):
            col = ACCENT2 if i == 0 else (160, 160, 180)
            t = FONT_SM.render(line, True, col)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 450 + i * 28))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 1 and event.unicode.isalpha():
                    name = event.unicode.upper()


def game_screen(player_initial):
    game = Game(player_initial)
    hover_line = None
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.random()) for _ in range(60)]

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        # AI turn logic
        if game.turn == "ai" and not game.game_over:
            if not game.ai_thinking:
                game.ai_thinking = True
                game.ai_think_start = time.time()
            elif time.time() - game.ai_think_start >= 0.7:
                game.ai_thinking = False
                game.ai_move()

        # Hover detection
        hover_line = None
        if game.turn == "player" and not game.game_over:
            hover_line = get_hover(mx, my)

        # Draw everything
        draw_gradient_bg()
        for sx, sy, sz in stars:
            br = int(60 + 80 * sz)
            pygame.draw.circle(screen, (br, br, br + 30), (sx, sy), int(1 + sz))

        draw_side_panel(game, left=True)
        draw_side_panel(game, left=False)
        draw_grid(game, hover_line)
        draw_particles(game)

        if game.game_over:
            draw_end_overlay(game)

        if game.ai_thinking and not game.game_over:
            t = FONT_SM.render("AI  IS  THINKING...", True, AI_COL)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT - 38))

        pygame.display.flip()
        game.update_particles()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.game_over:
                    if is_button_click(mx, my, "restart"):
                        return "restart"
                    if is_button_click(mx, my, "quit"):
                        pygame.quit(); sys.exit()
                elif game.turn == "player" and hover_line:
                    is_h, r, c = hover_line
                    extra = game.make_move(is_h, r, c, "player")
                    if not extra and not game.game_over:
                        game.turn = "ai"


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    while True:
        pi = input_screen()
        result = game_screen(pi)
        if result != "restart":
            break

if __name__ == "__main__":
    main()
