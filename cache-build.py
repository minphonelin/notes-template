#! /usr/bin/python
# -*- coding: UTF-8 -*-
# Created Time: 2022-01-14 18:19:10
#

import os
import commands
import pdb

NOTES_NAME = 'notes.tex'
NOTES_CACHE_DIR = '/tmp/notes-cache'
CUR_DIR = os.getcwd()

if os.path.isdir(NOTES_CACHE_DIR) is False:
  os.system('mkdir %s' % NOTES_CACHE_DIR)
else:
  os.system('rm -rf %s/*' % NOTES_CACHE_DIR)

print 'NOTES_CACHE_DIR = ', NOTES_CACHE_DIR
print 'CUR_DIR = ', CUR_DIR

# os.system('cp -r %s/* %s' % (CUR_DIR, NOTES_CACHE_DIR))

def CollectCacheFilesOfDir(cacheDir):
  (_, status) = commands.getstatusoutput("find %s -name \"*.tex\"" % cacheDir)
  print "status = \n", status
  fileList = []

  statusLine = status.split('\n')
  for line in statusLine:
    if '.tex' in line:
      fileList.append(line)

  return fileList

def CollectNeedCacheFiles():
  (_, status) = commands.getstatusoutput("git status")
  print "status = \n", status

  # 
  # eg. 
  #
  # On branch master
  # Changes not staged for commit:
  #   (use "git add/rm <file>..." to update what will be committed)
  #   (use "git checkout -- <file>..." to discard changes in working directory)
  # 
  #         modified:   languages/python/basic.tex
  #         modified:   languages/shell/program.tex
  #         modified:   linux/main.tex
  #         modified:   title/main.tex
  #         deleted:    windows/config.tex
  # 
  # Untracked files:
  #   (use "git add <file>..." to include in what will be committed)
  # 
  #         cache-build.py
  #         linux/linux-directory.tex
  #         windows/umd/
  #
  # no changes added to commit (use "git add" and/or "git commit -a")
  #
  cacheMap = {'modified':[], 'deleted':[], 'added':[]}

  statusLine = status.split('\n')
  lineList = []
  for line in statusLine:
    if '.tex' in line:
      lineList.append(line)
    else:
      line = line.strip()
      if len(line) > 0 and line[-1] == '/':
        lineList.append(line)

  for line in lineList:
    if 'title/' in line:
      continue

    if 'modified:' in line:
      line = line.replace('modified:', '').strip()
      cacheMap['modified'].append(line)
    elif 'deleted:' in line:
      line = line.replace('deleted:', '').strip()
      cacheMap['deleted'].append(line)
    else:
      line = line.strip()
      cacheMap['added'].append(line)

  #
  # check and update cacheMap['added']
  #
  addedList = []
  for u in cacheMap['added']:
    if '.tex' in u:
      addedList.append(u)
    else:
      addedList.extend(CollectCacheFilesOfDir(u))
  cacheMap['added'] = addedList

  return cacheMap

def GenDirectoryList(dirList, fileList):
  for fn in fileList:
    print 'fn = ', fn
    varPath = ''
    for subPath in fn.split('/'):
      if '.tex' not in subPath:
        if len(varPath) == 0:
          varPath = subPath
        else:
          varPath = varPath + '/' + subPath
        if varPath not in dirList:
          dirList.append(varPath)
  return dirList

def PrepareCacheDirs(cacheMap):
  #
  # dirList =  ['linux', 'languages', 'languages/python', 'languages/shell']
  #
  dirList = []
  dirList = GenDirectoryList(dirList, cacheMap['added'])
  dirList = GenDirectoryList(dirList, cacheMap['modified'])

  print 'dirList = ', dirList

  for varDir in dirList:
    varPath = NOTES_CACHE_DIR + '/' + varDir
    if os.path.exists(varPath) is False:
      os.system('mkdir %s' % varPath)

def IsSectionName(line):
  bSN = False
  if '\\chapter{' in line: bSN = True           # 1
  elif '\\section{' in line:  bSN = True        # 2
  elif '\\subsection{' in line: bSN = True      # 3
  elif '\\subsubsection{' in line: bSN = True   # 4
  elif '\\paragraph{' in line: bSN = True       # 5
  elif '\\subparagraph{' in line: bSN = True    # 6
  elif '\\subsubparagraph{' in line: bSN = True # 7
  return bSN

