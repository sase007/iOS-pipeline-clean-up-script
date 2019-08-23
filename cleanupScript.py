#!/usr/bin/env python3
import os
import subprocess
import shutil
from datetime import datetime, timedelta
import time
import sys

def diskSize():
    total, used, free = shutil.disk_usage('/')
    return [total // (2**30), used // (2**30), free // (2**30)]

def main():
    heads = []
    directories = []
    lastCacheDirectories = []
    otherDirectories = []
    diskSpace = []
    remotes = subprocess.check_output(["git", "ls-remote", "--heads"],universal_newlines=True).splitlines()
    currentTimestamp = int(time.time())

    archivesDirectory = os.path.expanduser('~/Library/Developer/Xcode/Archives/')
    devicesDirectory = os.path.expanduser('~/Library/Developer/CoreSimulator/Devices/')
    coreSimulatorDirectory = os.path.expanduser('~/Library/Logs/CoreSimulator/')
    userDataDirectory = os.path.expanduser('~/Library/Developer/Xcode/UserData/IB Support/Simulator/')

    heads = [w[:40] for w in remotes]
    directories = [x[0] for x in os.walk("/Users/administrator/cache/mobile/ios")] #This is the path to ours cache, change it to yours

    if directories:
        directories.pop(0)

    diskSpaceBefore = diskSize()
    print("\nFree space before cleaning: " + str(diskSpaceBefore[2]) + " G")
    print("Percentage of space used: " + str((diskSpaceBefore[1]/diskSpaceBefore[0])*100)[:5] + " %")

    for directory in directories:
        for head in heads:
            if head in directory:
                lastCacheDirectories.append(directory)

    lastCacheDirectories = list({i for sub in lastCacheDirectories for i in sub.split(' ')})
    otherDirectories = list(set(directories) - set(lastCacheDirectories))

    print("\nList of all directories at path: ")
    for directory in directories:
        print(directory)

    print("\nList of directories to be deleted (reason: cache not head of branch): ")
    for directory in otherDirectories:
        print(directory)
        shutil.rmtree(directory)

    print("\nList of directories to be deleted (reason: cache past 7 days): \n")
    for directory in directories:
        if os.path.isdir(directory):
            folderTime = int(os.stat(directory).st_mtime)
            if (folderTime+604800) < currentTimestamp:
                 print(directory)
                 shutil.rmtree(directory)

    os.system('xcrun simctl list | grep pipeline_simulator | cut -d "(" -f 2 | cut -d ")" -f 1 | while read sim; do xcrun simctl delete $sim; done')

    if os.path.isdir(archivesDirectory):
        shutil.rmtree(archivesDirectory)
    else:
        print("Archives directory not found!")

    if os.path.isdir(devicesDirectory):
        shutil.rmtree(devicesDirectory)
    else:
        print("Devices directory not found!")

    if os.path.isdir(coreSimulatorDirectory):
        shutil.rmtree(coreSimulatorDirectory, ignore_errors=True)
    else:
        print("Core simulator directory not found!")

    if os.path.isdir(userDataDirectory):
        shutil.rmtree(userDataDirectory)
    else:
        print("User data directory not found!")

    diskSpaceAfter = diskSize()
    spaceFreed = diskSpaceBefore[1] - diskSpaceAfter[1]
    print("\nFree space after cleaning: " + str(diskSpaceAfter[2]) + " G")
    print("Percentage of space used: " + str((diskSpaceAfter[1]/diskSpaceAfter[0])*100)[:5] + " %")
    print("Freed space: " + str((spaceFreed)) + " G")

    if diskSpaceAfter[2] < 30:
        cmd = 'bundle exec fastlane diskSpace slackUserName:{0} freeSpace:{1}'.format(sys.argv[1], diskSpaceAfter[2])
        os.system(cmd)

if __name__ == '__main__':
    main()
