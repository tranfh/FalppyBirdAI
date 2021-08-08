import pygame, neat, time, os, random
pygame.font.init()

# Set Dimension of  Screen
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Load Images 
# Make Images 2x Bigger
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),\
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),\
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
    """
    Represents Flappy Bird
    """

    IMGS = BIRD_IMGS
    # How much the bird will tilt
    MAX_ROTATION = 25
    # How much rotate on each frame
    ROT_VEL = 20
    # How long the animation is
    ANIMATION_TIME = 5

    def __init__(self, x, y) -> None:
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0           # position of bird on start
        self.tick_count = 0     # physics of bird
        self.vel = 0            # how fast the bird is moving
        self.height = self.y
        self.img_count = 0      # Which image to load
        self.img = self.IMGS[0]
    
    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.vel = -10.5        # to go up need a negative in y direction
        self.tick_count = 0     # keep track of when we last jump
        self.height = self.y    # keep track of where bird started jumping from
    
    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1    # frame went by, how many seconds went by
        displacement = self.vel*(self.tick_count) + 1.5*(3)*(self.tick_count)**2 # how many picels we move up or down the frame  starts negative to positive (makes arc for our bird)

        # max out at 16 pixels
        # terminal velocity
        if displacement >= 16:
            displacement = 16
        
        # if moving up just finetune to move up an additional 2
        if displacement < 0:
            displacement -= 2
        
        # moving the height of the bird
        self.y = self.y + displacement

        # tilt the bird depending on direction
        # check if bird position above the height position, once reach below then we can tilt else dont
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        # tilt bird down
        # tilt 90 to make the bird look like its nose diving 
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    # win represents the window the bird is drawn on
    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

        # For animation of bird, loop through three images
        # check what image we should show based on img_count 
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        
        # when bird is tilted dopwnwards we dont want it to flap its wing
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            # when we go back up this prevents it from skipping a frame - more smooth
            self.img_count = self.ANIMATION_TIME*2
    
        # tilting the bird
        # take img and the angle of tilt
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        # this fix, rotates the bird from the center of the image
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)
    
    # image when crashed
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200       # how much space in between pipe
    VEL = 5         # move the pipe towards bird to make it look like its moving

    def __init__(self, x) -> None:
        self.x = x      # only x because height of tube should be random
        self.height = 0

        # keep track of where the top and bottom pipe will be 
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()     # figure out where the height of the top left of the pipe is
        self.bottom = self.height + self.GAP
    
    def move(self):
        #change x position based on velocity of the frame
        self.x -= self.VEL # move slightly left
    
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x,self.bottom))
    
    # imagine box around all out objects
    # check if the boxes collide with eachother
    def collide(self, bird):
        # mask is an 2D array of where all the pixels are in the box 
        # check if any of the pixels in the mask are touching 
        # mask figures out where all the pixels are
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # calculate offset / how far away the masks are from each other 
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # find point of collision
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # check if theyre none
        if t_point or b_point:
            return True
        
        return False

class Base:
    # need to make base look like its moving
    VEL = 5     # same as pipe so they move together
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y) -> None:
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        # create 2 images queueing up with each other when moving left after out of screen
        self.x1 -= self.VEL 
        self.x2 -= self.VEL

        # once theyre out of screen width then cycle through the next 
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, bird, pipes, base, score):
    # draw background image then the bird on top
    win.blit(BG_IMG, (0,0)) # draw on window

    # draw pipes
    for pipe in pipes:
        pipe.draw(win)
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10)) # move the score if it gets bigger
    # draw base
    base.draw(win)
    # draw bird
    bird.draw(win)

    pygame.display.update()

def main():
    bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(650)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # create pygame window
    clock = pygame.time.Clock()

    run = True
    while(run):
        clock.tick(30) # only runs 30 ticks every second
        # keeps track of user iteraction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        bird.move()

        # create pipes and generate new pipes
        add_pipe = False
        rem = [] # list of pipes to remove
        score = 0
        for pipe in pipes:
            if pipe.collide(bird):
                pass
            # if pipe is off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()
        
        if add_pipe:
            score += 1
            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)

        # check if hit the floor
        if bird.y + bird.img.get_height() >= 70:
            pass
        base.move()
        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()