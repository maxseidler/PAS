import basebehavior.behaviorimplementation

import time

class AlignGoal_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    '''This behavior will circle around the ball until it and the target goal in in a line.'''

    #this implementation should not define an __init__ !!!


    def implementation_init(self):
        self.idling = False
        self.__start_time = time.time()
        self.__last_recogtime_ball = time.time()
        self.__last_recogtime_goal = time.time()
        self.__nao = self.body.nao(0)
        self.__nao.say("Lets try to align the ball with the goal!")
        self.ballIsFound = False
    def implementation_update(self):
        if self.idling:
            return
        

        if (self.m.n_occurs(self.ball_color) > 0):
            (recogtime_ball, obs_ball) = self.m.get_last_observation(self.ball_color)
            if not obs_ball == None and recogtime_ball > self.__last_recogtime_ball:
                self.__last_recogtime_ball = recogtime_ball
                if obs_ball['size'] > 0.0015:
                    self.ballIsFound = True

                    print 'ball found'
        if (self.ballIsFound):
            if obs_ball['y'] < 80:
                self.__nao.walkNav(0.10, 0, 0)
            elif obs_ball['y'] > 75:
                self.__nao.walkNav(-0.10, 0, 0)
            else:
                self.__nao.walk(0.06, 0.1, -0.8)
                
            if (self.m.n_occurs(self.target_goal) > 0):
                (recogtime_goal, obs_goal) = self.m.get_last_observation(self.target_goal)
                if not obs_goal == None and recogtime_goal > self.__last_recogtime_goal:
                    self.__last_recogtime_goal = recogtime_goal
                    
                    if obs_goal['size'] > 0.0015:  
                    
                        # obs contains an x, y and size (info from the blob detector)
                        if (obs_ball['x'] < obs_goal['x']+20 and obs_ball['x'] > obs_goal['x']-20):
                            # Ball is alligned with goal
                            #self.m.add_item('goal_aligned', time.time(),{})
                            print "Ball is aligned"
                            
                        elif (obs_ball['x'] > obs_goal['x'] + 20):

                            # Ball is not aligned and to the right of the goal
                            # move rightway around the ball
                            print "ball is right from goal"
                            self.__nao.walk(0.06, 0.1, -0.8)
                        elif (obs_ball['x'] < obs_goal['x'] - 20):
                            
                            # Ball is not aligned and te the left of the goal
                            # move leftway around the ball
                            print "ball is left from goal"
                            self.__nao.walk(0.06, 0.1, -0.8)
                    else:
                        
                            
                        self.__nao.look_horizontal()
                        self.__nao.looking_horizontal = False
                        print "ball is found, looking for goal"
		
		
		
        #TODO: Remove the following with the steps mentioned below (e.d. align the robot so that it can kick the ball in the direction of the goal):
        #It now simply assumes that it is already aligned:
        #self.m.add_item('goal_aligned',time.time(),{})
        
        # If the ball and the goal are both in sight, check if they are in line with each other.
        # If they are aligned, use self.m.add_item('goal_aligned',time.time(),{}) to finish this behavior.
        # Else, turn to align them.
        # If the ball is in sight but the goal is not, strafe/circle in a single direction, keeping the ball in sight.

        # TODO: Remove simple timeout with:
        # Check if you can see the ball. If you can't, go idle so the structure resets.
        if (time.time() - self.__start_time) > 5:
            self.m.add_item('subsume_stopped',time.time(),{'reason':'Ball no longer seen.'})
            self.idling = True