def GetSectionLevelFromName(sectionName):
  level = 0
  if sectionName is not None and len(sectionName) > 0:
    if '\\chapter{' in sectionName: level = 1
    elif '\\section{' in sectionName: level = 2
    elif '\\subsection{' in sectionName: level = 3
    elif '\\subsubsection{' in sectionName: level = 4
    elif '\\paragraph{' in sectionName: level = 5
    elif '\\subparagraph{' in sectionName: level = 6
    elif '\\subsubparagraph{' in sectionName: level = 7
    else: level = 0
  return level

#
# @@ -119,12 +119,6 @@ xxx
# -> 119
#
def GetLineIndexFromBlockTag(blockTagElement):
  return blockTagElement.split(',')[0].replace('+', '').strip()

#
# @@ -119,12 +119,6 @@ xxx
# -> 6
#
def GetLineCntFromBlockTag(blockTagElement):
  return blockTagElement.split(',')[1].strip()

def GetBlockContentFromGitDiffStatus(tag, content):
  lineIndex = int(GetLineIndexFromBlockTag(tag))
  lineCnt = int(GetLineCntFromBlockTag(tag))
  blockContent = content[lineIndex - 1 : lineIndex + lineCnt - 1]

  # add forward line
  for line in content[: lineIndex - 1][::-1]:
    blockContent.insert(0, line)
    if IsSectionName(line) is True:
      break

  # add backward line
  for line in content[lineIndex + lineCnt - 1:]:
    if IsSectionName(line) is True:
      break
    else:
      blockContent.append(line)

  return blockContent

__metaclass__ = type
class SectionBlock:
  def __init__(self, name = None):
    self.m_name = name
    self.m_level = GetSectionLevelFromName(name)
    self.m_parent = None
    self.m_file = None
    self.m_isParentAndChildInTheSameFile = None
    self.m_content = None
  def Name(self):
    return self.m_name
  def Parent(self):
    return self.m_parent
  def Level(self):
    return self.m_level
  def File(self):
    return self.m_file
  def Content(self):
    return self.m_content
  def IsParentAndChildInTheSameFile(self):
    return self.m_isParentAndChildInTheSameFile
  def SetParent(self, parent):
    self.m_parent = parent
  def SetFile(self, fileName):
    self.m_file = fileName
  def SetContent(self, content):
    self.m_content = content
  def SetIsParentAndChlidInTheSameFile(self, bSame):
    self.m_isParentAndChildInTheSameFile = bSame

def AddSectionBlockIntoSectionBlockList(sectionBlockList, sectionBlockString):
  if len(sectionBlockString) > 0:

    objSecBlk = SectionBlock(sectionBlockString[0])
    objSecBlk.SetContent(sectionBlockString[1:])

    if objSecBlk.Level() == 0:
      return sectionBlockList

    if len(sectionBlockList) > 0:
      bExist = False
      for block in sectionBlockList:
        if objSecBlk.Name() == block.Name():
          bExist = True
          break
      if bExist is False:
        sectionBlockList.append(objSecBlk)
    else:
      sectionBlockList.append(objSecBlk)
  return sectionBlockList

def IsIncludeOrInputCmdLine(line):
  inputCmd = '\\input{'
  includeCmd = '\\include{'
  if line[:len(inputCmd)] == inputCmd:
    return True
  if line[:len(includeCmd)] == includeCmd:
    return True
  return False

def ParseBlockContentToSectionBlock(sectionBlockList, blockContent, bFilterIncludeCmdLine = True):
  sectionBlock = []
  for line in blockContent:
    if IsSectionName(line) is True:
      sectionBlockList = AddSectionBlockIntoSectionBlockList(sectionBlockList, sectionBlock)
      sectionBlock = []

    #
    # 生成变更的 tex 对应的 section 时得过滤掉 include / input cmd line
    #
    if bFilterIncludeCmdLine is True :
      if IsIncludeOrInputCmdLine(line) is False:
        sectionBlock.append(line)
    else:
      sectionBlock.append(line)

  if len(sectionBlock) > 0 and IsSectionName(sectionBlock[0]) is True:
    sectionBlockList = AddSectionBlockIntoSectionBlockList(sectionBlockList, sectionBlock)
  else:
    print '[E] please check'
    pdb.set_trace()
  return sectionBlockList

