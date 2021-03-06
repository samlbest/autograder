# logger.py
# Written for CS419
# Author: Sam Best
# August 16, 2013

import shelve
import os

class Logger:
    studentDir = ""
    log = ""

    def __init__(self, studentDir):
        self.studentDir = studentDir
        self.log = shelve.open(os.path.join(self.studentDir, "log"), flag='c', writeback=True)

    #Close currently open shelf and open new one in new directory
    def setDirectory(self, studentDir):
        self.log.close()
        self.studentDir = studentDir
        self.log = shelve.open(os.path.join(self.studentDir, "log"), flag='c', writeback=True)

    #Add StageLog class with key (stage1, stage2, stage3, stage4) to the shelf file
    def createStageLog(self, key, success=True, output=""):
        data = StageLog(success, output)

        self.log[key] = data

    def logStudents(self, key, data):
        if self.log.has_key(key):
            students = self.log[key]
            for s in self.log[key]:
                if s not in students:
                    self.log[key].append(s)

        else:
            self.log[key] = data

    def createLog(self, key, data):
        self.log[key] = data;

    def getStudents(self):
        if self.log.has_key("students"):
            return self.log["students"]

        return []

    def getLog(self, key):
        if self.log.has_key(key):
            return self.log[key]

        return StageLog(False, "No output.")

    #Display log file
    def printStageLog(self, key):
        if self.log.has_key(key):
            data = self.log[key]
            print "Results for", key, "in", os.path.join(self.studentDir, "log:")
            data.displayOutput()

    def wasStageSuccessful(self, key):
        if self.log.has_key(key):
            data = self.log[key]
            return data.success
        else:
            return False

class StageLog:
    success = ""
    output = ""

    def __init__(self, success=True, output=""):
        self.success = success
        self.output = output

    def displayOutput(self):
        if not self.success:
            print "An error was logged. Output:\n", self.output
        else:
            print "No errors were logged. Output:\n", self.output
