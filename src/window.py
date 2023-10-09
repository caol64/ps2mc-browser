import sys
from browser import Browser
from canvas import Canvas
import pygame as pg


class Window(Browser):
    def __init__(self, file_path, game_name, win_size=(640, 480), fps=60):
        super().__init__(file_path)
        # pygame init
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        self.screen = pg.display.set_mode(win_size, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        self.running = True
        self.fps = fps
        self.canvas = Canvas(self, game_name)

    def run(self):
        while self.running:
            self.check_events()
            self.render()
            self.clock.tick(self.fps)
        pg.quit()
        sys.exit()

    def render(self):
        self.canvas.render()
        pg.display.flip()

    def check_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                self.running = False


if __name__ == '__main__':
    window = Window('../data/web1.ps2', 'BISCPS-15119sv01')
    window.run()