def GetCurrentFileParentSectionName(fn, childSectionName):
  if NOTES_CACHE_DIR in fn:
    fn = fn.replace(NOTES_CACHE_DIR, '').strip()

  varDir = None
  if 'main.tex' in fn:
    varDir = '/'.join(fn.split('/')[:-2])
  else:
    varDir = '/'.join(fn.split('/')[:-1])

  parentTex = None
  if len(varDir) > 0:
    parentTex = varDir + '/main.tex'
  else:
    parentTex = NOTES_NAME

  content = None
  with open(parentTex, 'r') as f:
    content = f.readlines()

  includeName = fn.split('.')[0]

  childSectionLevel = GetSectionLevelFromName(childSectionName)

  bFound = False
  parentSectionName = None
  for line in content[::-1]:
    if includeName in line:
      bFound = True
    if bFound is True:
      if IsSectionName(line):
        parentSectionName = line
        if childSectionLevel > GetSectionLevelFromName(parentSectionName):
          break

  return parentSectionName

def ExtractSectionNameListFromContent(contents):
  sectionNameList = []
  for line in contents:
    if IsSectionName(line) is True:
      sectionNameList.append(line)
  return sectionNameList

def GetPararentSectionName(sectionNameList, sectionBlock):
  bFoundCurrent = False
  for sectionName in sectionNameList[::-1]:
    if sectionName == sectionBlock.Name():
      bFoundCurrent = True
    if bFoundCurrent is True:
      level = GetSectionLevelFromName(sectionName)
      # print 'sectionName = ', sectionName,
      # print 'sectionBlock.Name() = ', sectionBlock.Name(),
      # print 'level = ', level,
      # print 'sectionBlock.Level() = ', sectionBlock.Level()
      # print '+++++++++++++++++++++++++++++++++++'
      if level < sectionBlock.Level():
        sectionBlock.SetParent(sectionName)
        sectionBlock.SetIsParentAndChlidInTheSameFile(True)
        break

  if sectionBlock.Parent() is None:
    sectionName = GetCurrentFileParentSectionName(sectionBlock.File(), sectionBlock.Name())
    sectionBlock.SetParent(sectionName)
    sectionBlock.SetIsParentAndChlidInTheSameFile(False)

__metaclass__ = type
class Stack:
  def __init__(self):
    self.m_stack = []
  def Push(self, data):
    self.m_stack.append(data)
  def Pop(self):
    return self.m_stack.pop()
  def GetTop(self):
    return self.m_stack[-1]
  def Empty(self):
    if len(self.m_stack) > 0:
      return False
    return  True

#
#       node
#     /      \
#    /        \
# child(L)  sibling(R)
#
__metaclass__ = type
class DocNode:
  def __init__(self, data, leftNode, rightNode):
    self.m_left = leftNode
    self.m_right = rightNode
    self.m_data = data
  def LeftNode(self):
    return self.m_left
  def RightNode(self):
    return self.m_right
  def Data(self):
    return self.m_data
  def SetLeftNode(self, leftNode):
    self.m_left = leftNode
  def SetRightNode(self, rightNode):
    self.m_right = rightNode

