import time
from machine import Pin
from Displays import LCDDisplay
from Buzzer import PassiveBuzzer, tones
from Button import Button
from Log import *

# --- Game Configuration ---
GROUND_LEVEL = 1
CHARACTER_START_X = 2
OBSTACLE_START_X = 15
SPEED = 0.5  

# --- Hardware Setup ---
buzzer = PassiveBuzzer(16)
display = LCDDisplay(sda=0, scl=1, i2cid=0)
button = Button(10, "Action Button")

# --- Sprites ---
character_running = chr(0) 
character_jumping = chr(1) 
character_ducking = chr(2) 
tree_obstacle = chr(3)     
bird_obstacle = chr(4)     

class DinoGame:
    """ Dino Game with score display only on game over """

    def __init__(self):
        # Add custom characters to the display (you'll need to define these)
        display.addShape(0, [0x04, 0x0E, 0x1F, 0x1B, 0x1F, 0x0E, 0x04, 0x00]) # Running
        display.addShape(1, [0x00, 0x04, 0x0A, 0x11, 0x1F, 0x1F, 0x0E, 0x04]) # Jumping
        display.addShape(2, [0x00, 0x04, 0x0E, 0x1F, 0x1F, 0x0E, 0x04, 0x00]) # Ducking
        display.addShape(3, [0x10, 0x18, 0x1C, 0x1E, 0x1E, 0x1C, 0x18, 0x10]) # Tree
        display.addShape(4, [0x00, 0x06, 0x0F, 0x03, 0x0F, 0x06, 0x00, 0x00]) # Bird

        self.character_x = CHARACTER_START_X
        self.character_y = GROUND_LEVEL 
        self.obstacle_x = OBSTACLE_START_X
        self.obstacle_type = "TREE" 
        self.game_over = False
        self.score = 0

        button.setHandler(self)  
        self.game_loop()

    def buttonPressed(self, name):
        """ Handle button press """
        if not self.game_over:
            if self.obstacle_type == "TREE" and self.obstacle_x < self.character_x + 3:
                self.character_y = 0  # Jump over tree
            else:
                self.character_y = GROUND_LEVEL + 1  # Duck under bird

    def buttonReleased(self, name):
        """ Return to running position """
        if not self.game_over:
            self.character_y = GROUND_LEVEL

    def update_game(self):
        """ Update game logic """
        self.obstacle_x -= 1
        if self.obstacle_x < 0:
            self.obstacle_x = OBSTACLE_START_X
            self.score += 1
            self.obstacle_type = "BIRD" if self.obstacle_type == "TREE" else "TREE"

        if self.obstacle_x == self.character_x and self.character_y == (0 if self.obstacle_type == "BIRD" else GROUND_LEVEL):
            self.game_over = True

    def draw_game(self):
        """ Draw game elements """
        display.clear()
        display.showText(character_running if self.character_y == GROUND_LEVEL else character_jumping if self.character_y == 0 else character_ducking, row=self.character_y, col=self.character_x)
        display.showText(tree_obstacle if self.obstacle_type == "TREE" else bird_obstacle, row=0 if self.obstacle_type == "BIRD" else GROUND_LEVEL, col=self.obstacle_x)

    def draw_game_over(self):
        """ Display game over screen with score """
        display.clear()
        display.showText("GAME OVER", row=0, col=3)
        display.showText(f"Score: {self.score}", row=1, col=3)  # Display score here
        buzzer.beep(tones['C3'], 500)

    def game_loop(self):
        """ Main game loop """
        while True:
            if not self.game_over:
                self.update_game()
                self.draw_game()
                time.sleep(SPEED)
            else:
                self.draw_game_over()
                time.sleep(2) 
                self.game_over = False 
                self.score = 0
                self.obstacle_x = OBSTACLE_START_X
                self.character_y = GROUND_LEVEL

if __name__ == "__main__":
    DinoGame()