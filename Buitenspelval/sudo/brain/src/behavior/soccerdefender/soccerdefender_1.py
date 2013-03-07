
import basebehavior.behaviorimplementation

import time


class SoccerDefender_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    '''this is the defending robot's behavior'''

    #this implementation should not define an __init__ !!!


    def implementation_init(self):
    
        try:
            self.own_goal # This should be specified in the config, but this is to catch it.
        except:
            print "You should specify your target goal as an argument in the config!"
            self.own_goal = "yellow"            
        try:
            self.ball_color
        except:
            print "You should specify the ball color as an argument in the config!"
            self.ball_color = "red"
    
        #Select Nao and make it stand up.
        self.__nao = self.body.nao(0)
        self.__nao.say("Lets defend the goal and enslave humanity!")
        self.__nao.start_behavior("standup")
        if (self.m.n_occurs('position') > 0):
            (time, pos) = self.m.get_last_observation('position')
            walkNav(0, -pos, 0)

        self.m.add_item = {'position',time.time(),{'Position':0}}

        self.aligndefence = self.ab.aligndefence({'ball_color':self.ball_color})
        self.defend = self.ab.defend({'ball_color':self.ball_color})
        self.stayandobserve = self.ab.stayandobserve({'ball_color':self.ball_color})

	    self.selected_behaviors = [ \
            ("stayandobserve", "True"), \
            ("aligndefence", "self.stayandobserve.is_finished()"), \
            ("defend", "self.aligndefence.is_finished()"), \
        ]

        self.restart_time = time.time()


    def implementation_update(self):

        if ((time.time()-self.restart_time)>5 and self.m.is_now('subsume_stopped', ['True'])):
            print "Lower level restarting."
            self.restart_time = time.time()
            self.aligndefence = self.ab.aligndefence({'ball_color':self.ball_color})
            self.defend = self.ab.defend({'ball_color':self.ball_color})
            self.stayandobserve = self.ab.stayandobserve({'ball_color':self.ball_color})
            return