#
# DocTree 只能接受原始目录的 fn
# 即不能接受 /tmp/notes-cache/ 路径的 fn
#
__metaclass__ = type
class DocTree:
  def __init__(self, fn, sectionNameList):
    self.m_root = None
    self.m_sectionNameList = sectionNameList
    self.m_file = fn
  def AddData(self, data):
    if self.m_root is None:
      #
      # 因为 AddData 从 Tex 的第一个 block 开始添加，第一个都是整个文章中最大的 section block
      # 所以只需要 set m_root 节点的时候需要判断 parent , child 是否在同一个文件中
      # 其余的 node 的 parent 都是和自身在同一个文件中的
      #
      if data.IsParentAndChildInTheSameFile() is True:
        parentNodeSectionBlock = SectionBlock(data.Parent())
        parentNodeSectionBlock.SetFile(self.m_file)
        GetPararentSectionName(self.m_sectionNameList, parentNodeSectionBlock)
        self.AddData(parentNodeSectionBlock)
        self.Insert(data, self.m_root)
      else:
        self.m_root = DocNode(data, None, None)
    else:
      self.Insert(data, self.m_root)
  def Insert(self, data, node):
    print 'node = %s, data = %s' % (node.Data().Name().strip(), data.Name()),

    dataParentLevel = GetSectionLevelFromName(data.Parent())
    nodeParentLevel = GetSectionLevelFromName(node.Data().Parent())
    if dataParentLevel == nodeParentLevel:
      if node.RightNode() is None:
        node.SetRightNode(DocNode(data, None, None))
      else:
        self.Insert(data, node.RightNode())
    elif dataParentLevel > nodeParentLevel:
      if node.LeftNode() is None and data.Parent() == node.Data().Name():
        node.SetLeftNode(DocNode(data, None, None))
      elif node.LeftNode() is None and data.Parent() != node.Data().Name():
        if node.RightNode() is None:

          #
          #       node
          #      /
          #  (no child) <- need to insert
          #    /
          # (child)
          #
          if dataParentLevel != node.Data().Level():
            parentNodeSectionBlock = SectionBlock(data.Parent())
            parentNodeSectionBlock.SetFile(self.m_file)
            GetPararentSectionName(self.m_sectionNameList, parentNodeSectionBlock)
            node.SetLeftNode(DocNode(parentNodeSectionBlock, None, None))
            self.Insert(data, node.LeftNode())

          else:
            #
            #          node
            #         /     \
            #  (child)      (no sibling) <- need to insert
            #               /
            #            (child)
            #
            #
            # 到这里不是 root node，所以其 parent 肯定是和 child 在同一个 file 中
            #
            parentNodeSectionBlock = SectionBlock(data.Parent())
            parentNodeSectionBlock.SetFile(self.m_file)
            GetPararentSectionName(self.m_sectionNameList, parentNodeSectionBlock)
            node.SetRightNode(DocNode(parentNodeSectionBlock, None, None))
            self.Insert(data, node.RightNode())
        else:
          self.Insert(data, node.RightNode())
      else:
        self.Insert(data, node.LeftNode())
    else:
      print 'dataParentLevel = ', dataParentLevel
      print 'nodeParentLevel = ', nodeParentLevel
      pdb.set_trace()

  def PreOrder(self, visit):
    stack = Stack()

    node = self.m_root

    while node is not None:
      visit(node)

      if node.RightNode() is not None:
        stack.Push(node.RightNode())

      if node.LeftNode() is not None:
        node = node.LeftNode()
      else:
        if stack.Empty() is True:
          node = None
        else:
          node = stack.Pop()

def NodeVisit(node):
  sectionBlock = node.Data()
  print '--- sectionBlock ---'
  print 'section block fn = ', sectionBlock.File()
  print '[MSG] section level = ', sectionBlock.Level()
  print '[MSG] name = ', sectionBlock.Name(),
  print '[MSG] parent = ', sectionBlock.Parent(),
  #for line in sectionBlock.Content():
  #  print line,
  print '--- sectionBlock ---'

__metaclass__ = type
class Visitor:
  def __init__(self):
    self.m_cache = []
  def Visit(self, node):
    sectionBlock = node.Data()
    self.m_cache.append(sectionBlock.Name())
    if sectionBlock.Content() is not None:
      self.m_cache.append(sectionBlock.Content())

  def Cache(self):
    return self.m_cache

#
# 这个仅仅针对 include cmd 的 merge，所以进行 merge 的处理也比较简单
# 只搜索 contents 中是否包含了 include cmd
#
# Visit() 的过程就实现了 merge 的操作，仅仅针对已经存在的 node 进行 merge
# 不会添加新的 node
#
__metaclass__ = type
class Merger:
  def __init__(self, sectionBlock):
    self.m_sectionBlock = sectionBlock
    self.m_status = False

  def Visit(self, node):
    if self.m_status is True:
      return

    sectionBlock = node.Data()
    if self.m_sectionBlock.Name() == sectionBlock.Name():
      if self.m_sectionBlock.Level() == sectionBlock.Level():
        if self.m_sectionBlock.File() == sectionBlock.File():
          if self.m_sectionBlock.Parent() == sectionBlock.Parent():
            self.m_status = True
            self.Merge(sectionBlock)

  def Merge(self, sectionBlock):
    if self.m_sectionBlock.Content() is not None:
      if sectionBlock.Content() is None:
        sectionBlock.SetContent(self.m_sectionBlock.Content())
      else:
        contentsOld = sectionBlock.Content()
        contentsNew = contentsOld
        for line in self.m_sectionBlock.Content():
          bFound = False
          for old in contentsOld:
            if line == old:
              bFound = True
              break
          if bFound is False:
            #
            # 这里的插入顺序没有保证，如果要保证顺序还需要和原文件进行比较
            #
            contentsNew.append(line)
        sectionBlock.SetContent(contentsNew)

  def MergeStatus(self):
    return self.m_status

