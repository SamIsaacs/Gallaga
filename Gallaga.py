import pygame
import random
import sys
import time


# This is the class for the overlay that contains the score and lives information
class Overlay(pygame.sprite.Sprite):
    # Constructor for Overlay
    def __init__(self):
        super(pygame.sprite.Sprite, self).__init__()
        # Specifies the size of the text box and makes it a rectangle
        self.image = pygame.Surface((500, 20))
        self.rect = self.image.get_rect()
        # Sets the font style and size
        self.font = pygame.font.Font('freesansbold.ttf', 18)
        # These are the starting values for lives and score
        self.render('Score: 0        Lives: 3')

    # Sets the text of the overlay based on score and lives passed in
    def render(self, text):
        # Makes text white
        self.text = self.font.render(text, True, (255, 255, 255))
        # Writes the text to the overlay
        self.image.blit(self.text, self.rect)

    # Draws the overlay to the screen
    def draw(self, screen):
        # Draws the overlay at the top right of the screen
        screen.blit(self.text, (0, 0))

    # Sets the texted based on the score and lives of the game
    def update(self, score, lives):
        self.render('Score: ' + str(score) + '        Lives: ' + str(lives))

# Class for the player's ship
class Ship(pygame.sprite.Sprite):
    # Constructor for the Ship class
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # The ship will take up a 20 by 2 pixel area
        self.image = pygame.Surface((20, 20))
        # Sets the color of the ship to a dark green
        self.image.fill((20, 100, 0))
        # Sets the starting location of the ship
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 650

    # Draws the ship onto the screen
    def draw(self, screen):
        screen.blit(self.image, self.rect)


# Class for the enemy ships
class Enemy(pygame.sprite.Sprite):
    # Constructor for the enemy class
    # @param color - The RGB values for the ship's color
    # @param position - The starting position for the ship
    def __init__(self, color, position):
        pygame.sprite.Sprite.__init__(self)
        # The enemy will take up a 20 by 20 area
        self.image = pygame.Surface((20, 20))
        # Sets the color to be the colors passed in
        self.image.fill((color[0], color[1], color[2]))
        # Sets the position to be what was passed in
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        # The ship starts moving right
        self.direction = 1

    # Function to determine if the ships need to change direction
    # @param enemies - The group of enemy sprites being used by the game
    def changeDirection(self, enemies):
        # Runs through all the enemeies and checks if each one is on the edge of the screen
        for e in enemies:
            if e.rect.x <= 0 or e.rect.x >= 580:
                # If a ship is on the edge of the screen, the function returns -1,
                # indicating that the ships need to change direction
                return -1
        # If none of the ships are on the edge of the screen, it returns 1, keeping the ships moving the same direction
        return 1

    # The function to move the enemies and draw them to the screen
    # @param screen - The screen to which we need to draw the enemy
    def update(self, screen):
        # Moves the enemy in the correct direction
        self.rect.x += self.direction
        # Draws the enemy to the screen
        screen.blit(self.image, self.rect)

    # Function to determine if the enemy will shoot and to produce a projectile if it does
    # @param game - all the game data we need to access
    def shoot(self, game):
        # Randomly generated a number in a ranged based on the number of enemies remaining.
        # Therefore, each ship will have a greater chance of firing a projectile the fewer enemies there are remaining.
        # The multiplier of 20 is essentially a difficulty multiplier. It can be lowered to increase the chance that the
        # ship will fire a projectile and thus increase the difficulty.
        shotchance = random.randint(0, len(game.enemies)*20)
        if shotchance == 1:
            # Creates a non-friendly projectile in the middle of the ship, at a random downward angle.
            # It always has a vertical velocity of 3.
            projectile = Projectile([self.rect.x + 10, self.rect.y], [random.randint(-2, 2), 3], False)
            # Adds the projectile to the projectiles group of the game
            game.projectiles.add(projectile)


