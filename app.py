from random import randint
import pygame
from time import time
import datetime

import menu
from menu import Menu

# Game difficulty
game_difficulty = [(10, 10, 'Easy'), (18, 40, 'Medium'), (24, 100, 'Hard')]
difficulty = game_difficulty[0]

# Window and grid parameters
grid_h = difficulty[0]

mine_num = difficulty[1]
start_time = 0
current_time = 0
reset = False

menuDisp = False

win_x, win_y = (800, 600)
scaling_term = 200 * 18 // difficulty[0]
side_len = min(win_x, win_y) - scaling_term
sq_len = side_len // grid_h

offset_x = (win_x - side_len) // 2
offset_y = (win_y - side_len) // 2

# Game parameters
GREEN_LIST = [(121, 255, 48), (64, 181, 0)]
BROWN_LIST = [(214, 188, 109), (140, 103, 0)]

exposed_squares = set()
nums = set()
flagged_squares = set()
mines = set()

player_loses = False
player_wins = False
written = False


def pos_to_grid(pos):
    x, y = pos
    return (x - offset_x) // sq_len, (y - offset_y) // sq_len


def grid_to_pos(grid_pos):
    x, y = grid_pos
    return sq_len * x + offset_x, sq_len * y + offset_y


def generate_nums():
    # calculates the number for each exposed square.
    for square in exposed_squares:
        adj_square = get_adjacent_squares(square)
        number = len(adj_square.intersection(mines))
        nums.add((square, number))


def generate_mines(number, clicked_pos):
    # generates a list of "number" many mines randomly and uniquely
    # TODO: Find a better way to generate mines

    while len(mines) < number:
        rand_pos = (randint(0, grid_h - 1), randint(0, grid_h - 1))
        adj_squares = get_adjacent_squares(clicked_pos)
        if rand_pos not in mines and rand_pos not in adj_squares and rand_pos is not clicked_pos:
            mines.add(rand_pos)


def get_adjacent_squares(square_):
    # Returns a set of all eight adjacent grid squares to "square."
    square_set = set()
    for i in range(3):
        for j in range(3):
            x = square_[0] - 1 + j
            y = square_[1] - 1 + i
            if 0 <= x < grid_h and 0 <= y < grid_h:
                square_set.add((x, y))

    return square_set


def game_update():
    global current_time
    current_time = time() - start_time

    generate_nums()
    val = [False, False]
    for square in nums:
        if square[1] == 0:
            for adj in get_adjacent_squares(square[0]):
                exposed_squares.add(adj)
    if exposed_squares.intersection(mines):
        val[0] = True
    if grid_h**2 - len(exposed_squares) == mine_num and not player_loses:
        val[1] = True

    return val


def write_score(time, diff):
    file = open('scores.txt', 'a')
    file.write(f'{diff}, {time}, {datetime.datetime.now().year}-{datetime.datetime.now().month}' +
               f'-{datetime.datetime.now().day}' + '\n')
    file.close()


pygame.init()
pygame.display.set_caption('Minesweeper')

