#! /usr/bin/python
# -*- coding: UTF-8 -*-
# 

import commands
import string
import sys
import os

GitCmds = {
        "GetCurrentVersion":"bash ./commit.sh current-version",
        "GetLastVersionIdx":"bash ./commit.sh last-version-idx",
        "GeneratePatch":"bash ./commit.sh patch %s",
        "GetEmail":"bash ./commit.sh email",
        "GitAdd":"bash ./commit.sh GitAdd",
        "Commit":"git commit -m ",
}

pwd = os.getcwd()
repoName = pwd.split('/')[-1]

(status, CurrentVersion) = commands.getstatusoutput(GitCmds["GetCurrentVersion"])
if status != 0:
    print "GetCurrentVersion error !"
    sys.exit()

(status, LastVersionIdx) = commands.getstatusoutput(GitCmds["GetLastVersionIdx"])
if status != 0:
    print "GetLastVersionIdx error !"
    sys.exit()

(status, email) = commands.getstatusoutput(GitCmds["GetEmail"])
if status != 0:
    print "GetEmail error !"
    sys.exit()

def TidyLastVersionIdx(strParam):
    strParam = filter(str.isdigit, strParam)
    strParam.strip()

    while True:
        if strParam[0] == '0':
            strParam = strParam[1:]
            print "strParam = ", strParam
        else:
            break

    strParam = string.atoi(strParam)
    return strParam

def TidyCurrentVersion(strParam):
    strParam.strip()
    strParam = strParam.split('=')[1]
    return strParam

def TidyAuthor(strParam):
    strParam.strip()
    strParam = strParam.split('=')[1]
    strParam = strParam.split('@')[0]
    return strParam

CurrentVersion = TidyCurrentVersion(CurrentVersion)
LastVersionIdx = TidyLastVersionIdx(LastVersionIdx)
author = TidyAuthor(email)

CommitVersionIdx = LastVersionIdx + 1

if 0 == status:
    print "CurrentVersion = ", CurrentVersion
    print "LastVersionIdx = ", LastVersionIdx
    print "GetEmail = ", author

CommitParams = "update --> V %s | %.3d" %(CurrentVersion, CommitVersionIdx)

print "CommitParams = ", CommitParams

GitCmds["Commit"] += "\""
GitCmds["Commit"] += CommitParams
GitCmds["Commit"] += "\""
print "commit = ", GitCmds["Commit"]

(status, ret) = commands.getstatusoutput(GitCmds["GitAdd"])
if status != 0:
    print "GitAdd error ! | ret = ", ret
    sys.exit()
else:
    print "ret = ", ret

(status, ret) = commands.getstatusoutput(GitCmds["Commit"])
if status != 0:
    print "Commit error ! | ret = ", ret
    sys.exit()
else:
    print "ret = ", ret

PatchCmd = GitCmds["GeneratePatch"] % repoName
(status, ret) = commands.getstatusoutput(PatchCmd)
if status != 0:
    print "GeneratePatch error | ret = ", ret
    sys.exit()