def GenDocTreeWithSectionNameListAndSectionBlockList(fn, sectionNameList, sectionBlockList):
  tree = DocTree(fn, sectionNameList)

  for sectionBlock in sectionBlockList:
    # print '--- sectionBlock ---'
    # print 'section block fn = ', sectionBlock.File()
    # print '[MSG] section level = ', sectionBlock.Level()
    # print '[MSG] name = ', sectionBlock.Name(),
    # print '[MSG] parent = ', sectionBlock.Parent(),
    # print '--- sectionBlock ---'
    tree.AddData(sectionBlock)

  # print '==========================='

  return tree

__metaclass__ = type
class DocTreeGenerator:
  def __init__(self, fn):
    self.m_fn = fn
    self.m_oriTex = fn
    if NOTES_CACHE_DIR in fn:
      self.m_oriTex = fn.replace(NOTES_CACHE_DIR + '/', '').strip()

    with open(self.m_fn, 'r') as f:
      self.contents = f.readlines()

    with open(self.m_oriTex) as f:
      self.oriContents = f.readlines()

  def GetSectionBlocksFromContents(self, sectionNameList):
    blockContent = []
    blockContentUnit = []
    for line in self.contents:
      if IsSectionName(line) is True:
        #
        # 只有 section name 一行的，不当作完整的 blockContentUnit
        #
        if len(blockContentUnit) > 1:
          blockContent.extend(blockContentUnit)
        blockContentUnit = []

      blockContentUnit.append(line)

    if len(blockContentUnit) > 1:
      blockContent.extend(blockContentUnit)

    sectionBlockList = []
    sectionBlockList = ParseBlockContentToSectionBlock(sectionBlockList, blockContent, False)

    #
    # update file name
    #
    for sectionBlock in sectionBlockList:
      sectionBlock.SetFile(self.m_oriTex)
      GetPararentSectionName(sectionNameList, sectionBlock)

    return sectionBlockList

  def Gen(self):
    sectionNameList = ExtractSectionNameListFromContent(self.oriContents)
    sectionBlockList = self.GetSectionBlocksFromContents(sectionNameList)

    # print 'sectionNameList = ', sectionNameList

    tree = DocTree(self.m_oriTex, sectionNameList)

    for sectionBlock in sectionBlockList:
      # print '--- sectionBlock ---'
      # print 'section block fn = ', sectionBlock.File()
      # print '[MSG] section level = ', sectionBlock.Level()
      # print '[MSG] name = ', sectionBlock.Name(),
      # print '[MSG] parent = ', sectionBlock.Parent(),
      # print '=== sectionBlock ==='
      tree.AddData(sectionBlock)

    return tree

def ColectSectionBlockAndGenCacheFile(fn):
  content = []
  blockTag = []
  sectionBlockList = []
  sectionNameList = []

  with open(fn, 'r') as f:
    content = f.readlines()

  (_, status) = commands.getstatusoutput("git diff %s" % fn)
  for line in status.split('\n'):
    if '@@ ' in line:
      #print 'line = ', line
      blockTag.append(line.split(' ')[2])

  #print 'blockTag = ', blockTag
  for tag in blockTag:
    blockContent = GetBlockContentFromGitDiffStatus(tag, content)
    sectionBlockList = ParseBlockContentToSectionBlock(sectionBlockList, blockContent)

  #print "len(sectionBlockList) = ", len(sectionBlockList)

  sectionNameList = ExtractSectionNameListFromContent(content)

  print '---------------------------'
  for sectionName in sectionNameList:
    print sectionName,
  print '---------------------------'

  #
  # update file name
  #
  for sectionBlock in sectionBlockList:
    sectionBlock.SetFile(fn)
    GetPararentSectionName(sectionNameList, sectionBlock)

  docTree = GenDocTreeWithSectionNameListAndSectionBlockList(fn, sectionNameList, sectionBlockList)

  docTree.PreOrder(NodeVisit)

  visitor = Visitor()

  docTree.PreOrder(visitor.Visit)

  return visitor.Cache()