screen = pygame.display.set_mode((win_x, win_y))
font = pygame.font.Font('freesansbold.ttf', 18 * sq_len // 20)
font_const = pygame.font.Font('freesansbold.ttf', 18)
font2 = pygame.font.Font('freesansbold.ttf', 32)

reset_rect = pygame.Rect(0, 0, 100, 30)
reset_rect.center = (win_x // 2, offset_y + side_len // 2 + 35)

menu_rect = pygame.Rect(0, 0, 200, 400)
menu_rect.center = (win_x // 2, offset_y + side_len // 2 + 35)
menu1 = Menu(menu_rect)

menutextRect = pygame.Rect(0, 0, 0, 0)
difftextRect = pygame.Rect(0, 0, 0, 0)

started = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_pos = pos_to_grid(event.pos)
            if menuDisp:
                menu1.mouse_press(event)
            # If the click is within the grid
            elif 0 <= click_pos[0] < grid_h and 0 <= click_pos[1] < grid_h:
                if event.button == 1 and not player_loses and not player_wins:
                    if click_pos not in flagged_squares:
                        exposed_squares.add(click_pos)
                    if not started:
                        started = True
                        generate_mines(mine_num, click_pos)
                        start_time = time()
                        print("STARTED")
                elif event.button == 3 and not player_loses and not player_wins:
                    if click_pos in flagged_squares:
                        flagged_squares.remove(click_pos)
                    elif click_pos not in exposed_squares:
                        flagged_squares.add(click_pos)
                elif event.button == 2 and not player_loses and not player_wins:
                    if click_pos in exposed_squares:
                        for square in nums:
                            if square[0] == click_pos:
                                adj = get_adjacent_squares(click_pos)
                                flags_next = adj.intersection(flagged_squares)
                                if square[1] == len(flags_next) and not square[1] == 0 and not len(flags_next) == 0:
                                    set_diff1 = adj.difference(flagged_squares)
                                    set_diff2 = set_diff1.difference(exposed_squares)
                                    for chunk in set_diff2:
                                        exposed_squares.add(chunk)

                elif event.button == 1 and (player_loses or player_wins):
                    reset = True
            # Change difficulty
            if difftextRect.collidepoint(event.pos):
                # Change difficulty
                new_index = (game_difficulty.index(difficulty) + 1) % 3
                difficulty = game_difficulty[new_index]

                # Reset window and grid parameters
                grid_h = difficulty[0]
                mine_num = difficulty[1]

                scaling_term = 200 * 18 // difficulty[0]
                side_len = min(win_x, win_y) - scaling_term

                offset_x = (win_x - side_len) // 2
                offset_y = (win_y - side_len) // 2

                sq_len = side_len // grid_h
                font = pygame.font.Font('freesansbold.ttf', 18 * sq_len // 20)

                reset = True

            if menutextRect.collidepoint(event.pos):
                menuDisp = not menuDisp

        if event.type == pygame.MOUSEWHEEL:
            if menuDisp:
                menu1.scroll(pygame.mouse.get_pos(), event)

    # Initialize board
    BACKGROUND = (100, 100, 100)
    screen.fill(BACKGROUND)

    # Draw difficulty button
    difftext = font_const.render(f"Difficulty: {difficulty[2]}", True, (255, 255, 255), BACKGROUND)
    difftextRect = difftext.get_rect()
    wid = 160
    difftextRect.update(10, 10, wid, 20)
    # Check for mose hover (this is weirdly inefficient)
    if difftextRect.collidepoint(pygame.mouse.get_pos()):
        difftext = font_const.render(f"Difficulty: {difficulty[2]}", True, (220, 220, 220), BACKGROUND)
        difftextRect = difftext.get_rect()
        wid = 160
        difftextRect.update(10, 10, wid, 20)
    screen.blit(difftext, difftextRect)

    # Draw menu button
    menutext = font_const.render("Times", True, (255, 255, 255), BACKGROUND)
    menutextRect = menutext.get_rect()
    wid = 60
    menutextRect.update(win_x - wid, 10, wid, 20)
    # Check for mose hover (this is weirdly inefficient)
    if menutextRect.collidepoint(pygame.mouse.get_pos()) or menuDisp:
        menutext = font_const.render("Times", True, (220, 220, 220), BACKGROUND)
        menutextRect = menutext.get_rect()
        menutextRect.update(win_x - wid, 10, wid, 20)
    screen.blit(menutext, menutextRect)

    if started and not player_loses and not player_wins:
        text = font_const.render(f"Time: {round(current_time, 2)}", True, (255, 255, 255), BACKGROUND)
        textRect = text.get_rect()
        textRect.update(offset_x, offset_y - 40, side_len, 20)
        screen.blit(text, textRect)

        text = font_const.render(f"Flags left: {mine_num - len(flagged_squares)}", True,
                           (255, 255, 255), BACKGROUND)
        textRect = text.get_rect()
        textRect.update(offset_x, offset_y - 20, side_len, 20)
        screen.blit(text, textRect)

    for i in range(grid_h):
        for j in range(grid_h):
            x, y = grid_to_pos((i, j))
            pygame.draw.rect(screen, GREEN_LIST[(i + j) % 2], pygame.Rect(x, y, sq_len, sq_len), 0)

    for square in exposed_squares:
        x_grid, y_grid = square
        x, y = grid_to_pos(square)

        pygame.draw.rect(screen, BROWN_LIST[(x_grid + y_grid) % 2], pygame.Rect(x, y, sq_len, sq_len), 0)

    for square in flagged_squares:
        x_grid, y_grid = square
        x, y = grid_to_pos(square)

        pygame.draw.rect(screen, (255, 126, 94), pygame.Rect(x, y, sq_len, sq_len), 0)

    for square in nums:
        number = square[1]
        x, y = square[0]
        x_pos, y_pos = grid_to_pos((x, y))

        if not number == 0:
            text = font.render(str(number), True, (0, 0, 0), BROWN_LIST[(x + y) % 2])
            textRect = text.get_rect()
            textRect.center = (x_pos + sq_len // 2, y_pos + sq_len // 2)
            screen.blit(text, textRect)

    # Handle game ending
    if player_wins and player_loses:
        player_wins = False

    if player_loses:
        # Draw mines
        for square in mines:
            x_grid, y_grid = square
            x, y = grid_to_pos(square)

            pygame.draw.rect(screen, (109, 207, 214), pygame.Rect(x, y, sq_len, sq_len), 0)

        rect1 = pygame.Rect(0, 0, 230, 150)
        rect1.center = (win_x // 2, win_y // 2)
        pygame.draw.rect(screen, (180, 180, 180), rect1)

        text = font2.render("You Lost!", True, (255, 0, 0))
        textRect = text.get_rect()
        textRect.center = (offset_x + side_len // 2, offset_y + side_len // 2)
        screen.blit(text, textRect)

        text = font_const.render(f"Time: {round(current_time, 2)}", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.update(reset_rect)
        screen.blit(text, textRect)

    if player_wins:
        # Draw mines
        for square in mines:
            x_grid, y_grid = square
            x, y = grid_to_pos(square)

            pygame.draw.rect(screen, (109, 207, 214), pygame.Rect(x, y, sq_len, sq_len), 0)

        rect1 = pygame.Rect(0, 0, 230, 150)
        rect1.center = (win_x // 2, win_y // 2)
        pygame.draw.rect(screen, (180, 180, 180), rect1)

        text = font2.render("You Won!", True, (255, 0, 0))
        textRect = text.get_rect()
        textRect.center = (offset_x + side_len // 2, offset_y + side_len // 2)
        screen.blit(text, textRect)

        text = font_const.render(f"Time: {round(current_time, 2)}", True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.update(reset_rect)
        screen.blit(text, textRect)

        if not written:
            write_score(round(current_time, 2), difficulty[2])
            written = True

    if reset:
        reset = False

        exposed_squares = set()
        nums = set()
        flagged_squares = set()
        mines = set()

        player_loses = False
        player_wins = False
        started = False
        written = False

        start_time = 0

    if not player_loses and not player_wins and not menuDisp:
        player_loses, player_wins = game_update()

    # Draw menu
    if menuDisp:
        menu1.draw(screen, font_const, pygame.mouse.get_pos())

    pygame.display.update()
