#!/usr/bin/env python
# autograder.py
# Written for CS419
# Author: Sam Best
# July 31, 2013

#Autograder modules
import stage1 as Extractor
import stage2 as Compiler #stage 2
import stage3 as Tester
import logger

#Libraries
import urllib
import urllib2
import sys
import ordereddict #replacement for OrderedDict in Python 2.7 (Source: https://pypi.python.org/pypi/ordereddict)
from threading import Timer
import os
import datetime

#Constants
DEBUG = True
PHPPASS = "cs419group1"
MAX_READ = 2**16 #limit file read

class Autograder:
    extractor = ""
    logger = ""
    baseDir = ""
    stages = {}
    timeout = ""
    testfile = ""
    multipleTests = ""
    studentList = []

    def __init__(self):
        self.stages = {'1': False, '2': False, '3': False, '4': False}
        self.stages = ordereddict.OrderedDict(sorted(self.stages.items())) #keep stages in order
        self.timeout = 0 #default no timeout
        #Parse user arguments
        self.parseArgs()

        #Populate student list if contained in log
        self.logger = logger.Logger(self.baseDir)
        self.studentList = self.logger.getStudents()

    def stopGrader(self):
        print "TIMEOUT"
        os.abort()

    #Parse command line arguments. Valid arguments are --stage=n, --timeout=n, --test=FILENAME, --tests=FILENAME
    #Example usage (Run all stages on directory HW1): python autograder.py HW1 --stage=1 --stage=2 --stage=3 --stage=4 --timeout=15 --test=testfile.txt
    def parseArgs(self):
        if len(sys.argv) < 2:
            raise Exception("No arguments provided.")

        #Get directory to grader
        if sys.argv[1][:2] != '--':
            if DEBUG:
                print "Running AUTOGRADER in directory ["+sys.argv[1]+"]"
                print("-"*40)
            self.baseDir = sys.argv[1]

        else:
            if DEBUG:
                print "Running in current working directory."

        #Parse other command line option
        for arg in sys.argv:
            if arg[:2] == '--':
                #Parse stages
                if arg[2:8] == 'stage=':
                    stage = arg[8]
                    if int(stage) in range(1, 5):
                        self.stages[stage] = True
                    else:
                        raise Exception("Stage must be in range 1 to 4: ", arg)

                #Parse timeout (given in minutes)
                elif arg[2:10] == 'timeout=':
                    timeout = arg[10:]
                    if int(timeout) in range(0, 3601):
                        self.timeout = timeout
                    if DEBUG:
                        print "timeout="+self.timeout

                #Parse testfile
                elif arg[2:7] == 'test=':
                    self.testfile = arg[7:]
                    self.multipleTests = False
                    if DEBUG:
                        print "test="+self.testfile

                #Parse testfile list
                elif arg[2:8] == 'tests=':
                    self.testfile = arg[8:]
                    self.multipleTests = True
                    if DEBUG:
                        print "tests="+self.testfile

                else:
                    raise Exception("Invalid argument: ", arg)

        return True

    #Send post with data to url (taken from George's post.py)
    def post(self, url, data):
        encode = urllib.urlencode(data)
        headers = {"User-Agent":"Mozilla/4.0 (compatible; MSIE 5.5;Windows NT)"}
        postRequest = urllib2.Request(url,encode,headers)
        postResponse = urllib2.urlopen(postRequest)
        return postResponse.read()

    #Run stages that are marked as True
    def runStages(self):
        try:
            #Start the timer
            if self.timeout != 0:
                t = Timer(float(60*self.timeout), self.stopGrader)
                t.start()

            for key, value in self.stages.iteritems():
                if value is True:
                    if key == '1':
                        if DEBUG:
                            print "***Running stage one***"
                        self.runStageOne()
                    if key == '2':
                        if DEBUG:
                            print("-"*40)
                            print "***Running stage two***"
                        self.runStageTwo()
                    if key == '3':
                        if DEBUG:
                            print("-"*40)
                            print "***Running stage three***"

                        #Make sure test file argument provided
                        if self.testfile:
                            self.runStageThree()
                        else:
                            raise Exception("No test file provided.")

                    if key == '4':
                        if DEBUG:
                            print("-"*40)
                            print "***Running stage four***"
                        self.runStageFour()
        except Exception, e:
            print "An error occurred. Ending timer:",e
        finally:
            if self.timeout != 0:
                t.cancel()

    #Extract files from student directories and add name of the directory to the database
    def runStageOne(self):
        self.extractor = Extractor.Stage1(self.baseDir) #use current directory if none was specified
        self.studentList = self.extractor.traverseDirectories()

        result = ""
        success = True

        #--------------------Update database---------------------
        for s in self.studentList:
            if DEBUG:
                print "Adding student", s, "to database."
            url = "https://www.samlbest.com/cs419/update_db.php"
            #Update student table:
            data = {"password":PHPPASS, "updateType":"student", "onidID":s, "studentName":s}
            result = self.post(url, data)
            self.createStageLog(self.baseDir+os.sep+s, "stage1", success, result)

            #Get submission id:
            url = "https://www.samlbest.com/cs419/get_submission_info.php"
            data = {"password":PHPPASS, "onidId":s, "assignmentName":os.path.basename(self.baseDir)}
            submissionId = self.post(url, data);

            #Update local log with submission id
            self.logger.setDirectory(self.baseDir+os.sep+s)
            self.logger.createLog("submissionId", submissionId)

            #Create new autograder log in database, deleting old logs for that submission:
            url = "https://www.samlbest.com/cs419/update_db.php"
            data = {"password":PHPPASS, "updateType":"autograderLog", "stage":1, "output":result, "lastSuccessfulStage":1, "submissionId":submissionId, "error":0}
            logresult = self.post(url, data)
            if DEBUG:
                print logresult
        #--------------------------------------------------------

        #Update student log
        self.logger.setDirectory(self.baseDir)
        self.logger.logStudents("students", self.studentList)


    #Run make on extracted directories
    def runStageTwo(self):
        result = ()

        for s in self.studentList:
            #Check if stage1 was successful:
            if not self.checkStages(os.path.join(self.baseDir, s), ("stage1", )):
                if DEBUG:
                    print "Student", s, "had an error in stage1, continuing..."
                continue
            if DEBUG:
                print "Running make in", os.path.join(self.baseDir, s, "src")

            #Run make
            result = Compiler.run_make(os.path.join(self.baseDir, s, "src"))

            #Create logs
            if result[0] is True:
                self.createStageLog(os.path.join(self.baseDir, s), "stage2", True, result[1])
                error = 0
            else:
                self.createStageLog(self.baseDir+os.sep+s, "stage2", False, result[1])
                error = 1

            #--------------------Update database---------------------
            #Get student's latest submission id
            self.logger.setDirectory(os.path.join(self.baseDir, s))
            submissionId = self.logger.getLog("submissionId")

            #Create new autograder log in database, deleting old logs for that submission:
            url = "https://www.samlbest.com/cs419/update_db.php"
            data = {"password":PHPPASS, "updateType":"autograderLogUpdate", "stage":2, "output":result[1], "lastSuccessfulStage":2 if error == 0 else 1, "submissionId":submissionId, "error":error}
            logresult = self.post(url, data)
            if DEBUG:
                print logresult
            #-------------------------------------------------------

    #Runs tests defined in the test files passed as an argument and using the template file
    #to create valid command line statements for each student.
    def runStageThree(self):
        result = ()
        for s in self.studentList:
            #Check if stage 1 and 2 were successful
            if not self.checkStages(os.path.join(self.baseDir, s), ("stage1", "stage2")):
                if DEBUG:
                    print "Student",s, "had an error in stage 1 or 2 and will be skipped."
                continue
            if DEBUG:
                print "Running tests for student",s

            #Run stage 3
            s3 = Tester.Stage3(os.path.join(self.baseDir, s, "src"), self.testfile)
            result = s3.runTests(self.multipleTests)

            #May be multiple outputs from several commands run from testfile
            output = "~~~\n".join(result[1])

            if result[0] is True:
                self.createStageLog(os.path.join(self.baseDir, s), "stage3", True, output)
                error = 0

            else:
                self.createStageLog(os.path.join(self.baseDir, s), "stage3", False, output)
                error = 1
            #--------------------Update database---------------------
            #Get student's latest submission id
            self.logger.setDirectory(os.path.join(self.baseDir, s))
            submissionId = self.logger.getLog("submissionId")

            #Create new autograder log in database, deleting old logs for that submission:
            url = "https://www.samlbest.com/cs419/update_db.php"
            data = {"password":PHPPASS, "updateType":"autograderLogUpdate", "stage":3, "output":output, "lastSuccessfulStage":3 if error == 0 else 2, "submissionId":submissionId, "error":error}
            logresult = self.post(url, data)
            if DEBUG:
                print logresult
            #--------------------------------------------------------

    #Generate a text report from the log file then add to database
    def runStageFour(self):
        for s in self.studentList:
            f = open(os.path.join(self.baseDir, s, 'submit.log'), 'w')
            self.logger.setDirectory(self.baseDir+os.sep+s)
            f.write("ONID ID: "+ s)
            f.write("\nDate graded: "+datetime.datetime.utcnow().strftime("%I:%M%p UTC on %B %d, %Y"))
            f.write("\n###STAGE1###")
            f.write("\nError? No" if self.logger.wasStageSuccessful("stage1") else "\nError? Yes")
            f.write("\nOutput:\n"+self.logger.getLog("stage1").output)

            f.write("\n###STAGE2###")
            f.write("\nError? No" if self.logger.wasStageSuccessful("stage2") else "\nError? Yes")
            f.write("\nOutput:\n"+self.logger.getLog("stage2").output)

            f.write("\n###STAGE3###")
            f.write("\nError? No" if self.logger.wasStageSuccessful("stage3") else "\nError? Yes")
            f.write("\nOutput:\n"+self.logger.getLog("stage3").output)

            f.close()
            fw = open(os.path.join(self.baseDir, s, "submit.log"), 'r')
            logContents = fw.read(MAX_READ)
            #--------------------Update database---------------------
            submissionId = self.logger.getLog("submissionId")
            url = "https://www.samlbest.com/cs419/update_db.php"
            data = {"password":PHPPASS, "updateType":"addTextLog", "textLog":logContents, "submissionId":submissionId}
            logresult = self.post(url, data)
            if DEBUG:
                print logresult
            #--------------------------------------------------------
            fw.close()

    def createStageLog(self, directory, stage, success=True, output=""):
        self.logger.setDirectory(directory)
        self.logger.createStageLog(stage, success, output)
        if DEBUG:
            self.logger.printStageLog(stage)

    #Check list of stages, if any were false return false
    def checkStages(self, directory, stages):
        l = logger.Logger(directory)
        for s in stages:
            if not l.wasStageSuccessful(s):
                return False
        return True

if __name__ == '__main__':
    grader = Autograder()
    grader.runStages()
