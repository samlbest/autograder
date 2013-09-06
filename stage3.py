# stage3.py - Parses arguments from a template file and then runs tests from
# the test file
# Authors: Sam Best, Steve Dunbar, George Nix
# Created August 16, 2013

import subprocess
import os

class Stage3:
    templateDir = ""
    testFile = ""
    args = ""
    templateFound = ""

    def __init__(self, templateDir, testFile):
        self.templateFound = True
        self.testFile = testFile
        self.templateDir = templateDir
        self.parseTemplate()

    #Extracts template keywords from template file (filename must be "template") and creates a list of
    #the matching command line arguments.
    def parseTemplate(self):
        try:
            self.args = dict(line.strip().split('=') for line in open(os.path.join(self.templateDir, "template")))
            #Make sure program runs from correct directory
            self.args["PROGRAM"] = os.path.join(self.templateDir, self.args["PROGRAM"])
        except IOError:
            self.templateFound = False

    #Runs tests from each testfile
    def runTests(self, isList):
        output = []
        testresult = []
        success = True
        testfileList = []

        if not self.templateFound:
            return (False, ["No template file found."])

        #Run each command contained in test file
        if not isList:
            (success, output) = self.runTestFile(self.testFile)

        #Get filename for each test file and run tests
        else:
            for line in open(self.testFile):
                testfileList.append(os.path.join(os.path.dirname(self.testFile),line.strip()))

            for f in testfileList:
                (checksuccess, testresult) = self.runTestFile(f)
                if not checksuccess:
                    success = False
                for t in testresult:
                    output.append(t)

        return (success, output)

    #Runs a test file using the correct command line arguments.
    def runTestFile(self, filename):
        output = []
        success = True
        for line in open(filename):
            #print success
            try:
                #python 2.7 version:
                #output.append(subprocess.check_output(self.buildCommand(line), universal_newlines=True))
                #python 2.6 version:
                try:
                    command = self.buildCommand(line)
                except Exception, e:
                    output.append("%s\n"%e)
                    success = False
                    continue
                cmd_results = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                out, err = cmd_results.communicate()
                if out:
                    output.append(out)
                if err:
                    output.append(err)
                    success = False
            except subprocess.CalledProcessError as e:
                output.append(e.output)
                return (False, output)

        return (success, output)

    #Replaces template keywords from the test file with the matching argument.
    def buildCommand(self, testcmd):
        #Make sure all keys are in template
        for arg in testcmd.strip().split():
            if arg not in self.args.keys():
                raise Exception("Missing template keyword: "+arg)

        cmd = testcmd
        for key, value in self.args.items():
            cmd = cmd.replace(key, value)
        return cmd.strip().split()

if __name__ == '__main__':
    test = Stage3("test_data/hw1")
    test.runTests("test_data/hw1/test1.txt")