def GenCacheFile(cacheMap):
  #
  # 1> for cacheMap['added']
  #
  for fn in cacheMap['added']:
    dstDir = NOTES_CACHE_DIR + '/' + '/'.join(fn.split('/')[0:-1])
    os.system('cp %s %s' % (fn, dstDir))

  #
  # 2> for cacheMap['modified']
  #
  for fn in cacheMap['modified']:
    cache = ColectSectionBlockAndGenCacheFile(fn)

    dstFn = NOTES_CACHE_DIR + '/' + fn
    with open(dstFn, 'w') as f:
      for line in cache:
        f.writelines(line)

__metaclass__ = type
class ParentCacheGenerator:
  def __init__(self, child):
    self.m_child = child
    self.m_parent = None
    self.m_sectionNameList = None
    self.Gen()

    if self.m_parent is not None:
      ParentCacheGenerator(self.m_parent)

  def GetParentTexName(self, child):
    parent = None

    #
    # m_child = languages/c++/basic/main.tex
    # parent -> languages/c++/main.tex
    # m_child = windows/software/vscode.tex
    # parent -> windows/software/main.tex
    # m_child = notes.tex
    # parent -> None
    # m_child = linux/gdb.tex
    # parent -> linux/main.tex
    # m_child = linux/main.tex
    # parent -> notes.tex
    #

    if NOTES_NAME != child:
      if 'main.tex' in child:
        parent = '/'.join(child.split('/')[:-2])
      else:
        parent = '/'.join(child.split('/')[:-1])

      if len(parent) == 0:
        parent = NOTES_NAME
      elif len(parent) > 0:
        parent = parent + '/' + 'main.tex'

    return parent

  def GetFirstSectionName(self, fn):
    with open(fn, 'r') as f:
      for line in f:
        if IsSectionName(line) is True:
          return line
    return None

  def GetSectionBlockOfIncludeCmd(self, oriParentTex, child):
    includeCmd = child.split('.')[0]
    childSectionName = self.GetFirstSectionName(child)
    parentSectionName = GetCurrentFileParentSectionName(child, childSectionName)

    contents = None
    with open(oriParentTex, 'r') as f:
      contents = f.readlines()
      for line in contents:
        if includeCmd in line:
          includeCmd = line
          break

    print 'child = ', child
    print 'includeCmd = ', includeCmd
    self.m_sectionNameList = ExtractSectionNameListFromContent(contents)

    sectionBlock = SectionBlock(parentSectionName)
    sectionBlock.SetFile(oriParentTex)
    sectionBlock.SetContent([includeCmd])
    GetPararentSectionName(self.m_sectionNameList, sectionBlock)

    # print '--- sectionBlock ---'
    # print 'parent section block fn = ', sectionBlock.File()
    # print '[MSG] section level = ', sectionBlock.Level()
    # print '[MSG] name = ', sectionBlock.Name(),
    # print '[MSG] parent = ', sectionBlock.Parent(),
    # for line in sectionBlock.Content():
    #   print '[CTT]', line,
    # print '--- sectionBlock ---'

    return sectionBlock

  def IsExistIncludeCmdCheck(self, cacheParentTex, sectionBlockOfIncludeCmd):
    bExist = False

    with open(cacheParentTex, 'r') as f:
      contents = f.readlines()
      for line in contents:
        if sectionBlockOfIncludeCmd.Content()[0] in line:
          bExist = True
          break

    return bExist

  def GenParentContent(self, oriParentTex, child):

    cacheParentTex = NOTES_CACHE_DIR + '/' + oriParentTex

    #
    # 1> 生成包含当前 child 的 include cmd 的 section
    # 2> 生成 cacheParentTex 的 DocTree
    # 3> 将 section 合并到 DocTree
    # 4> DocTree -> file content
    #

    print 'call GenParentContent() step 1'
    sectionBlockOfIncludeCmd = self.GetSectionBlockOfIncludeCmd(oriParentTex, child)

    docTree = None
    if os.path.exists(cacheParentTex) is True:
      print 'call GenParentContent() step 2'
      print 'cacheParentTex = ', cacheParentTex
      docTree = DocTreeGenerator(cacheParentTex).Gen()

      print 'call GenParentContent() step 3'
      if self.IsExistIncludeCmdCheck(cacheParentTex, sectionBlockOfIncludeCmd) is False:
        #
        # merge 过了就不需要再 tree.AddData()
        #
        merger = Merger(sectionBlockOfIncludeCmd)
        docTree.PreOrder(merger.Visit)
        if merger.MergeStatus() is False:
          docTree.AddData(sectionBlockOfIncludeCmd)
    else:
      docTree = DocTree(oriParentTex, self.m_sectionNameList)
      docTree.AddData(sectionBlockOfIncludeCmd)

    print 'call GenParentContent() step 4'
    visitor = Visitor()
    docTree.PreOrder(visitor.Visit)
    return  visitor.Cache()

  def Gen(self):
    print 'm_child = ', self.m_child
    parent = self.GetParentTexName(self.m_child)
    print 'parent = ', parent

    self.m_parent = parent

    if parent is None:
      return

    oriParentTex = parent
    cacheParentTex = NOTES_CACHE_DIR + '/' + parent
    print '<%s, %s>' % (oriParentTex, cacheParentTex)

    parentContent = self.GenParentContent(oriParentTex, self.m_child)

    if os.path.exists(cacheParentTex) is True:
      os.system('rm -f %s' % cacheParentTex)

    with open(cacheParentTex, 'w') as f:
      for line in parentContent:
        f.writelines(line)

