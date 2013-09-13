autograder
==========

A tool written in Python which can be used with an SQL database to automate some of the grading of C and C++ assignments.

**Note: This was part of a group project for school. All of the documentation and code in this repo except for a preliminary version of stage2.py (created by Steve Dunbar) was written by me.**

#Project Documentation#
The program is divided into four main stages. These stages can be run independently but must be run in order. For example, stage 2 can be executed on its own but it will only be successful if stage 1 has already ran. Stages that have already been run for a student will not be run unnecessarily even if the Autograder is executed again for that stage.

Each stage updates a local log within the student directory (filename = “log”). These logs use Python’s shelve library (http://docs.python.org/2/library/shelve.html). The output and error information are also added to a MySQL database.

##Stage 1##
Traverse all directories within the assignment directory and extract all valid tarfiles to a /src subdirectory. Each base directory must correspond to the ONID ID of a student because the name of each directory that a tarfile has been successfully extracted in is used to create a list of students which is added to the local log file in each student’s directory and added to the SQL database. This list of students is used to point the subsequent stages to the correct directories.

##Stage 2##
This stage enters each student directory and runs make to compile student submissions. All output from make is logged locally. If an error occurred, it will also be noted. This information is also added to the SQL database.

##Stage 3##
Stage 3 enters each student’s directory, parses a template file that is provided by each student and translates the template keys defined for the assignment to the command line options specific to the student’s program. It then references one or multiple test files provided by the instructor to run the student’s program and test its correctness.

##Stage 4##
This is the only stage that can be run for all students regardless of errors that occurred in prior stages. It accesses the local log in each student directory and generates a structured text report. This report is added to the database as a TEXT object.

#Program Structure#
The program is written in Python. The Autograder class contained in autograder.py is the interface to the program. It contains functions to parse the command line arguments, run the requested stages, and update the database. Stages 1-3 are implemented in separate files and imported through the Autograder class. Stage 4 is implemented within autograder.py because it’s simpler than the other stages.

##autograder.py##
Contains the Autograder class. This keeps track of a number of member variables that are needed for stages 1-3.

```extractor```: An instance of the stage 1 class.

```logger```: An instance of the logger class which contains some utility functions for creating shelves.

```baseDir```: String, set to the relative path of the assignment directory (specified by the command line argument described in the “how does one run it” section).

```stages```: An ordered dictionary defining the stages which should be run (specified by command line arguments). The dictionary keys are ‘1’, ‘2’, ‘3’, ‘4’ and their values are Booleans.

```timeout```: The length the autograder should be allowed to run, in minutes.

```testfile```: The relative location of the test file or test file list.

```multipleTests```: A Boolean specifying whether the testfile references a list or a single test file.

```studentList```: A list of student directories. This should correspond with student ONID IDs.

###Functions###
```parseArgs(self, url, data)```: Parses command line arguments and assigns values to corresponding members.

```post(self, url, data)```: Updates the database by sending a POST request to the script at the url parameter. The data parameter expects a Python dictionary.

```runStages(self)```: Starts a timer if a timeout is specified, then runs each stage which is set to True in the self.stages member. If timer exceeds timeout at any time, grader is aborted.

```runStageOne(self)```: Runs stage 1 (described above).

```runStageTwo(self)```: Runs stage 2.

```runStageThree(self)```: Runs stage 3.

```runStageFour(self)```: Runs stage 4.

```createStageLog(self, directory, stage, success=True, output=””)```: Accesses the logger member to create a log containing the error status and the output for the specified stage in the specified directory.

```checkStages(self, directory, stages)```: This is used by stage 2 and 3 to check whether the specified stages were successful for the log contained in the student directory given by the directory parameter.

##stage1.py##
Uses os.walk to traverse all of the directories within the assignment directory and the tarfile library to extract all valid tarfiles.

###Member variables###
```baseDir```: This is a string defining the root of the directory tree which should be traversed. This will normally be the assignment directory specified by the Autograder.

```students```: The name of each directory where an archive is successfully extracted is added to this list, which is returned after the traversal function completes.

##Functions##
```traverseDirectories(self)```: Checks all files within each directory in the tree rooted by baseDir. Uses tarfile.is_tarfile to check if the file is an archive. If it is, calls extractSubmission() with the corresponding path.

```extractSubmission(self, filepath, root)```: Runs stage 1 (described above).

###stage2.py###
This file contains a function which runs make and returns any output.

##Functions##
```run_make(dir)```: Runs make in the directory specified by the dir parameter and returns a tuple containing the error status and the output.

###stage3.py###
This file contains the Stage3 class which runs tests after translating test file templates into valid console commands for each student’s program using the student’s template file.

##Member variables##
```templateDir```: This is a string defining the location of the template file (passed by Autograder). Typically this will be studentname/src.

```testFile```: Location of the test file or test file list.

```args```: A dictionary created from the student template file. The keys are the template keys defined in the assignment description and the values are the specific command line options set in each student’s template file.

```templateFound```: Set to False when an exception is raised on attempting to access the template file.

##Functions##
```runTests(self, isList)```: If isList is False, calls runTestFile() with the test file location and returns the error status and output of the test. If isList is True, calls runTestFile() once for each line  in the test file list, passing the path of the test file given on each line.

```runTestFile(self, filename)```: Uses buildCommand() to create a console command based on the test file but valid for each student’s particular program name and options.

```buildCommand(self, testcmd)```: testcmd is the list of template keys taken from each test file. buildCommand() checks that all of the keys are present in the self.args list (created from the student template file) and replaces each of the keys in testcmd with the corresponding options.

###logger.py###
This contains a utility class which facilitates creation of shelve logs. It also contains the StageLog class which is the format that data for each stage are stored. The StageLog contains a success flag and the output for each stage.

##Member variables##
```studentDir```: The directory of the log currently being accessed.

```log```: A shelve reference to the log currently being used.

###Functions###
```setDirectory(self, studentDir)```: Closes the current log, then updates self.studentDir to studentDir and opens a new log in writeback=True mode, creating a new one if it doesn’t already exist. Writeback mode allows modification of log variables beyond simple writes. For example, it enables use of .append() on log variables without using a temp variable.

```createStageLog(self, key, success=True, output=””)```: Creates a new instance of the StageLog class and adds it to the log with the key passed as a parameter. Key created by the Autograder will be “stage1”, “stage2”, or “stage3”.

```logStudents(self, key, data)```: Saves a new student list (passed through data) in the log if one doesn’t exist. Otherwise, adds non-duplicate students contained in data to the log. This allows Autograder to be run multiple times without loss of students (when stage1 isn’t run for all students) or redundancy (when a student is already on the list).

```createLog(self, key, data)```: Creates a log containing data with the passed key.

```getStudents(self)```: Returns the student list from the current log if it exists.

```getLog(self, key)```: Returns the log specified by key if it exists.

```printStageLog(self, key)```: Outputs results of the specified stage.

```wasStageSuccessful(self, key)```: Checks if the stage given by key was successful for the current log.

###ordereddict.py###
This is a Python 2.6-compatible replacement for the collections.OrderedDict subclass introduced in Python 2.7. If Python 2.6 compatibility is not required, this can be easily replaced with OrderedDict by modifying line 39 in autograder.py to use the built-in OrderedDict. Documentation for the replacement can be found at https://pypi.python.org/pypi/ordereddict.
