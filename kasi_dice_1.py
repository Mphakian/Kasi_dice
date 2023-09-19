"""
     ___________________________________________________________________________________________________________
    |                                                   #RULES                                                  |
    |                                                                                                           |
    |   This is a dice game between Thabang and Thabo. They must battle it out in a dice rolling game, a player |
    |   who gets to R100 000 first wins the game. This version of dice game is a kasi(township) version which   |
    |   is played in almost every corner of every kasi of each province. Its played hustlers for various        |
    |   reasons, the story of the hustlers in our game will be introduced in the game. The game follows the     |
    |   following rules:                                                                                        |
    |       1.  It is a two player game                                                                         |
    |       2.  There is a roller and an observer                                                               |
    |       3.  The roller rolls the dice while the observer observes until the roller to loses the round       |
    |       4.  When a roller loses a round they become the observer and vice versa                             |
    |       5.  If on the first roll the roller rolls 2, 3 or 12, they lose the round                           |
    |       6.  If on the first roll the roller rolls 7 or 11, they win the round                               |
    |       7.  If conditions 4 and 4 is not met, the rolled number becomes the target number                   |
    |           N.B: The target number is the number the roller needs to roll in order to win the round         |
    |       8.  If on a second roll of the round going forward the rolled number is equal to the target number, |
    |           the roller wins the round                                                                       |
    |       9.  If on a second roll of the round going forward the rolled number is equal to seven, the roller  |
    |           loses the round                                                                                 |
    |       10. The first player to run out of credits loses the game                                           |
    |                                                                                                           |
    |       N.B: A round is from the first roll to when the roller loses in terms of conditions 5, 6, and 9     |
    |___________________________________________________________________________________________________________|
"""
#================================================================================================================
import sys
import pygame
import network_kasi_dice
import random
import time
#================================================================================================================

class Settings:
    """This class saves dimensions, titles and pictures"""
#================================================================================================================
    #Dimensions
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    DICE_SCLAE = 100
    CHARACTER_SCALE = (100,100)
 #================================================================================================================  
 #================================================================================================================
    #Game title
    TITLE = "Kasi Dice"
#================================================================================================================
#================================================================================================================
    #Images
    #Story images
    thabang_story = [pygame.image.load(f'thabang/Thabang_{i}.png') for i in range(1,10)]
    thabo_story = [pygame.image.load(f'thabo/Thabo_{i}.png') for i in range(10,17)]

    #Dice pictures
    dice_images = [pygame.image.load(f'dice/{i}.png') for i in range(1,7)]

    #Background images
    background = pygame.image.load(f'background/3.png')
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    #Game playing table
    table = pygame.image.load(f'table/table_r.png')
    table = pygame.transform.scale(table, (350, 200))

    #Welcome screen icon
    icon_image = pygame.image.load("animation/0.jpg")

    #Load characters' images
    char_1 = pygame.image.load("characters/1.png")
    char_2 = pygame.image.load("characters/2.png")
    char_1_trans = pygame.transform.scale(char_1, CHARACTER_SCALE)
    char_2_trans = pygame.transform.scale(char_2, CHARACTER_SCALE)

    #Winner background image
    background_winner_image = pygame.image.load("winner/winner.png")
#================================================================================================================