def GenOrUpdateParentCacheFile(cacheMap):
  for fn in cacheMap['modified']:
    ParentCacheGenerator(fn)

  # print
  # print '*****************************************'
  # print
  for fn in cacheMap['added']:
    # print 'fn = ', fn
    ParentCacheGenerator(fn)
    # print
    # print '00000000000000000000000000000000000'
    # print


def CompleteCacheNotes():
  target = NOTES_CACHE_DIR + '/' + NOTES_NAME
  if os.path.exists(NOTES_CACHE_DIR) is False:
      exit(-1)

  if os.path.exists(target) is False:
    print '[E] no found ', target
    pdb.set_trace()

  contents = []
  with open(NOTES_NAME, 'r') as f:
    for line in f:
      contents.append(line)
      if '\\tableofcontents' in line:
        break

  contents.append('\n')
  with open(target, 'r') as f:
    contents.extend(f.readlines())

  contents.append('\n')
  contents.append('\\end{sloppypar}\n')
  contents.append('\\end{document}\n')
  contents.append('\n')

  if os.path.exists(target) is True:
    os.system('rm -f %s' % target)

  with open(target, 'w') as f:
    for line in contents:
      f.writelines(line)

def CopyImagesToCacheDir():
  fileList = CollectCacheFilesOfDir(NOTES_CACHE_DIR)
  imageList = []
  for file in fileList:
    with open(file, 'r') as f:
      for line in f:
        if '\includegraphics' in line:
          image = line.strip().split(']{')[1].strip('}').strip()
          imageList.append(image)

  if len(imageList) > 0:
    if os.path.exists(NOTES_CACHE_DIR + '/images') is False:
      os.system('mkdir %s/images' % NOTES_CACHE_DIR)

    for image in imageList:
      os.system('cp -r %s %s/images' % (image, NOTES_CACHE_DIR))

#
# 1> gen cache files to /tmp/notes-cache/
#

#
# cacheMap =
# {
#  'deleted':  ['windows/config.tex'],
#  'added':    ['linux/linux-directory.tex'],
#  'modified': ['languages/python/basic.tex', 'languages/shell/program.tex', 'linux/main.tex']
# }
#
cacheMap = CollectNeedCacheFiles()
print 'cacheMap = \n', cacheMap
if len(cacheMap['added']) == 0 and len(cacheMap['modified']) == 0:
  os.system('rm -rf %s' % NOTES_CACHE_DIR)
  print 'clean and remove %s' % NOTES_CACHE_DIR
  exit(-1)

PrepareCacheDirs(cacheMap)
GenCacheFile(cacheMap)
GenOrUpdateParentCacheFile(cacheMap)

#
# 2> complete /tmp/notes-cache/notes.tex
#
CompleteCacheNotes()

#
# 3> copy images to /tmp/notes-cache/
#
CopyImagesToCacheDir()

#
# 4> copy title
#
os.system('cp -r title %s' % NOTES_CACHE_DIR)


