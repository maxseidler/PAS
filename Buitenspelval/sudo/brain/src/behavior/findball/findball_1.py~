import basebehavior.behaviorimplementation

import sys
import time
import random
from naoqi import ALProxy

class FindBall_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    '''This behavior will move the Nao around until the ball is seen in the middle of the FoV.'''

    #this implementation should not define an __init__ !!!
    

    def implementation_init(self):
        self.__nao = self.body.nao(0)
        self.__nao.say("Lets find the %s ball!" % self.ball_color)
        self.__start_time = time.time()

        #Make sure the robot is standing and looks horizontal:
        self.__nao.start_behavior("standup")
        self.__nao.look_horizontal()

        #Possible states (WALK, TURN, Look_Left, Look_Right ):
        self.__state = "Look_For_Ball"
        self.__last_recogtime = time.time()


        self.motionProxy = ALProxy("ALMotion", "129.125.178.227", 9559)
        self.head = 0
        
    def implementation_update(self):
        # Turn around in a certain direction unless you see the ball.
        # In that case, turn towards it until you have it fairly central in the Field of Vision.        
        #Needs testing


        #Add centering of ball in camera (ie. x=60)
        #This way we rotate the nao towards the ball correctly
        
        if (time.time() - self.__start_time) > 10:

            if self.__state == "Look_For_Ball":
                self.__state = "Look_Right"
                
            self.head = self.motionProxy.getAngles("HeadYaw", 1)
            if self.__state == "Look_Right":
                names  = ["HeadYaw", "HeadPitch"]
                yaw = -1.1
                angles  = [yaw, 0.0]
                self.motionProxy.setAngles(names, angles, 0.05)
                if self.head[0] < -0.7:
                    self.__state = "Look_Left"                
                    
                
            if self.__state == "Look_Left":
                names  = ["HeadYaw", "HeadPitch"]
                yaw = 1.1
                angles  = [yaw, 0.0]
                self.motionProxy.setAngles(names, angles, 0.05)
                if self.head[0] > 0.7: 
                    self.__state = "Look_Forward"  
                  
            if(self.__state == "Look_Forward"):
                print "IK KIJK NAAR VOREN"
                names  = ["HeadYaw", "HeadPitch"]
                angles  = [0.0, 0.0]
                self.motionProxy.setAngles(names, angles, 0.8)
                self.__nao.look_horizontal()
                if(self.head[0] < 0.01):
                    self.__state = "TURN"
                    self.__nao.say("found no ball")

            elif self.__state == "TURN":
                if not self.__nao.isWalking():
                    self.__state = "WALK"
                    self.__nao.walkNav(random.random() * 10, 0, 0)
            elif self.__state == "WALK":
                if not self.__nao.isWalking():
                    self.__state = "TURN"
                    self.__nao.walkNav(0, 0, random.random() * 2 - 1, 0.1)
        
        #Try to see if there is a ball in sight:
        if (self.m.n_occurs(self.ball_color) > 0):
            (recogtime, obs) = self.m.get_last_observation(self.ball_color)
            if not obs == None and recogtime > self.__last_recogtime:
                self.head = self.motionProxy.getAngles("HeadYaw", 1)
                
                print self.head[0]
                if(obs['surface'] > 70 and ((self.__state == "Look_Right") or (self.__state == "Look_Left") or (self.__state == "Look_Forward"))):
                    # Draai naar de nao naar rechts
                    self.__nao.say("I see the ball!")
                    self.__nao.walk( 0, 0, self.head[0])
                    names  = ["HeadYaw", "HeadPitch"]
                    angles  = [0.0, 0.0]
                    self.motionProxy.setAngles(names, angles, 0.8)
                    self.__state = "Walk"
                    print "IK ZIE DE BAL en hoofd is gedraaid"
                    self.m.add_item('ball_found',time.time(),{})

                    
                print self.ball_color + ": x=%d, y=%d, size=%f" % (obs['x'], obs['y'], obs['surface'])
                self.__last_recogtime = recogtime
                '''
                #Ball is found if the detected ball is big enough (thus filtering noise):
                if (obs['surface'] > 70): #and obs['x'] > 45 and obs['x'] < 65):
                    self.__nao.say("I see the ball!")
                    # Once the ball is properly found, use: self.m.add_item('ball_found',time.time(),{}) to finish this behavior.
                    '''