# Class for all the projectiles in the game
class Projectile(pygame.sprite.Sprite):
    # Constructor for the Projectile class
    # @param position - a tuple containing the starting coordinates for the projectile
    # @param vector - a tuple containing the x and y velocities of the projectile
    # @param friendly - a bool determining whether the projectile was fired by the player or by an enemy
    def __init__(self, position, vector, friendly):
        pygame.sprite.Sprite.__init__(self)
        self.friendly = friendly
        # Each projectile takes up a space of 4 by 10 pixels
        self.image = pygame.Surface((4, 10))
        if self.friendly:
            # if the projectile was fired by the player, the color of the projectile is set to white
            self.image.fill((255, 255, 255))
            # Sets the sound of the projectile firing to the appropriate soundbyte
            self.fire_sound = pygame.mixer.Sound('assets/friendly_fire.mp3')
            # Sets the appropriate volume for the sound
            self.fire_sound.set_volume(.6)
        else:
            # If the projectile was fired by an enemy, the color is red
            self.image.fill((255, 0, 0))
            # Sets the sound of the projectile firing to the appropriate soundbyte
            self.fire_sound = pygame.mixer.Sound('assets/enemy_fire.mp3')
            # Sets the appropriate volume for the sound. The volume is low because there are lots of enemy projectiles
            # fired per second
            self.fire_sound.set_volume(.15)
        # Sets the sound to be played when the projectile hits a ship
        self.hit_sound = pygame.mixer.Sound('assets/explosion.mp3')
        # Sets the appropriate volume for the sound
        self.hit_sound.set_volume(.3)
        self.rect = self.image.get_rect()
        # Sets the starting x and y coordinates of the projectile
        self.rect.x = position[0]
        self.rect.y = position[1]
        # Sets the x and y velocities of the projectile
        self.vector = vector
        # Plays the appropriate sound effect based on whether the projectile is friendly or from an enemy
        self.fire_sound.play()

    # Updates the position of the projectile
    # @param game - all the game data we need to access
    def update(self, game):
        # If the projectile hits the edge of the screen, it is removed from the game's projectiles group
        if self.rect.x < 0 or self.rect.x > 600 or self.rect.y < 0 or self.rect.y > 800:
            game.projectiles.remove(self)
        # Detects whether the projectile hit an enemy ship
        hitObject = pygame.sprite.spritecollideany(self, game.enemies)
        if hitObject:
            # Only considers the collision if the projectile was fired by the player. Therefore, enemy projectiles
            # will go through other enemies.
            if self.friendly:
                # Removes the hit enemy from the game and the enemies group
                hitObject.kill()
                # Removes the projectile from the game's projectile group
                game.projectiles.remove(self)
                # Adds 1 to the player's score
                game.score += 1
                # Plays the collision sound effect
                self.hit_sound.play()
        # Detects if a projectile hit the player ship
        if pygame.sprite.collide_rect(self, game.ship):
            # Only considers the collision if the projectile was fired from an enemy.
            if not self.friendly:
                # Removes the projectile from the game's projectile group
                game.projectiles.remove(self)
                # Triggers a new life event, which is handled in the game class.
                pygame.event.post(game.new_life_event)
                # Plays the collision sound effect
                self.hit_sound.play()
        # If the projectile is not at the edge of the screen or hit an opposing ship, it continues moving in the
        # direction it was heading
        self.rect.x += self.vector[0]
        self.rect.y += self.vector[1]


# The class for the stars moving in the background of the game
class Star(pygame.sprite.Sprite):
    def __init__(self):
        # Constructor for the Star class
        pygame.sprite.Sprite.__init__(self)
        # Randomly sets the diameter of the star between 3 and 5
        self.size = random.randint(3, 5)
        self.image = pygame.Surface((self.size, self.size))
        # Generates a color based on 3 random numbers between 0 and 80, subtly changing the color of the star
        self.color = (255-random.randint(0, 80), 255-random.randint(0, 80), 255-random.randint(0, 80))
        self.image.fill(self.color)
        # This variable denotes if the star is currecntly being shown on screen, and is used to make the star twinkle
        self.image_filled = True
        self.rect = self.image.get_rect()
        # Generates a location for the star to start at. Always at the top of the screen but at a randomly location
        # on the x axis
        self.rect.x = random.randint(0, 596)
        self.rect.y = 0

    # Updates the location and state of the star
    # @param stars - The list of all stars in the game
    def update(self, stars):
        # Determines if the star will toggle between being visible and invisible based on a random number from 0 to 120
        # each clock cycle. So each star will twinkle on average every 2 seconds
        if random.randint(0, 120) == 1:
            if self.image_filled:
                # If the star is currently visible, its color is set to black and the image_filled flag is toggled
                self.image.fill((0, 0, 0))
                self.image_filled = False
            else:
                # If the star is currently not visible, its color is set to its original color
                # and the image_filled flag is toggled
                self.image.fill(self.color)
                self.image_filled = True
        # If the star moves off the bottom of the screen, it is removed from the game's stars group
        if self.rect.y > 700:
            stars.remove(self)
        # If the star is still on the screen, it moves at an interval determined by its size on the screen.
        # This gives the appearance of stars closer to the scene being bigger and moving faster, giving
        # a sense of depth
        else:
            self.rect.y += int(self.size/2)


