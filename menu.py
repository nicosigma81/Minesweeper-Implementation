import pygame
import math


class Menu:

    colour = (150, 150, 150)

    diff_disp = ['Easy', 'Medium', 'Hard']
    diff_idx = 0

    def __init__(self, rect):
        self.rect = rect
        self.x = rect.x
        self.y = rect.y
        self.w = rect.w
        self.h = rect.h

        self.list_s = math.floor((self.h - 60) / 20) - 1
        self.scroll_idx = 0
        self.list_queue = []

        self.difftext = 0
        self.difftextRect = 0

    def mouse_press(self, event):
        if not self.difftextRect == 0 and event.button == 1:
            if self.difftextRect.collidepoint(event.pos):
                self.diff_idx = (self.diff_idx + 1) % 3

    # TODO: Indicate incomplete scroll
    def scroll(self, pos, event):
        list_rect = pygame.Rect(self.x, self.y + 60, self.w, self.list_s * 20)
        if list_rect.collidepoint(pos):
            if self.scroll_idx < len(self.list_queue) - self.list_s:
                self.scroll_idx = max(self.scroll_idx - event.y, 0)
            else:
                self.scroll_idx = min(self.scroll_idx - event.y, len(self.list_queue) - self.list_s)

    def draw(self, screen, font, mouse_pos):

        # Draw main rectangle
        pygame.draw.rect(screen, self.colour, self.rect, 0)

        text = font.render('Times', True, (255, 255, 255), self.colour)
        textRect = text.get_rect()
        textRect.center = (self.x + self.w / 2, self.y + 20)
        screen.blit(text, textRect)

        # Draw difficulty button
        self.difftext = font.render(f"Difficulty: {self.diff_disp[self.diff_idx]}", True, (255, 255, 255), self.colour)
        self.difftextRect = self.difftext.get_rect()
        self.difftextRect.center = (self.x + self.w / 2, self.y + 40)
        # Check for mose hover (this is weirdly inefficient)
        if self.difftextRect.collidepoint(mouse_pos):
            self.difftext = font.render(f"Difficulty: {self.diff_disp[self.diff_idx]}", True, (220, 220, 220), self.colour)
            self.difftextRect = self.difftext.get_rect()
            self.difftextRect.center = (self.x + self.w / 2, self.y + 40)
        screen.blit(self.difftext, self.difftextRect)

        self.list_queue = []
        scores = self.read_score(self.diff_disp[self.diff_idx])
        for score in scores:
            date = score[1].replace("\n", "")
            txt = '{:<8} {:>12}'.format(f'{score[0]}s', date)
            self.list_queue.append(txt)

        # Render times list
        if not len(self.list_queue) > self.list_s:
            self.scroll_idx = 0

        if self.list_queue:
            for i in range(min(self.list_s, len(self.list_queue))):
                txt = self.list_queue[self.scroll_idx + i]
                text = font.render(txt, True, (255, 255, 255), self.colour)
                textRect = text.get_rect()
                textRect.y = self.y + 60 + 20 * i
                center_y = textRect.center[1]
                textRect.center = (self.x + self.w / 2, center_y)
                screen.blit(text, textRect)

        pygame.display.update()

    def read_score(self, diff):
        file = open('scores.txt', 'r')
        times = []
        lines = file.readlines()
        if lines:
            for line in lines:
                delim = line.rsplit(', ')
                if diff == delim[0]:
                    times.append((float(delim[1]), delim[2]))
        times.sort()

        return times
