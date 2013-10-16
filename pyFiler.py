#Pyfileing
#
#Interactive program to quickly sort files and folder into folders
#that require a human to choose final destination

#Two parts, 
#Shell
#The interactive shell that has a dictionry of paths and input-shortcuts
#that asks the user where a certan file shold go.

#MovingVan
#Script that constanctly is looking for files to read in a working dir
#that contain on two lines, the source path, and destination path
#This script will be creating folders, not the shell. 
#The shell shall have a dictonary of paths that that it has already asked
# about if they do not exist.


#doto creating new shortcuts

import os
import sys #not sure if needed
import pickle

from byteconvert import *
from shortcuts import *
#os.path.walk



class FilingCabnet():
    def __init__(self):
        #init dictionary to contain paths and their shortcuts
        self.path_dict = shortcuts #global dict from import
        #dictionary of paths that do not exist that should not be asked abou
        self.path_exceptions = {}
        
        #passive commands are called with no args and still requte further input
        self.passive_commands = {"mv" : self.set_to_move,
                                "cp" : self.set_to_copy,
                                "shorts" : self.print_shortcuts,
                                "?" : self.print_input_help,
                                 }
        #folder where move files are saved
        self.move_directions_path = "./move_directions/"
        self.current_mode = 'mv'

    def add_shortcut(self, shortname, path):
        """Try to add a new shortcut-path to the dict,
        if already existing, confirem overwrite, 
        if overwite true: move the overwirten path to trashpath:<overwritenpath>
        
        """
        #todo: overwite conferm
        valid = True
        #test is path exists, if not ask if to creat path
        valid = self.path_exists(path)
        if not valid:
            valid = self.create_path_exception(path)
            #returns True only if user chooses to create nonexsitance dir
        if valid:
            self.path_dict[shortname] = path


    def save_shortcuts(self):
        f = open("shortcuts.py", "w")
        f.write("shortcuts = " + repr(self.path_dict))
        f.close

    def path_exists(self,path):
        "returns True if path exists or is in self.path_exceptions"
        if path in self.path_exceptions:
            return True
        else:
            return os.path.exists(path)

    def create_path_exception(self, path):
        print("%s does not exist."%path)
    
        if raw_input("Would you like to create it? (y/n)").lower().startswith("y"):
            self.path_exceptions[path] = True
            return True
        else: return False
            
    
    def create_move_file(self, file_path, dest_path):
        """Creates a file consiting of two lines, the file path, and dest_path in self.move_directions_path
        """
        f = open(os.path.join(self.move_directions_path, os.path.split(file_path)[1]+".order"), "w")
        f.write(self.current_mode + "\n")
        f.write(file_path)
        f.write("\n")
        f.write(dest_path)
        f.close()

    def create_delete_file(self, file_path):
        f = open(os.path.join(self.move_directions_path, os.path.split(file_path)[1]+".order"), "w")
        f.write("del" + "\n")
        f.write(file_path)
        f.close()
        
    def run(self, path):
        if raw_input("is %s the correct working path? (y/n)"%os.path.realpath(path)
                 ).lower().startswith("n"):
            path = ""
            while not os.path.exists(path):
                print("please input a valid path for what folder to sort")
                path = raw_input()
        
        self.sort_dir(path)
        self.save_shortcuts()
        sys.exit()

    def sort_dir(self, dirname):
        fnames = os.listdir(dirname) #create list of files/folers
        if raw_input("Start sorting %s with files? (y/n)"%os.path.realpath(dirname)).lower().startswith("y"):
            self.dirs_to_end(dirname,fnames)
        else:
            self.files_to_end(dirname, fnames)
        for f in fnames:
            if os.path.isdir(os.path.realpath(os.path.join(dirname,
                                                           f))):
                #will return a path to moveto, or None to skip,
                path = self.ask_for_input(dirname, f)
                if path is None:
                    continue
                if path == "enter":
                    self.sort_dir(os.path.join(dirname,f))
                else:
                    self.create_move_file(os.path.join(dirname, f), path)               
            else:
                self.sort_file(dirname,f)

    def sort_file(self, dirname, f):
        path = self.ask_for_input(dirname, f) #will return a path, or None
        if path is None:
            return
        if path == "del":
            self.create_delete_file(os.path.join(dirname, f))
        else:
            self.create_move_file(os.path.join(dirname, f), self.path_dict[path])
        
            
            
            

    def ask_for_input(self, dirname, f):
        """prints current mode and Asks for input from the user
        responces should be:
        "?" : prints help
        "shorts" : prints shortcuts
        [shortcut] : will move/copy file to shortcut destinatnon
        "mv" : set default action to move
        "cp" : set defualt action to copy
        "quit" : quits, asks if it is wanted to save shortcuts
        "enter" : starts walking the dir that is being looked at
        "skip" : skips current file #not done at all
        "del" : deletes current file #not done at all
        """

        responce = None
        
        self.print_info(dirname, f)
        responce = raw_input("%s:"%self.current_mode)
        responce = responce.strip() 
        if responce.lower() in self.path_dict:
            return responce
        elif responce.lower() == "del":
            return "del"
        elif responce.lower() in ("", "skip"):
            return None

        elif responce.lower() == "enter" and\
                os.path.isdir(os.path.realpath(os.path.join(dirname,f))):
            return "enter"

        elif responce.lower() in self.passive_commands:
            self.passive_commands[responce]()
            return self.ask_for_input()
        else:
            new_shortcut = self.is_new_shortcut(responce)
            if new_shortcut in self.path_dict:
                return new_shortcut 
            else:
                return self.ask_for_input(dirname, f)
    def is_new_shortcut(self, path):
        print("%s is not a reconised command. \nPlease Enter a new shortcut if it is a new shortcut path.\n othwise just press enter"%path)
        shortcut = raw_input("Shortcut: ")
        if shortcut == "":
            return None
        elif shortcut in self.passive_commands:
            print("that shortcut is a reserved shortcut")
            return self.is_new_shortcut(path)
        else:
            self.add_shortcut(shortcut, path)
            return shortcut
            

    def print_input_help(self):
        print( """prints current mode and Asks for input from the user
        responces should be:
        "" : prints help
        "shorts" : prints shortcuts
        [shortcut] : will move/copy file to shortcut destinatnon
        "mv" : set default action to move
        "cp" : set defualt action to copy
        "quit" : quits, asks if it is wanted to save shortcuts
        "enter" : starts walking the dir that is being looked at
        "skip" : skips current file #not done at all
        "del" : deletes current file #not done at all
        """)

    def print_info(self, dirname, filename):
        print(os.path.realpath(dirname))
        print(filename)
        if os.path.isdir(os.path.realpath(os.path.join(dirname,
                                                       filename))):
            for f in os.listdir(os.path.join(os.path.realpath(dirname),filename))[:5]:
                s = "\t%s\t%s"%(f,bytes2human(os.stat(os.path.join(os.path.realpath(dirname),filename,f)).st_size))
                if os.path.isdir(os.path.join(os.path.realpath(dirname),filename,f)):
                    s += "\t [DIR]" 
                print(s)
        print(bytes2human(os.stat(os.path.join(os.path.realpath(dirname),filename)).st_size))

    def print_shortcuts(self):
        for s, p in self.path_dict.items():
            print("%s/t%s"%(s,p))
        
    def files_to_end(self, dirname, fnames):
        """ moves all dirs in fnames to the end of fnames
        modifyes fnames"""
        files = []
        for f in fnames:
            if os.path.isfile(os.path.realpath(os.path.join(dirname,
                                                           f))):
                files.append(f)
        for f in files:
            fnames.remove(f)
            fnames.append(f)
        return fnames
        
            
    def dirs_to_end(self, dirname, fnames):
        """ moves all dirs in fnames to the end of fnames
        modifyes fnames"""
        dirs = []
        for f in fnames:
            if os.path.isdir(os.path.realpath(os.path.join(dirname,
                                                           f))):
                dirs.append(f)
        print dirs
        for d in dirs:
            fnames.remove(d)
            fnames.append(d)
        return fnames

    def set_to_move(self):
        self.current_mode = 'mv'
    
    def set_to_copy(self):
        self.current_mode = 'cp'

    def quit(self):
        if raw_input("Do you wish to save current shortcuts? (y/n)").lower().startswith("y"):
            self.save_shortcuts()
        sys.exit()



if __name__ == "__main__":
    f = FilingCabnet()
    f.run(".")