class Game:
    """Overall class to manage game assets and behaviour"""

    def __init__(self):
        """Initialize the game and create game resources"""
        pygame.init() 

        #Settings and screen
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.SCREEN_WIDTH, 
                                               self.settings.SCREEN_HEIGHT))       

        #Connections
        self.network = network_kasi_dice.Client()
        self.network.connect()

        #Game start
        self.new_game()
        self.welcome, self.story, self.betting, self.animate, self.gameplay, self.winner = True, False, False, False, False, False
        self.my_turn = self.turn()
        #rolling variables
        self.target = 0
        self.current_bet = 0
        self.pot = self.current_bet * 2
        self.dice_1 = 1
        self.dice_2 = 2
        #Story images
        self.story_increment = 0
  
    def new_game(self):
        '''This function starts the initial state of the game everytime a new game is started'''
     
         #A request is sent to the server to ask for player ID, name
        response = self.network.send("who_am_i")
        self.my_id = int(response[0])
        self.my_name = response[1:]    
        
        print(f'Your are playing as {self.my_name}') 

        #Keeps track of player balances        
        self.balances = [
            50_000, #Thabang's balance 
            50_000  #Thabo's balance
            ]
          
        #Create a game window and set its title
        self.screen = pygame.display.set_mode((self.settings.SCREEN_WIDTH, 
                                               self.settings.SCREEN_HEIGHT))

        #keeps track of game statistics. 
        self.stats_list = [
            1, #Index_0 = Dice 1
            2, #Index_1 = Dice 2
            0, #Index_2 = Rolled number (roll = dice 1 + dice 2)
            0, #Index_3 = The winning target
            0  #Index_4 = Bet amount 
            ]

    def opponent_name(self):
        """Returns the opponents' name"""

        if self.my_name == 'thabang': 
            return 'thabo'
        elif self.my_name == 'thabo':
            return 'thabang'
    
    def balance_update(self):
        """Updates balances by sending a request to the server"""
        balance_update = self.balances
        self.network.send(f'b+{balance_update}')

    def turn(self):
        """Sends a request to the server to determine if its Thabang's turn to play"""
        #The request is sent and the reponse is stored in variable 'turn'
        turn = self.network.send("turn")

        if turn == 'True' and self.my_name == 'thabang':
            return True
        elif turn == 'False' and self.my_name == 'thabo':
            return True
        else:
            return False

    def show_start_screen(self):
        """Displays the start screen when a new game starts"""
        if self.welcome:
            #Background image
            self.render_picture(self.settings.background, (0, 0), (self.settings.SCREEN_WIDTH,
                                                                   self.settings.SCREEN_HEIGHT))
            #Welcome screen icon
            self.render_picture(self.settings.icon_image, (250, 180), (250,250))
            #Title
            self.draw_text_adrip(self.settings.TITLE, 400, 120, 150, 1)
            #Proceed text
            self.draw_text_adrip(text='Press Enter to proceed....', x=400, y=500, num=3)

    def story_screen(self):
        """Introduces the characters of the game and shows a slide show"""
        if self.story:    
            self.screen.fill('black')
            #Next and Prev text
            self.draw_text_adrip('<<<< arrow| Previous | Next |arrow >>>>>>>', 400, 560, 30, 2)
            #Slide show
            if self.story_increment <= 8:
                self.render_picture(self.settings.thabang_story[self.story_increment], (50, 10), (700,525))
            elif self.story_increment > 8 and self.story_increment <= 15:
                self.render_picture(self.settings.thabo_story[self.story_increment-9], (50, 10), (700,525))
            else:
                self.story = False
                self.gameplay = True

    def betting_screen(self):
        """Displays the bet screen when the first roll is initiated"""    
        #Creates the bet window 
        window = pygame.display.set_mode((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))

        # Load font
        font = pygame.font.Font("font/Black Ravens.ttf", 48)
      
        # Create text 
        betting_text = font.render("Press 1 to bet 1k, 5 to bet 5k or 0 to bet 10k", True, (255, 255, 255))
        betting_rect = betting_text.get_rect(center=(self.settings.SCREEN_WIDTH/2, self.settings.SCREEN_HEIGHT/2 - 50))

        #The loop will run until a player makes a bet
        while True:
            window.fill('black')
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    #Small bet
                    if event.key == pygame.K_1:
                        if (self.balances[0]-1000) >= 0 and (self.balances[0]-1000) >= 0: 
                            self.current_bet = 1_000
                            self.balances[0] -= 1_000
                            self.balances[1] -= 1_000
                            self.stats_list[4] = 1_000
                            return
                        else:
                            print('You can\'t place that bet...try another bet size')
                        
                    #Medium bet
                    elif event.key == pygame.K_5:
                        if (self.balances[0]-5000) >= 0 and (self.balances[0]-5000) >= 0:
                            self.current_bet = 5_000
                            self.balances[0] -= 5_000
                            self.balances[1] -= 5_000
                            self.stats_list[4] = 5_000
                            return
                        else:
                            print('You can\'t place that bet...try another bet size')                            
                    #Large bet
                    elif event.key == pygame.K_0:
                        if (self.balances[0]-100000) >= 0 and (self.balances[0]-100000) >= 0:
                            self.current_bet = 10_000
                            self.balances[0] -= 10_000
                            self.balances[1] -= 10_000
                            self.stats_list[4] = 10_000
                            return
                        else:
                            print('You can\'t place that bet...try another bet size')
                            
                    else: print('Choose valid bet: ')
           
            window.blit(betting_text, betting_rect)
            pygame.display.update()

    def play_screen(self):
        """Displays the gameplay screen"""
        
        if self.gameplay:
            #Background
            self.render_picture(self.settings.background, (0, 0), (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))
            
            #Table
            self.render_picture(self.settings.table, (self.settings.SCREEN_WIDTH/2- self.settings.SCREEN_WIDTH/3.3, 
                                                      self.settings.SCREEN_HEIGHT/2- self.settings.SCREEN_HEIGHT/2.791), 
                                (self.settings.SCREEN_WIDTH/1.6, self.settings.SCREEN_HEIGHT/1.818))

            #Dice 1
            self.render_picture(
                self.settings.dice_images[self.stats_list[0]-1],
                (325, 220),
                (75,75)
            )
            #Dice 2
            self.render_picture(
                self.settings.dice_images[self.stats_list[1]-1],
                (425, 220),
                (75,75)
            )

            #Press space_bar to roll, text
            self.draw_text_adrip(
                text=f"Press space_bar to roll",
                x=410, y=375, size=25, num=1
            )

            #Character 1 = Thabang
            #Picture
            self.render_picture(
                self.settings.char_1_trans,
                (50, 430)
            )
            
            #Character 2 = Thabo
            #Picture
            self.render_picture(
                self.settings.char_2_trans,
                (630, 430)
            )
            
            #Names and balance texts
            if self.my_name == 'thabang':
                self.draw_text_adrip(
                    text=f"Thabang : ${self.balances[0]}",
                    x=120, y=550, size=28, num=2
                )
                self.draw_text_adrip(
                    text=f"Thabo : ${self.balances[1]}",
                    x=680, y=550, size=28, num=2 
                )              
            
            #Name and balance text

            elif self.my_name == 'thabo':
                self.draw_text_adrip(
                    text=f"Thabang : ${self.balances[0]}",
                    x=120, y=550, size=28, num=2
                )
                self.draw_text_adrip(
                    text=f"Thabo : ${self.balances[1]}",
                    x=680, y=550, size=28, num=2
                )

            #Game stats
            #Pot
            self.draw_text_adrip(
                text=f"Pot size: $ {self.stats_list[4]*2}",
                x=400, y=450, size=35, num=2
            )
            #Target number
            self.draw_text_adrip(
                text=f"Target= {self.stats_list[3]}",
                x=400, y=485, size=35, num=2
            )
            #Current roll
            self.draw_text_adrip(
                text=f"Current roll: {self.stats_list[2]}",
                x=400, y=520, size=35, num=2
            )           

        if self.my_turn and self.my_name == 'thabang':
            self.draw_text('++', 100, 415)
        elif self.my_turn and self.my_name == 'thabo':
            self.draw_text('++', 680, 415)
            
        self.draw_text_adrip(text='when "++" appears on top of your charatcer, it is your turn.....', x=400, y=40, size=30, num=2)

    def roll_dice(self):
        """This function is responsible for the following:
                1.  simulate the rolling of dice by generating two random numbers and assigning them to respective variables
                2.  Update the stats list
                3.  Check winning and losing conditions
                4.  Send balance update requests to the server
                5.  reset target, roll and bet on the stats list when the round is over
                6.  Send requests to change player turns on the server
                7.  Update game state on the server after every roll
                """

        #Generate 2 random numbers that represent the rolling of dice
        self.dice_1 = random.randint(1, 6)
        self.dice_2 = random.randint(1, 6)
        #Update the stats list with the dice numbers
        self.stats_list[0] = self.dice_1
        self.stats_list[1] = self.dice_2
        #Set the roll number by adding the dice numbers and update the stats list
        self.roll = self.dice_1 + self.dice_2
        self.stats_list[2] = self.roll

        #Check wiining or losing conditions on the first roll
        if self.target == 0:
            if self.roll in [2, 3, 12]:      #If first roll is 2, 3, or 12 the roller loses, the opponent wins
                #Update balance accordingly
                if self.my_name == 'thabang':
                    self.balances[1] += self.current_bet * 2
                    self.winner_activater()
                elif self.my_name == 'thabo':
                    self.balances[0] += self.current_bet * 2
                    self.winner_activater()

                #Reset the target number and bet
                self.target = 0
                self.current_bet =0
                #change the turn of the player to false
                self.network.send('change')
                

            elif self.roll in [7, 11]:  #If first roll is 7 or 11 the roller wins, the opponent loses
                #Update balance accordingly
                if self.my_name == 'thabang':
                    self.balances[0] += self.current_bet * 2
                    self.winner_activater()
                elif self.my_name == 'thabo':
                    self.balances[1] += self.current_bet * 2
                    self.winner_activater()

                #Reset the target number and bet
                self.target = 0
                self.current_bet =0
                

            else:
                #Set the target number
                self.target = self.roll
                #Update the target stat on the stat list
                self.stats_list[3] = self.target
        else:
            #If subsequent roll = target then the player win, the opponent loses
            if self.roll == self.target:
                #Update balance accordingly
                if self.my_name == 'thabang':
                    self.balances[0] += self.current_bet * 2
                    self.winner_activater()
                elif self.my_name == 'thabo':
                    self.balances[1] += self.current_bet * 2
                    self.winner_activater()

                #Reset the target number and bet
                self.target = 0
                self.current_bet =0
               
            
            #If subsequent roll = 7 then the player loses, the opponent wins   
            elif self.roll == 7:
                #Update balance accordingly
                if self.my_name == 'thabang':
                    self.balances[1] += self.current_bet * 2
                elif self.my_name == 'thabo':
                    self.balances[0] += self.current_bet * 2

                #Reset the target number and bet
                self.target = 0
                self.current_bet =0
                #Change the turn of the  player to false
                self.network.send('change')
                self.winner_activater()

        #Update stats on the server 
        self.update_state()
        
        #Update turns
        self.my_turn = self.turn()

    def winner_screen(self):
        """This function is responsible for diplaying a winner screen after the game"""
        if self.winner:
            self.render_picture(
                self.settings.background_winner_image,
                (0, 0),
                (self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT)
            )

            if self.balances[0] == 0 and self.my_name == 'thabang':

                self.draw_text(
                    f"{self.my_name.title()} won!!!!!!",
                    400, 100
                )

            elif self.balances[1] == 0 and self.my_name == 'thabo':
                self.draw_text(
                    f"{self.opponent_name().title()} won!!!!!!",
                    400, 100
                )           
    
    def events(self):
        """This function is responsible for managing window close actions and key presses"""
        #Request game state when it is not players turn
        if not self.my_turn:
            self.get_state()
            
        #Manage pygame events
        for event in pygame.event.get():
            #Quit when window is closed
            if event.type == pygame.QUIT:
                self.quit_game()
            #Manages keydown actions
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE and self.gameplay and self.my_turn:
                    #The function uses the bet amount to determine if its the first roll or not
                    #If it is the first roll the bet screen is displayed else roll
                    if self.current_bet == 0 :
                        self.betting_screen()                           
                        self.roll_dice()
                    else:
                        self.roll_dice()

                #Switching between different windows
                elif event.key == pygame.K_RETURN and self.welcome:
                    self.welcome = False
                    self.story = True

                elif event.key == pygame.K_RETURN and self.story:
                    self.story = False
                    self.gameplay = True
                
                elif event.key == pygame.K_RIGHT and self.story:
                    self.story_increment += 1
                    
                elif event.key == pygame.K_LEFT and self.story:
                    self.story_increment -= 1

                elif event.key == pygame.K_ESCAPE and self.winner:
                    self.quit_game()
                    sys.exit()
                elif self.gameplay and not self.my_turn:
                    print('Wait for your turn')

    def update_state(self):
        """This function is responsible for sending an updated game state to the server"""   
        stats = self.stats_list
        self.network.send(f's{stats}')
        
        balance = self.balances
        self.network.send(f'b+{balance}')

    def get_state(self):
        """This function is responsible for requesting the current game state from the server and assign it to the stats list"""
        state_update = self.network.send(f'g')
        get_balance = self.network.send(f'b-')

        try:
            self.stats_list = state_update.split(',')
            self.balances = get_balance.split(',')
            for i in range(len(self.stats_list)):
                self.stats_list[i] = int(self.stats_list[i].strip())
                
            for x in range(len(self.balances)):
                self.balances[x] = int(self.balances[x].strip())
            self.my_turn = self.turn()
          
        except Exception as e:
            print(f'get_state ERROR - {e}')
            exit()

    def draw_text(self, text, x, y, size=40):
        """This function is responsible for drawing text on the screen"""
        text_font = pygame.font.SysFont('Arial', size)
        img = text_font.render(text, True, 'white')
        self.screen.blit(img, img.get_rect(center=(x, y)))
        
    def draw_text_adrip(self, text, x, y, size=40, num=None):
        
        if num == 1:
            font = pygame.font.Font("font/Casino3DFilledMarquee-Italic.ttf", size)
            text = font.render(text, True, 'black')
        elif num == 2:
            font = pygame.font.Font("font/Black Ravens.ttf", size)
            text = font.render(text, True, 'white') 
        elif num == 3:
            font = pygame.font.Font("font/adrip1.ttf", size)
            text = font.render(text, True, 'white')             
                        
        self.screen.blit(text, text.get_rect(center=(x,y)))

    def render_picture(self, picture, coordinates, size=None):
        """This function is responsible for displaying pictures on the screen"""
        if size:
            image = pygame.transform.scale(picture, size)
            self.screen.blit(image, coordinates)
        else:
            self.screen.blit(picture, coordinates)
  
    def draw(self):
        """This funtion is responsible for activating different windows"""
        if self.running:
            if self.welcome:
                self.show_start_screen()
            elif self.story:
                self.story_screen()
            elif self.betting:
                self.betting_screen()
            elif self.animate:
                self.animate_images()
                self.animate = False
            elif self.gameplay:
                self.play_screen()
            elif self.winner:
                self.winner_screen()

            pygame.display.flip()
    
    def quit_game(self):
        self.running = False
        pygame.quit()
        sys.exit()

    def winner_activater(self):
        if self.balances[0] == 0 or self.balances[1] == 0:
            print(f'{self.balances[0]} and {self.balances[0]}')
            print(f'target : {self.stats_list[3]} | dice_1 : {self.stats_list[0]} | dice_2 : {self.stats_list[1]}')
            self.gameplay = False
            self.winner = True

    def run(self):
        """This function is responsible for running the major function s of the game """
        self.running = True
        while self.running:
            self.events()
            self.draw()


if __name__ == '__main__':
    """Creates an instance of the gamne and activates the run function """
    g = Game()
    g.run()
