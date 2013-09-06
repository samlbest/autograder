# stage1.py - Traverses all directories within baseDir and extracts all tar
# files.
# Author: Sam Best
# Created July 24, 2013

import os
import tarfile

class Stage1:
    baseDir = ""
    students = [] #A list of the directories tars were extracted in

    def __init__(self, baseDirectory="."):
        self.baseDir = baseDirectory
        self.students = []

    #Traverses student directories, extracting valid tarfiles to studentdir/src
    def traverseDirectories(self):
        if not self.baseDir:
            raise Exception("No base directory specified.")

        for root, dirs, files in os.walk(self.baseDir):
            for f in files:
                fullPath = os.path.join(root, f) #generate full relative path to each file
                if tarfile.is_tarfile(fullPath):
                    self.extractSubmission(fullPath, root)

        return self.students

    #Extracts a tarfile to ./root/src
    def extractSubmission(self, filepath, root):
        if not tarfile.is_tarfile(filepath):
            raise("Not a tarfile.")

        try:
            #open tarfile
            archive = tarfile.open(filepath)

            #create root/src if it doesn't already exist
            if not os.path.exists(os.path.join(root, "src")):
                os.mkdir(os.path.join(root, "src"))
            archive.extractall(os.path.join(root, "src"))
        except tarfile.TarError:
            print "Error extracting submission from", os.path.basename(root)

        self.students.append(os.path.basename(root))

#for testing
if __name__ == '__main__':
    test = Stage1()
    test.traverseDirectories()

