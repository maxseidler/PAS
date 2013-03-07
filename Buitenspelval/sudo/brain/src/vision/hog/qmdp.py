from decider import Decider 
import logging
import util.nullhandler
import sys
import random
import numpy
import math
import configparse
import os

logging.getLogger('Borg.Brain.Vision.hog.Q-mdp').addHandler(util.nullhandler.NullHandler())

class Qmdp(Decider):
    def __init__(self, host, port, path, opath, discountfactor=0.99, method = "cv"):
        self.logger = logging.getLogger("Borg.Brain.Vision.hog.Q-mdp")
        super(Qmdp, self).__init__(host, port, path, opath, discountfactor=0.99, method = "cv")
        
        #Lambda Value
        self.__lambda = 1500
        self.__beliefs = numpy.zeros(len(self.kcenters))
        self.__actions = 4 #Number of possible actions
        self.__prevAction = 0
        self.__prevCenter = 0
        
        #debug variables
        self.maxObs = 0
    
    def __initBeliefs(self):
        self.__beliefs = numpy.ones(len(self.kcenters)) / (len(self.kcenters)*1.0)
        #for i in range(len(self.kcenters))
    
    def __normalizeBelief(self):
        self.__beliefs = self.__beliefs / self.__beliefs.sum()

        
    def __distance(self, center):
        curCenter = self.kcenters[center,:]
        distance = numpy.sqrt(numpy.sum(numpy.power(numpy.subtract(curCenter, self.currentFeature) , 2)))
        #self.logger.debug("Distance is " + str(distance))
        
        return distance
    def __allDistance(self, center):
        allDist = numpy.sqrt(numpy.sum(numpy.power(numpy.subtract(self.kcenters , self.currentFeature) , 2), axis = 1))
        #self.logger.debug("PROB: Average Distance to all centers is: " +  str(numpy.mean(allDist)))
        
        return allDist
    #Probablity of observation regarding a certain cluster center P(O|C_t) = exp((d(o,c) / lambda) / sum_t(d(o,c_t) / lambda))
    def __observeProbability(self, center):
        divTop = math.exp(self.__distance(center) / -self.__lambda)
        #divBottom = numpy.sum(numpy.exp(self.__allDistance(center) / -self.__lambda))
 
        res = divTop #/ divBottom
        
        #self.logger.debug("PROB: observation probability is: " + str(res)) 
        #self.logger.debug("DivBottom shape is: " +  str(divBottom.shape))
        #self.logger.debug("res shape is: " +  str(res.shape))
        
        return res
    
    #Calculates the belief of current center and updates it
    def __belief(self, center):
        #self.logger.debug("Current center cluster is: " +  str(center))
        
        if self.__beliefs.any():
            #P(c_t-1 , a, c_t)*b(c_t-1)
            beliefs = self.__beliefs
            #for i in range(6):
            #    beliefs = numpy.vstack(beliefs)
            mulRes = numpy.multiply(self.tp_matrix[:,center,self.__prevAction],beliefs)
            
            
            self.__beliefs[center] =  self.__observeProbability(center) * numpy.sum(mulRes) 
            
            
        else:
            self.logger.debug("BELIEF: Initializing belief states")
            for i in range(len(self.kcenters)):
                self.__beliefs = numpy.zeros(len(self.kcenters))
                self.__beliefs[i] = self.__observeProbability(center) 
                
        return self.__beliefs[center]
    
    #Selects an action using Modified Q-MDP method
    def select_action(self, temperature = False):
        #self.logger.debug("Q-MDP action selection.")
        self.logger.debug("Current Goal number." + str(self.current_location))
        
        #Qvalue of the action for all states will be calculated
        Qvalues = []
        maxObs = 0
        maxidx = 0
        totalBelief = 0 #debug variable
        for j in range(3):
            values = 0

            
            for i in range(len(self.kcenters)):
                curBelief = self.__belief(i)
                if maxObs < curBelief:
                    maxObs = curBelief
                    maxidx = i
                #values += curBelief * self.qvalues[i,j]
            self.__normalizeBelief();
            
            values = numpy.sum(numpy.multiply(self.qvalues[:,j],self.__beliefs))
            #values = values.sum()
            self.logger.debug("Sum of all beliefs: " + str(numpy.sum(self.__beliefs)))
            self.logger.debug("Highest belief value: " + str(self.__beliefs[maxidx]))
            self.logger.debug("QVALUE: Q-value of action " + str(j) + " is " + str(values))
            Qvalues.append(values)
        
        #The biggest Qvalue will be selected     
        firstvalue = -1
        for x in range(3):
            temp = Qvalues[x]
            if temp > firstvalue:
                firstvalue = temp
                firstaction = x   
        
        #E-greedy method. Small chance of choosing a random action instead of the best one
        randomness = random.random()
        
        if randomness < 0.1 or firstaction == 3:
            firstaction = random.randint(0,2)
        action = firstaction
        self.__prevAction = action
        #action = self.qvalues[self.current_location,:].argmax()
        if action >= 0:
            self.add_property('name', 'action')
        else:
            self.logger.error("Ambigous location")
            return
        if action == 0 or action == 4:  
            self.add_property('action', 'move')
        elif action == 1 or action == 5:
            self.add_property('action', 'left')
        elif action == 2 or action == 6:   
            self.add_property('action', 'right')
        elif action == 3:
            self.add_property('action', 'move')
            
        #Update Beliefs
        
        def __del__(self):
            self.stop() 
         
    
def usage():
    print "You should add the cbbonfiguration options on the command line.\n"
    print "Usage: ", sys.argv[0], " host=<controller_host> port=<controller_port> preview=<True>\n"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        exit()

    sec = "decider" #section in config_dict
    args = sys.argv[1:]
    config_dict = configparse.parse_args_to_param_dict(args, sec)

    controller_ip = config_dict.get_option(sec, "host")
    controller_port = config_dict.get_option(sec, "port")
    path = config_dict.get_option(sec, "path")
    opath = config_dict.get_option(sec, "opath")
    discountfactor = config_dict.get_option(sec, "discountf")
    
    if path == None:
        path = os.path.abspath(os.environ['BORG'] + '/Brain/data/hog_test/matrixtest/') + '/'

    if opath == None:
        opath = path
        
    if discountfactor == None:
        discountfactor = 0.98
        

    sect = config_dict.get_section(sec)
    print sect

    if not (controller_ip and controller_port):
        usage()
        exit()

    logging.getLogger('Borg.Brain').addHandler(util.loggingextra.ScreenOutput())
    logging.getLogger('Borg.Brain').setLevel(logging.DEBUG)

    decider = Qmdp(controller_ip, controller_port, path, opath, discountfactor)
    decider.connect()
    decider.set_socket_verbose(True, True)
    if (decider.is_connected()):
        decider.run()
