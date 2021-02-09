#test comment

#Created by: Nancy Hernandez
#Created on 2/2/21
#CS 4375 Professor Ward
#This program is a user shell for a Unix operating system

import sys
import re
import os

class userShell:
    def __init__(self):
        self.promptUser()

    #this method will identify if the user wants to exit,
    #switch directories or use redirection/pipes
    def promptUser(self):
        while 1:
            command = self.getCommand()
            if command == "exit":
                sys.exit(0)
            elif command[0] == "#":
                pass    #will igore if the line begins with #
            elif "cd" in command:
                command = command.split()
                self.changeDirectory(command[1])
            elif command == "":     #will ignore if empty
                pass
            elif ">" in command or "<" in command:  #redirection input or output
                self.redirection(command)
            elif "|" in command:
                self.pipes(command)
            elif "&" in command:
                self.backgroundTask(command)
            else:
                self.executeCommand(command)


    #this method will identify the command from the terminal
    def getCommand(self):
        terminal = os.getcwd() + "\n$ "      #prints '$' at start of every line
        os.write(1, (terminal).encode())

        userInput = os.read(0, 128)
        userInput = userInput.strip()
        userInput = userInput.decode().split("\n")
        userInput = userInput[0]
        userInput = str(userInput)

        return userInput

    def executeCommand(self, command):
        pid = os.fork()
        if pid == 0:
            self.runCommand(command)
        elif pid > 0:
            os.wait()
        else:
            print("fork failed")

    def changeDirectory(self, path):
        try:
            os.chdir(path)      #will redirect to the specified path
        except:
            os.write(1, "No such directory\n".encode())     #if invalid dir

    def runCommand(self, command):
        #lines 62 - 68 were given by Professor which will execute commands
        line = command.split()
        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, line[0])
            try:
                os.execve(program, line, os.environ)
            except:
                pass
        #if invalid command
        os.write(1, ("shell command " + line[0] + " not found\n").encode())
        sys.exit(0)

    def redirection(self, command):
        pid = os.fork()
        if pid == 0:
            #for redirecting output
            if ">" in command:
                #splitting betweent the > to execute specified command
                command = command.split(">")
                os.close(1)     #will close output
                #will create the file if it doesnt exist and will open for writing only
                os.open(command[1], os.O_CREAT | os.O_WRONLY)
                #chile will inherit what is at 1
                os.set_inheritable(1, True)
            #for redirecting input
            else:
                command = command.split("<")
                os.close(0)     #will close input
                #will open file for reading onlly
                os.open(command[1], os.O_RDONLY)
                #child will inherit what is at 0
                os.set_inheritable(0, True)

            #once files have been open it will run the command
            self.runCommand(command[0])
        elif pid > 0:
            os.wait()
        else:
            print("redirection failed")

    def pipes(self, command):
        #pid = os.fork()
        if "|" in command:
            #next couple lines will split things
            write = command[0:command.index("|")]
            read = command[command.index("|") + 1:]

            pipeIn, pipeOut = os.pipe()
            pid = os.fork()

            for i in (pipeIn, pipeOut):
                os.set_inheritable(i, True)
            #pid = os.fork()
            if pid == 0:
                os.close(1)
                os.dup2(pipeOut, 1)

                for fd in (pipeIn, pipeOut):
                    os.close(fd)

                self.runCommand(write)
            elif pid < 0:
                os.write(2, ("fork fialed returning %d\n" % rc).encode())
                sys.exit()
            # elif pid > 0:
            #     os.wait()
            else:
                os.close(0)
                os.dup2(pipeIn, 0)

                for fd in (pipeIn, pipeOut):
                    os.close(fd)

                self.runCommand(read)

    def backgroundTask(self, command):
        pid = os.fork()
        if pid == 0:
            self.runCommand(command)
        elif pid > 0:
            pass        #will no wait here instead will pass
        else:
            print("background task failed")

shell = userShell()
