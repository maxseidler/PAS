# imports
import collections
import bisect
import time
import os
import os.path
import logging
import numpy
import threading

import ConfigParser
import util.nullhandler

logging.getLogger('Borg.Brain.Memory').addHandler(util.nullhandler.NullHandler())

class Memory(object):
    """ A singleton memory object""" 
    """Stores and retrieves perceptions, and possibly other objects such as
    plans or goals. """ 
    
    # storage for the instance reference
    __instance = None
           
    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Memory.__instance is None:
            Memory.__instance = Memory.__impl()# Create and remember instance
        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Memory.__instance
        self.logger = logging.getLogger("Borg.Brain.Memory")

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)

    
    class __impl:
        """ Implementation of the singleton interface """
        ##### MEMORY HANDLING #####
        def __init__(self):
            self.database = collections.defaultdict(list)
            """database is a name-indexed dictionary of lists consisting of (time, properties_dict) tuples"""
            self.recognizable_objects = {}
            
            #create a filehandle for the log:
            self.log_handle = open(os.path.abspath(os.environ['BORG'] + '/brain/src/memory.log'), 'a')

            self.config = ConfigParser.ConfigParser()
            self.config.read(os.path.abspath(os.environ['BORG'] + '/brain/src/config/mem_config'))

            self.memory_lock = threading.RLock()

            self.keep_lastonly = []
            for (name, _) in self.config.items("lastonly"):
                self.keep_lastonly.append(name)

            self.keep_long = []
            for (name, _) in self.config.items("long"):
                self.keep_long.append(name)


        def add_item(self, name, time, properties):
            """add observation at time of item to memory"""
            with self.memory_lock:
                if name in self.keep_lastonly:
                  #If we should keep only last observation, overwrite any other entry
                  self.database[name] = [(time, properties)]
                else:
                  #else append it to the list of observations
                  self.append_item(name, time, properties)
                self.log_addition(name,time,properties)

        def append_item(self, name, time, properties):
            """
            When we need to keep all observations of an item,
            add it to the list of existing observations of that item if it exists.
            The list has to be sorted, so append it if it's the latest or else
            insert it at the correct part of the list.
            """
            with self.memory_lock:
                itemlist = self.database[name]

                if itemlist == [] or self.get_last_observation(name)[0] <= time:
                    #simply add it to the end
                    itemlist.append((time, properties))
                else:
                    bisect.insort_left(itemlist, (time, properties)) #keep it sorted



        def clear(self):
            "Memorie cleared, this should only be done for testing"
            with self.memory_lock:
                self.database = collections.defaultdict(list)

        def add_recognizable_object(self,modulename,new_object):
            '''when a new module is started, it can use this function to register what it can recognize, one object at a time'''
            with self.memory_lock:
                if modulename not in self.recognizable_objects:
                    self.recognizable_objects[modulename] = []
                self.recognizable_objects[modulename].append(new_object)

        def add_recognizable_objects(self,modulename,objects):
            '''when a new module is started, it can use this function to register what it can recognize'''
            with self.memory_lock:
                self.recognizable_objects[modulename] = objects

        def clean_recognizable_objects(self,modulename):
            '''unregister a module, delete all objects that module has registered'''
            with self.memory_lock:
                del self.recognizable_objects[modulename]


        ##### MEMORY RETRIEVAL #####
        def get_database(self):
            """returns the database, a name-indexed dictionary of lists consisting of (time, properties_dict) tuples"""
            with self.memory_lock:
                return self.database
        
        def n_items(self):
            """return number of distinct types of items in memory"""
            with self.memory_lock:
                return len(self.database)

        def get_last_observation(self, name, oldskool=True):
            """return a (time, properties_dictionary) pair"""
            with self.memory_lock:
                try:
                    if oldskool:
                        return self.get_observations(name)[-1] #last item in list
                    else:
                        return self.get_observations(name)[-1][1]
                except:
                    return None

        def get_recent_observations(self, name, time_since, oldskool=True):
            """returns a list of (time, property_dictionary) pairs"""
            with self.memory_lock:
                try:
                    if oldskool:
                        itemlist = self.database[name]
                        #TODO: to be improved:
                        #bisect compares tuple to tuples in itemlist
                        #we are now using a nonsensical properties dict ({'a': 'a'})
                        #just to be able to compare the tuple with the time_since
                        indexfrom = bisect.bisect(itemlist, (time_since, {'a': 'a'}))
                        return itemlist[indexfrom:]
                    else:
                        itemlist = self.database[name]
                        indexfrom = bisect.bisect(itemlist, (time_since, {'a': 'a'}))
                        return [x[1] for x in itemlist[indexfrom:]]
                except:
                    return []


        def has_understood(self, start_time, text_list):
            """
            Returns true if one or more text messages inside text_list are received by the speech recognizer.
            """
            if self.n_occurs("voice_command") == 0:
                return False

            obs_list = self.get_observations("voice_command")
            #TODO: Use get_recent_observations instead:
            for obs in obs_list:
                (time, props) = obs
                if time > start_time:
                    command = props['message']
                    for text in text_list:
                        if command == text:
                            return True
            return False


        def n_occurs(self, name):
            """count how often the object was perceived"""
            with self.memory_lock:
                try:
                    return len(self.database[name])
                except:
                    return 0

        def get_observations(self, name, oldskool=True):
            """returns a list of (time, property) tuples"""
            with self.memory_lock:
                if oldskool:
                    return self.database[name]
                else:
                    return [x[1] for x in self.database[name]]

        def is_now(self,object, properties):
            '''check if an object has a property now'''
            with self.memory_lock:
                if (self.n_occurs(object) == 0):
                    return False
                observation = self.get_last_observation(object)
                treshhold_time = time.time() - 5
                (obs_time, obs_properties) = observation
                if (obs_time < treshhold_time):
                    #observation was to long ago
                    return False
                #set all properties in memory
                for key in obs_properties.keys():
                    try:
                        exec(key + " = obs_properties[key]")
                    except SyntaxError:
                        print "Memory: Error: " + str(obs_properties[key]) + " is bad syntax!"
                    except NameError:
                        print "Memory: Error: " + str(obs_properties[key]) + " is an unknown name!"
                    
                #now eval all the properties
                for prop in properties:
                    try:
                        if (eval(prop) == False):
                            return False
                    except NameError:
                        return False
                return True


        def was_ever(self,object, properties):
            '''check if an object ever had some property'''
            with self.memory_lock:
                if (self.n_occurs(object) == 0):
                    return False
                observations = self.get_observations(object)
                for (obs_time, obs) in observations:
                    #set all properties in memory
                    for key in obs.keys():
                        try:
                            exec(key + " = obs[key]")
                        except SyntaxError:
                            print "Memory: Error: " + str(obs_properties[key]) + " is bad syntax!"
                    #now eval all the properties
                    this_one_valid = True
                    for prop in properties:
                        try:
                            if (eval(prop) == False):
                                this_one_valid = False
                        except NameError:
                            this_one_valid = False
                    if (this_one_valid):
                        return True
                return False


        def was_last_time(self,object, properties):
            '''check if an object had some property the last time it was seen'''
            '''can for example be used to check on a status of something (i.e. door open)'''
            
            with self.memory_lock:
                if (self.n_occurs(object) == 0):
                    return False
                observation = self.get_last_observation(object)
                (obs_time, obs_properties) = observation
                #set all properties in memory
                for key in obs_properties.keys():
                    try:
                        exec(key + " = obs_properties[key]")
                    except SyntaxError:
                        print "Memory: Error: " + str(obs_properties[key]) + " is bad syntax!"
                    except NameError:
                        print "Memory: Error: " + str(obs_properties[key]) + " is an unknown name!"
                #now eval all the properties
                for prop in properties:
                    try:
                        if (eval(prop) == False):
                            return False
                    except NameError:
                        return False
                return True





        def get_objects_seen_since(self,time):
            '''return the objects we have seen till now (unique list)'''

            #TODO: check for each object we have whether it is on the list of recognizable objects
            #if an item is in there, return it (a unique list of them)

            with self.memory_lock:
                return [] #TODO: implement
            #TODO: test


        ##### MEMORY LOGGING #####
        def load_log(self,filename):
        
            with self.memory_lock:
                fd = open( os.environ['BORG'] + '/brain/src/memory.log')

                content = fd.readline()
                while (content != "" ):

                    print "LINE: " + content

                    time = content.split('|')[0]
                    name = content.split('|')[1]
                    #load the dictionary of properties:
                    exec("props = " + content[(len(time) + len(name)):])

                    self.add_item(name, time, props)

                    content = fd.readline()



        def log_addition(self, name, time, properties):
            '''add the added memory item to the log'''


            with self.memory_lock:
                self.log_handle.write(str(time) + "|" + name + "|" + str(properties) + "\n")
            


        ##### REGISTERING WHAT MODULES CAN DETECT #####
        def get_recognizable_objects(self):
            '''returns all objects that we can possibly recognize (no determined order!)'''
            with self.memory_lock:
                all_objects = []
                for key in self.recognizable_objects.keys():
                    for object in self.recognizable_objects[key]:
                        all_objects.append(object)
                ret = list(set(all_objects))
                return ret

        def is_object_recognizable(self,object):
            '''check if the current sensor modules can recognize some object'''
            #loop over all modules
            with self.memory_lock:
                for key in self.recognizable_objects.keys():
                    if object in self.recognizable_objects[key]:
                        return True
                return False