# This is the class for the game over screen
class EndScreen(pygame.sprite.Sprite):
    # Constructor for the EndScreen class
    # @param win - a bool denoting whether the game was won or lost. True = won, False = lost
    def __init__(self, win, score):
        pygame.sprite.Sprite.__init__(self)
        # Takes up the same space that the game screen does
        self.image = pygame.Surface((600, 700))
        # Sets the background to black
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        # sets font style and size of the end screen text
        self.font = pygame.font.Font('freesansbold.ttf', 40)
        # Displays an appropriate message based on whether the player won or lost, and displays the ending score
        if win:
            self.render('You Win! Final Score: ' + str(score))
        else:
            self.render('Game Over! Final Score: ' + str(score))

    # Updates the text of the screen
    # @param text - The appropriate text to be written
    def render(self, text):
        # Sets the text to be white
        self.text = self.font.render(text, True, (255, 255, 255))
        # Writes the text to the rectangle
        self.image.blit(self.text, self.rect)

    # Draws the text to the end screen
    # @param screen - The end screen we are writing the text to
    def draw(self, screen):
        # Draws the text to the middle of the screen
        screen.blit(self.text, (30, 300))


# Class that handles all the objects and player inputs
class Game:
    # Constructor for the game class
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(50)
        # Loads the background song "Space Oddity 8 bit"
        pygame.mixer.music.load('assets/Space_Oddity.mp3')
        pygame.mixer.music.set_volume(1)
        # Plays the song indefinitely
        pygame.mixer.music.play(-1)
        # Starts the game clock
        self.clock = pygame.time.Clock()
        # Sets the game screen to 600 by 700 pixels
        self.screen = pygame.display.set_mode((600, 700))
        # Sets the end screen to 600 by 700 pixels
        self.end_screen = pygame.display.set_mode((600, 700))
        # Defines a new life event
        self.new_life_event = pygame.event.Event(pygame.USEREVENT + 1)
        # Intitializes the player ship
        self.ship = Ship()
        # Creates a group for all the enemy ships
        self.enemies = pygame.sprite.Group()
        # Creates a group for all projectiles
        self.projectiles = pygame.sprite.Group()
        # Creates a group for all the background stars
        self.stars = pygame.sprite.Group()
        # Initializes the overlay
        self.overlay = Overlay()
        # Sets the game screen and end screen to black
        self.screen.fill((0, 0, 0))
        self.end_screen.fill((0, 0, 0))
        self.ready = True
        self.score = 0
        self.lives = 3
        # Creates a grid of 60 enemies
        for i in range(0, 10):
            for j in range(0, 6):
                # The ship's color is determined by its coordinate values, establishing the pretty array of colors
                # seen in the game
                enemy = Enemy([int(i*25), int(j*40), int(120+i*j/5)], [int(40+i*50), int(40+j*50)])
                # Adds each enemy to the enemies group
                self.enemies.add(enemy)

    # Runs the game
    def run(self):
        self.done = False
        # This bool is used to determine if the user is holding the space bar. This is used to ensure that
        # only one friendly projectile is created every time the spacebar is pressed
        self.space_held = False
        # While loop to run the game
        while not self.done:
            # Clears the screen of all objects so they can be accurately redrawn
            self.screen.fill((0, 0, 0))
            # Handles all events such as player inputs and object collisions
            for event in pygame.event.get():
                # Handles if the player was hit by an enemy projectile
                if event.type == self.new_life_event.type:
                    # Takes a life from the player
                    self.lives -= 1
                    # The player loses the game if they run out of lives
                    if self.lives == 0:
                        # Initializes the end screen with the player having lost the game and passing in the final score
                        end = EndScreen(False, self.score)
                        # Draws the end screen
                        end.draw(self.end_screen)
                        # Puts the end screen on the display
                        pygame.display.flip()
                        # Leaves the end screen up for ten seconds before closing the program
                        time.sleep(10)
                        pygame.quit()
                        sys.exit(0)
                # Exits the program if the user hits the X button
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                # Handles all player inputs
                if event.type == pygame.KEYDOWN:
                    # Moves the ship left if the player presses the left arrow key
                    if event.key == pygame.K_LEFT:
                        # Moves the ship left 5 pixels
                        self.ship.rect.x -= 5
                        # If the ship is on the left edge of the screen, it will not move
                        if self.ship.rect.x < 0:
                            self.ship.rect.x = 0
                    # Moves the ship right if the player presses the right arrow key
                    if event.key == pygame.K_RIGHT:
                        # Moves the ship right 5 pixels
                        self.ship.rect.x += 5
                        # If the ship is on the right edge of the screen, it will not move
                        if self.ship.rect.x > 580:
                            self.ship.rect.x = 580
                    # Handles the playe pressing the space bar
                    if event.key == pygame.K_SPACE:
                        # Int variable to hold the number of friendly shots currently on the screen
                        shotcount = 0
                        # Runs through all the projectiles in the game
                        for p in self.projectiles:
                            # Increments shotcount if the projectile was fired by the player
                            if p.friendly:
                                shotcount += 1
                        # Fires a friendly projectile, but only if space was not held and if there are 6 or less
                        # friendly projectiles in play. I decided to limit the number of projectiles the player
                        # can have on the screen because otherwise the player can repeatedly press the space bar and
                        # fire a ridiculous number of shots, making the game extremely easy
                        if not self.space_held and shotcount <= 6:
                            # Creates a friendly projectile from the middle of the ship moving directly upward
                            projectile = Projectile([self.ship.rect.x+10, self.ship.rect.y], [0, -4], True)
                            # Adds the projectile to the projectiles group
                            self.projectiles.add(projectile)
                            # Toggles the space_held bool
                            self.space_held = True
                # Detects when a key is released
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        # When the player releases the space bar, the space_held bool is toggle, signifying that
                        # the player may fire another projectile
                        self.space_held = False
            # Determines if a star will be spawned on this clock tick, based on a random int from 0 to 20
            if random.randint(0, 20) == 1:
                # Creates a star and adds it to the stars group
                star = Star()
                self.stars.add(star)
            # Determines if each enemy will fire a projectile
            for e in self.enemies:
                e.shoot(game)
            # Updates the states and locations of all projectiles
            for p in self.projectiles:
                p.update(game)
            # Determines whether or not the enemy ships will need to change direction
            for e in self.enemies:
                modifier = Enemy.changeDirection(e, self.enemies)
                break
            # Changes each enemy's direction if necessary, leaves them unchanged otherwise
            for e in self.enemies:
                e.direction *= modifier
            # Update all object groups and redraws them in the correct position
            self.enemies.update(self.screen)
            self.overlay.update(self.score, self.lives)
            self.stars.update(self.stars)
            self.stars.draw(self.screen)
            self.ship.draw(self.screen)
            self.enemies.draw(self.screen)
            self.projectiles.draw(self.screen)
            self.overlay.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)
            # Detects if all the enemies have been eliminated
            if len(self.enemies) == 0:
                self.end_screen.fill((0, 0, 0))
                # Initializes the end screen for a won game and passes the end score
                end = EndScreen(True, self.score)
                # Displays the end screen
                end.draw(self.end_screen)
                pygame.display.flip()
                # Waits ten seconds before closing the program
                time.sleep(10)
                pygame.quit()
                sys.exit(0)


if __name__ == "__main__":
    game = Game()
    game.run()
