import basebehavior.behaviorimplementation

import time

class AlignDefence_x(basebehavior.behaviorimplementation.BehaviorImplementation):

    '''This behavior will make the Nao stand between the goal and the ball.'''

    #this implementation should not define an __init__ !!!


    def implementation_init(self):
        self.idling = False

        self.__start_time = time.time()

        self.__nao = self.body.nao(0)
        self.__nao.say("Lets try to align between the ball and the goal!")

    def implementation_update(self):
        if self.idling:
            return
            
        (time, pos) = self.m.get_last_observation('position')
        print "Post align position: %d " % (pos)

        self.m.add_item('ball_aligned',time.time(),{})

        #TODO: Als afstand klein is (size < threshold), aligndefence stoppen met self.m.add_item('ball_aligned',time.time(),{})
		#TODO: Else: (size >= threshold)
                #Move left iff ball is left   && Update memory position
                #Move right iff ball is right && Update memory position
		
