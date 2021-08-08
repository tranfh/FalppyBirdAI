from neat.reporting import StdOutReporter
import pygame, neat, time, os, random
pygame.font.init()

# Set Dimension of  Screen
WIN_WIDTH = 500
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) # create pygame window
pygame.display.set_caption("Flappy Bird")

# Load Images 
# Make Images 2x Bigger
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),\
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),\
            pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

gen = 0


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
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)
    
    # image when crashed
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200       # how much space in between pipe
    VEL = 5         # move the pipe towards bird to make it look like its moving

    def __init__(self, x) -> None:
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
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
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
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
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
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
    """
    Represnts the moving floor of the game
    """
    # need to make base look like its moving
    VEL = 5     # same as pipe so they move together
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y) -> None:
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        # create 2 images queueing up with each other when moving left after out of screen
        self.x1 -= self.VEL 
        self.x2 -= self.VEL

        # once theyre out of screen width then cycle through the next 
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    # take img and the angle of tilt
    rotated_image = pygame.transform.rotate(image, angle)
    # this fix, rotates the bird from the center of the image
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    # draw background image then the bird on top
    win.blit(BG_IMG, (0,0)) # draw on window

    # draw pipes
    for pipe in pipes:
        pipe.draw(win)
    
    # draw base
    base.draw(win)

    for bird in birds:
    # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass

        # draw bird
        bird.draw(win)

   # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10)) # move the score if it gets bigger 

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()

def eval_genomes(genomes, config):
    """
    :genomes: NEAT requirment
    "config: pass the config file for NEAT
    """
    global WIN, gen
    win = WIN
    gen += 1

    nets = [] # keep track of bird that neural network is controlling
    ge = []     # keep track of genomes to see how the brids are doing 
    birds = []

    # genome is tuple that has id and object so add _
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(genome)


    base = Base(FLOOR)
    pipes = [Pipe(650)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while(run) and len(birds) > 0:
        clock.tick(30) # only runs 30 ticks every second

        # keeps track of user iteraction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        
        # move the birds based on their neural network
        # accounts how many pipes are on the screen
        # tells it which pipe to look at, max 2 at all time 
        pipe_idx = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): # determine whether to use the first or second
                pipe_idx = 1    # pipe on the screen for neural network input
        
        # quit if no birds
        else:
            run = False
            break
        
        for x, bird in enumerate(birds):
            # pass value to neural network for each bird
            # get output value to see if greater than 0.5 and make jump
            # if it reaches this frame add fitness to encourage it to keep moving forward
            ge[x].fitness += 0.1 
            bird.move()

            # activate neural network with out input
            # find distance between bird and the the gap
            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_idx].height), abs(bird.y - pipes[pipe_idx].bottom)))

            # output is a list, in this case we only have one so pass the first element
            if output[0] > 0.5:
                bird.jump()

        base.move()

        # create pipes and generate new pipes
        add_pipe = False
        rem = [] # list of pipes to remove
        for pipe in pipes:
            pipe.move()

            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1      # everytime it hits a pipe have 1 removed from fitness score
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    
            # if pipe is off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5      # if its still a live add 5 to fitness score
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        # check if hit the floor
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() -10 >= FLOOR or bird.y < -50:  # check to make sure bird isnt out of the screen
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)


        draw_window(WIN, birds, pipes, base, score, gen, pipe_idx)

def run(config_path):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    # load config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    # create population
    population = neat.Population(config)

    # give details of the generation
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    # fitness determined based on how far the bird gets in the game
    # call the main fn 50 times to run the bird
    winner = population.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
