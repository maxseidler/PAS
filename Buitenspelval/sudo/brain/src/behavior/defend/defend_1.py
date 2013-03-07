import basebehavior.behaviorimplementation


class Defend_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    '''this behavior makes the Nao sit down, untill the ball is nog longer seen than 10 seconds'''

    #this implementation should not define an __init__ !!!


    def implementation_init(self):
        self.__nao.start_behavior("sitDown")
        self.__last_ball_recogtime = time.time()

    def implementation_update(self):
        
        #Try to see if there is a ball in sight:
        if (self.m.n_occurs(self.ball_color) > 0):
            (recogtime, obs) = self.m.get_last_observation(self.ball_color)
            if (recogtime - self.__last_ball_recogtime) > 10:
                self.m.add_item('goal_defended',time.time(),{})
                self.m.add_item('subsume_stopped',time.time(),{'reason':'Hopefully I saved us.'})
                self.idling = True
            else:                
                self.__last_recogtime = recogtime
