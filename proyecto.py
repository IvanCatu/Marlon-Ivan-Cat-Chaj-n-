import pygame
import random

# Inicialización de Pygame
pygame.font.init()

# Constantes del juego
s_width, s_height = 800, 700
play_width, play_height = 300, 600
block_size = 30
top_left_x, top_left_y = (s_width - play_width) // 2, s_height - play_height

# Formatos de las piezas
SHAPES = [
    [['.....', '.....', '..00.', '.00..', '.....'], ['.....', '..0..', '..00.', '...0.', '.....']], # S
    [['.....', '.....', '.00..', '..00.', '.....'], ['.....', '..0..', '.00..', '.0...', '.....']], # Z
    [['..0..', '..0..', '..0..', '..0..', '.....'], ['.....', '0000.', '.....', '.....', '.....']], # I
    [['.....', '.....', '.00..', '.00..', '.....']], # O
    [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '..00.', '..0..', '..0..', '.....'], ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']], # J
    [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'], ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '.00..', '..0..', '..0..', '.....']], # L
    [['.....', '..0..', '.000.', '.....', '.....'], ['.....', '..0..', '..00.', '..0..', '.....'], ['.....', '.....', '.000.', '..0..', '.....'], ['.....', '..0..', '.00..', '..0..', '.....']] # T
]

SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

class Piece:
    def __init__(self, x, y, shape):
        self.x, self.y = x, y
        self.shape = shape
        self.rotation = 0
        self.color = SHAPE_COLORS[SHAPES.index(shape)]

def create_grid(locked_positions):
    return [[locked_positions.get((j, i), (0, 0, 0)) for j in range(10)] for i in range(20)]

def convert_shape_format(piece):
    return [(piece.x + j - 2, piece.y + i - 4) for i, line in enumerate(piece.shape[piece.rotation % len(piece.shape)]) for j, column in enumerate(line) if column == '0']

def valid_space(piece, grid):
    return all((x, y) in [(j, i) for i in range(20) for j in range(10) if grid[i][j] == (0, 0, 0)] or y <= -1 for x, y in convert_shape_format(piece))

def check_lost(positions):
    return any(y < 1 for _, y in positions)

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2, top_left_y + play_height / 2 - label.get_height() / 2))

def draw_grid(surface, grid):
    for i in range(20):
        pygame.draw.line(surface, (128, 128, 128), (top_left_x, top_left_y + i * block_size), (top_left_x + play_width, top_left_y + i * block_size))
        for j in range(10):
            pygame.draw.line(surface, (128, 128, 128), (top_left_x + j * block_size, top_left_y), (top_left_x + j * block_size, top_left_y + play_height))

def clear_rows(grid, locked):
    inc, rows = 0, []
    for i in range(19, -1, -1):
        if (0, 0, 0) not in grid[i]:
            rows.append(i)
    for i in rows:
        for j in range(10):
            locked.pop((j, i), None)
        for key in sorted(list(locked.keys()), key=lambda x: x[1], reverse=True):
            x, y = key
            if y < i:
                locked[(x, y + 1)] = locked.pop((x, y))
        inc += 1
    return inc

def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 30)
    surface.blit(font.render('Next Shape', 1, (255, 255, 255)), (top_left_x + play_width + 50, top_left_y + play_height / 2 - 100))
    for i, line in enumerate(piece.shape[piece.rotation % len(piece.shape)]):
        for j, column in enumerate(line):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (top_left_x + play_width + 50 + j * block_size, top_left_y + play_height / 2 - 50 + i * block_size, block_size, block_size))

def update_score(nscore):
    try:
        with open('scores.txt', 'r') as f:
            high_score = int(f.read())
    except (FileNotFoundError, ValueError):
        high_score = 0
    if nscore > high_score:
        with open('scores.txt', 'w') as f:
            f.write(str(nscore))

def draw_window(surface, grid, score):
    surface.fill((0, 0, 0))
    font = pygame.font.SysFont('comicsans', 60)
    surface.blit(font.render('TetriXNXX', 1, (255, 255, 255)), (top_left_x + play_width / 2 - font.size('TetriXNXX')[0] / 2, 30))
    font = pygame.font.SysFont('comicsans', 30)
    surface.blit(font.render('Score: ' + str(score), 1, (255, 255, 255)), (top_left_x + play_width + 20, top_left_y + play_height / 3 - 40))
    for i, row in enumerate(grid):
        for j, color in enumerate(row):
            pygame.draw.rect(surface, color, (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size))
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)
    draw_grid(surface, grid)

def main(win):
    locked_positions, grid = {}, create_grid({})
    change_piece, run, fall_time, fall_speed, level_time, score = False, True, 0, 0.27, 0, 0
    current_piece, next_piece, clock = get_shape(), get_shape(), pygame.time.Clock()

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Ajustar la velocidad de caída basada en el puntaje
        if score >= 10:
            fall_speed = 0.15
        elif score >= 6:
            fall_speed = 0.20
        else:
            fall_speed = 0.27

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        for x, y in convert_shape_format(current_piece):
            if y >= 0:
                grid[y][x] = current_piece.color
        
        if change_piece:
            for x, y in convert_shape_format(current_piece):
                if y >= 0:
                    locked_positions[(x, y)] = current_piece.color
            change_piece = False
            current_piece, next_piece = next_piece, get_shape()
            if not valid_space(current_piece, grid) or check_lost(locked_positions):
                draw_text_middle(win, "eres manco como yair 17", 40, (255, 255, 255))
                pygame.display.update()
                pygame.time.delay(2000)
                update_score(score)
                run = False

        score += clear_rows(grid, locked_positions) ** 2
        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

def main_menu(win):
    while True:
        win.fill((0, 0, 0))
        draw_text_middle(win, 'Pulse si quiere chevechita', 50, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                main(win)
                return

def run_game():
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('TetriXNXX')
    main_menu(win)

if __name__ == "__main__":
    run_game()
