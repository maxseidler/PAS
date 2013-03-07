import basebehavior.behaviorimplementation

import time

class StayAndObserve_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    '''this is a behavior will move the Nao in front of the goal, untill the ball is seen'''

    def implementation_init(self):
        self.__nao = self.body.nao(0)
        self.__nao.say("Watch out for the %s ball!" % self.ball_color)
        self.__last_ball_recogtime = 0
        self.__last_walk_time = time.time()
        self.__position = 0

        self.__movement = 0.25
        
    def implementation_update(self):
        if self.idling:
            return

        #Walk to the left and right --> TESTEN
        if (not self.__nao.isWalking()) and (time.time() - self.__last.walk_time > 5):
            self.__nao.walkNav(0, self.__movement, 0)
            (time, pos) = self.m.get_last_observation("position")
            pos += self.__movement
            self.m.add_item('position',time.time(),{'position':pos})
            print "Current position: x = %d" % (pos)
            position += self.__movement
            self.__movement *= -1            
            self.__last.walk_time = time.time()
       
        #Try to see if there is a ball in sight: --> KOMT OVEREEN MET AANVALLER, ZOU MOETEN WERKEN
        if (self.m.n_occurs(self.ball_color) > 0):
            (recogtime, obs) = self.m.get_last_observation(self.ball_color)
            if not obs == None and recogtime > self.__last_ball_recogtime:
                print self.ball_color + ": x=%d, y=%d, surface=%f" % (obs['x'], obs['y'], obs['surface'])
                self.__last_recogtime = recogtime
                #Ball is found if the detected ball is big enough (thus filtering noise):
                if obs['surface'] > 25:
                    self.__nao.say("I see the ball!")
                    # Once the ball is properly found, use: self.m.add_item('ball_seen',time.time(),{}) to finish this behavior.
                    self.m.add_item('ball_seen',time.time(),{})
