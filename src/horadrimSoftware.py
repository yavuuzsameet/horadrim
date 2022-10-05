import os
import os.path
import time
import sys

# Important note: This B+ tree structure defined by the Node class and BPlusTree class are taken from the internet.
# Here is a link to the original github repo of the mentioned structure from the owner of this code segment.
# https://gist.github.com/savarin/69acd246302567395f65ad6b97ee503d 
class Node(object):
    """Base node object.
    Each node stores keys and values. Keys are not unique to each value, and as such values are
    stored as a list under each key.
    Attributes:
        order (int): The maximum number of keys each node can hold.
    """
    def __init__(self, order):
        """Child nodes can be converted into parent nodes by setting self.leaf = False. Parent nodes
        simply act as a medium to traverse the tree."""
        self.order = order
        self.keys = []
        self.values = []
        self.leaf = True

    def add(self, key, value):
        """Adds a key-value pair to the node."""
        # If the node is empty, simply insert the key-value pair.
        if not self.keys:
            self.keys.append(key)
            self.values.append([value])
            return None

        for i, item in enumerate(self.keys):
            # If new key matches existing key, add to list of values.
            if key == item:
                self.values[i].append(value)
                break

            # If new key is smaller than existing key, insert new key to the left of existing key.
            elif key < item:
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break

            # If new key is larger than all existing keys, insert new key to the right of all
            # existing keys.
            elif i + 1 == len(self.keys):
                self.keys.append(key)
                self.values.append([value])

    def split(self):
        """Splits the node into two and stores them as child nodes."""
        left = Node(self.order)
        right = Node(self.order)
        mid = self.order // 2

        left.keys = self.keys[:mid]
        left.values = self.values[:mid]

        right.keys = self.keys[mid:]
        right.values = self.values[mid:]

        # When the node is split, set the parent key to the left-most key of the right child node.
        self.keys = [right.keys[0]]
        self.values = [left, right]
        self.leaf = False

    def is_full(self):
        """Returns True if the node is full."""
        return len(self.keys) == self.order

    def show(self, counter=0):
        """Prints the keys at each level."""

        # Recursively print the key of child nodes (if these exist).
        if not self.leaf:
            for item in self.values:
                item.show(counter + 1)

class BPlusTree(object):
    """B+ tree object, consisting of nodes.
    Nodes will automatically be split into two once it is full. When a split occurs, a key will
    'float' upwards and be inserted into the parent node to act as a pivot.
    Attributes:
        order (int): The maximum number of keys each node can hold.
    """
    def __init__(self, order=8):
        self.root = Node(order)
        self.keyList = []

    def _find(self, node, key):
        """ For a given node and key, returns the index where the key should be inserted and the
        list of values at that index."""
        for i, item in enumerate(node.keys):
            if key < item:
                return node.values[i], i

        return node.values[i + 1], i + 1

    def _merge(self, parent, child, index):
        """For a parent and child node, extract a pivot from the child to be inserted into the keys
        of the parent. Insert the values from the child into the values of the parent.
        """
        parent.values.pop(index)
        pivot = child.keys[0]

        for i, item in enumerate(parent.keys):
            if pivot < item:
                parent.keys = parent.keys[:i] + [pivot] + parent.keys[i:]
                parent.values = parent.values[:i] + child.values + parent.values[i:]
                break

            elif i + 1 == len(parent.keys):
                parent.keys += [pivot]
                parent.values += child.values
                break

    def insert(self, key, value, type = ""):
        """Inserts a key-value pair after traversing to a leaf node. If the leaf node is full, split
        the leaf node into two.
        """
        parent = None
        child = self.root

        # Traverse tree until leaf node is reached.
        while not child.leaf:
            parent = child
            child, index = self._find(child, key)

        child.add(key, value)
        self.keyList.append(key)
        
        if type == "str" or type == "":
            self.keyList.sort()
        elif type == "int":
            self.keyList.sort(key = int)

        # If the leaf node is full, split the leaf node into two.
        if child.is_full():
            child.split()

            # Once a leaf node is split, it consists of a internal node and two leaf nodes. These
            # need to be re-inserted back into the tree.
            if parent and not parent.is_full():
                self._merge(parent, child, index)

    def retrieve(self, key):
        """Returns a value for a given key, and None if the key does not exist."""
        child = self.root

        while not child.leaf:
            child, index = self._find(child, key)

        for i, item in enumerate(child.keys):
            if key == item:
                return child.values[i]

        return None

    def show(self):
        """Prints the keys at each level."""
        self.root.show()

    def returnMatchingKeys(self,condition,type=""):
        
        valueToCheck= "",""
        
        if "=" in condition:
            valueToCheck = condition.split("=")[1]
            data = self.retrieve(valueToCheck)
            if data == None:
                return []
            else:
                return [valueToCheck]

        elif "<" in condition:
            valueToCheck = condition.split("<")[1]
            matchingKeys = []
            for key in self.keyList:
                if type == "str" or type == "":
                    if key < valueToCheck:
                        matchingKeys.append(key)
                else:
                    if int(key) < int(valueToCheck):
                        matchingKeys.append(key)
            return matchingKeys
        
        elif ">" in condition:
            valueToCheck = condition.split(">")[1]
            matchingKeys = []
            for key in self.keyList[::-1]:
                if type == "str" or type == "":
                    if key > valueToCheck:
                        matchingKeys.append(key)
                else:
                    if int(key) > int(valueToCheck):
                        matchingKeys.append(key)
            return matchingKeys[::-1]

PAGES_PER_FILE = 3
RECORDS_PER_PAGE = 10
PAGE_SIZE = 2410 + 90 #(12*20+1)*10 + (89 + 1)

outFile = open(sys.argv[2],'w')
logFile = open('horadrimLog.csv', 'a')
inputFile = open(sys.argv[1])

dir_list = os.listdir(os.getcwd())

types_list = []
for l in dir_list:
    if 'types' in l:
        types_list.append(l)

records_list = []
for r in dir_list:
    if 'records' in r:
        records_list.append(r)


def log(line, succession):
    logFile.write(str(int(time.time())) + ',' + line + ',' + succession + '\n')

def whichOperation(tokens):
    if tokens[0] == 'create':
        if tokens[1] == 'type':
            return 1
        elif tokens[1] == 'record':
            return 4

    elif tokens[0] == 'delete':
        if tokens[1] == 'type':
            return 2
        elif tokens[1] == 'record':
            return 5

    elif tokens[0] == 'list':
        if tokens[1] == 'type':
            return 3
        elif tokens[1] == 'record':
            return 8
    
    elif tokens[0] == 'update':
        return 6

    elif tokens[0] == 'search':
        return 7

    elif tokens[0] == 'filter':
        return 9

def deleteRecord(data):
    file,pageNo,record = data.split(":")[0],int(data.split(":")[1]),int(data.split(":")[2])

    deleteFromFile = open(file,'r+')

    for i in range(pageNo):
        page = deleteFromFile.read(PAGE_SIZE)
    header = page.split("\n")[0]
    recordNo = header.split(",")[2].split(":")[1]
    newRecordNo = str(int(recordNo) - 1)

    emptySpots = header.split(",")[1].split(":")[1].split("-")
    if emptySpots == [""]:
        emptySpots = []
    emptySpots.append(str(record))
    emptySpots.sort(key=int)
    newEmptySpots = "-".join(emptySpots)

    newHeader = ("PAGE:"+str(pageNo)+",Empty:" + newEmptySpots +",Records:"+newRecordNo).ljust(89," ") + "\n"
    lineToAdd = " ".ljust(240," ")+"\n"

    deleteFromFile.seek((pageNo-1)*(PAGE_SIZE+11))
    deleteFromFile.write(newHeader)
    deleteFromFile.seek((pageNo-1)*(PAGE_SIZE+11) + (91) + (record-1)*242)
    deleteFromFile.write(lineToAdd)
    deleteFromFile.flush()   
    deleteFromFile.close()

    removeFileIfEmpty(file)               

def searchTypes(typeName):
    for file in types_list:
        findPlace = open(file,'r')
        for i in range(PAGES_PER_FILE):
            page = findPlace.read(PAGE_SIZE)
            if page != "":            
                recordsInPage = page.split("\n")
                pageNo = recordsInPage[0].split(",")[0].split(":")[1]
                for record in recordsInPage:
                    if record:
                        if typeName == record.split(" ")[1]:
                            recordNo = record.split(" ")[0]
                            primaryKeyOrder = record.split(" ")[2]
                            return [pageNo,recordNo,primaryKeyOrder,record,file]
    return -1

def findTypeFile():
    for file in types_list:
        findFile = open(file,'r')
        for i in range(PAGES_PER_FILE):
            findFile.seek(i*(PAGE_SIZE+11))
            header = findFile.readline()
            recordNo = header.split(",")[2].split(":")[1]
            if int(recordNo) < 10:
                return file

    return createNewFile('type')

def findRecordFile():
    for file in records_list:
        findFile = open(file,'r')
        for i in range(PAGES_PER_FILE):
            findFile.seek(i*(PAGE_SIZE+11))
            header = findFile.readline()
            recordNo = header.split(",")[2].split(":")[1]
            if int(recordNo) < 10:
                return file

    return createNewFile('record')

def createNewFile(method):
    filename = ''

    if method == 'type':
        filename = 'types' + str(len(types_list)+1) + '.txt'
        for i in range(len(types_list)):
            filenamecheck = 'types'+str(i+1)+'.txt'
            if filenamecheck not in types_list:
                filename = filenamecheck

        types_list.append(filename)

    elif method == 'record':
        filename = 'records' + str(len(records_list)+1) + '.txt'
        for i in range(len(records_list)):
            filenamecheck = 'records'+str(i+1)+'.txt'
            if filenamecheck not in records_list:
                filename = filenamecheck

        records_list.append(filename)

    file = open(filename, 'a')
    fileContent = ""
    for i in range(PAGES_PER_FILE):
        pageHeader = ("PAGE:"+str(i+1) +",Empty:1-2-3-4-5-6-7-8-9-10,Records:0").ljust(89," ") + "\n"
        fileContent = fileContent + pageHeader
        for j in range(10):
            fileContent = fileContent + " ".ljust(240," ") + "\n"
    file.write(fileContent)
    file.flush()
    file.close()

    return filename

def removeFileIfEmpty(filename):
    file = open(filename, 'r')
    for i in range(PAGES_PER_FILE):
        file.seek(i*(PAGE_SIZE+11))
        header = file.readline()
        recordNo = header.split(",")[2].split(":")[1]
        if int(recordNo) != 0:
            return 'file is not empty'
    if 'types' in filename:
        types_list.remove(filename)
    elif 'records' in filename: 
        records_list.remove(filename)
    file.close()
    os.remove(filename)
    
for line in inputFile:
    line = line.strip()
    if not line:
        continue

    tokens = line.split()
    type = whichOperation(tokens) 

    if type ==1 :
        if len(types_list) == 0:
            typeFile = open('types1.txt', 'a')
            types_list.append('types1.txt')
            fileContent = ""
            for i in range(PAGES_PER_FILE):
                pageHeader = ("PAGE:"+str(i+1) +",Empty:1-2-3-4-5-6-7-8-9-10,Records:0").ljust(89," ") + "\n"
                fileContent = fileContent + pageHeader
                for j in range(10):
                    fileContent = fileContent + " ".ljust(240," ") + "\n"
            typeFile.write(fileContent)
            typeFile.flush()
            typeFile.close()

        typeName = tokens[2]

        searchResult = searchTypes(typeName)

        if  searchResult != -1:
            log(line, 'failure')
            continue

        if not os.path.exists('B+'+typeName+'.txt'):
            bTreeFile = open('B+'+typeName+'.txt','a')
            bTreeFile.close()

        fieldNo = int(tokens[3])
        primaryKeyOrder = tokens[4]
        primaryKey = tokens[4 + 2*int(tokens[4])-1]
        primaryKeyType = tokens[4 + 2*int(tokens[4])]

        #Note in typeInf primary key is the first field.
        typeInf = typeName + " " + primaryKeyOrder + " " +primaryKey + " " + primaryKeyType
        for i in range(fieldNo):
            if tokens[5+2*i] != primaryKey:
                typeInf = typeInf +" " + tokens[5+2*i] + " " +tokens[6+2*i]
        

        #Find a place to insert new type info
        availableTypeFile = findTypeFile()
        findPlace = open(availableTypeFile,'r+')

        for i in range(PAGES_PER_FILE):
            page = findPlace.read(PAGE_SIZE)
            header = page.split("\n")[0]
            pageNo = header.split(",")[0].split(":")[1]
            recordNo = header.split(",")[2].split(":")[1]
            if recordNo.strip() == "10":
                continue
            
            emptySpots = header.split(",")[1].split(":")[1].split("-")
            firstEmptySpot = emptySpots[0]
            emptySpots.remove(firstEmptySpot)
            newEmptySpots = "-".join(emptySpots)
            newRecordNo = str(int(recordNo) + 1)
            newHeader = ("PAGE:" +str(i+1)+",Empty:" + newEmptySpots +",Records:"+newRecordNo).ljust(89," ") +"\n"
            lineToAdd = (firstEmptySpot +" " + typeInf).ljust(240," ") + "\n"

            findPlace.seek(i*(PAGE_SIZE+11))
            findPlace.write(newHeader)
            findPlace.seek(i*(PAGE_SIZE+11) + (91) + (int(firstEmptySpot)-1)*242)
            findPlace.write(lineToAdd)
            findPlace.flush()
            findPlace.close()
            
            break

    elif type == 2:
        typeToDelete = tokens[2]

        results = searchTypes(typeToDelete)

        if  results == -1:
            log(line, 'failure')
            continue

        else: 
            pageNo, recordIndex, fileName = results[0], results[1], results[4]
            findPlace = open(fileName,'r+')


            findPlace.seek((int(pageNo)-1)*(PAGE_SIZE+11))
            header = findPlace.readline()
            recordNo = header.split(",")[2].split(":")[1]
            newRecordNo = str(int(recordNo) - 1)

            #file silme durumunu ayarla
            emptySpots = header.split(",")[1].split(":")[1].split("-")
            
            if emptySpots == [""]:
                emptySpots = []
            emptySpots.append(recordIndex)
            emptySpots.sort(key=int)
            newEmptySpots = "-".join(emptySpots)

            newHeader = ("PAGE:"+ pageNo+",Empty:" + newEmptySpots +",Records:"+newRecordNo).ljust(89," ") + "\n"
            lineToAdd = " ".ljust(240," ")+"\n"

            findPlace.seek((int(pageNo)-1)*(PAGE_SIZE+11))
            findPlace.write(newHeader)
            findPlace.seek((int(pageNo)-1)*(PAGE_SIZE+11) + (91) + (int(recordIndex)-1)*242)
            findPlace.write(lineToAdd)
            findPlace.flush()
            findPlace.close()   

            ###CHECK IF THE TYPE FILE ALL EMPTIED
            removeFileIfEmpty(fileName)
                          
        #ALL RECORDS OF THIS TYPE SHOULD BE DELETED
        bplustree = BPlusTree(order=4)

        # primaryKeyOrder = results[2]
        # primaryKey = tokens[2+int(primaryKeyOrder)]

        if os.path.exists("B+"+typeToDelete+".txt"):

            readLines = open("B+"+typeToDelete+".txt",'r')
            while True:
                tree_line = readLines.readline()
                if not tree_line:
                    break
                bplustree.insert(tree_line.split("-")[0],tree_line.split("-")[1])
            readLines.close()
        else:
            log(line, 'failure')
            continue

        keys = bplustree.keyList
        for key in keys:
            data = data = bplustree.retrieve(key)[0][:-1]
            deleteRecord(data)
        os.remove("B+"+typeToDelete+".txt")
                
    elif type == 3:
        results = []
        for file in types_list:
            findPlace = open(file,'r')
            for i in range(PAGES_PER_FILE):
                page = findPlace.read(PAGE_SIZE)
                if page != "":            
                    recordsInPage = page.split("\n")
                    for record in recordsInPage:
                        if record.strip() != "":
                            if record.split(" ")[1]:
                                results.append(record.split(" ")[1])

        if len(results) == 0: 
            log(line, 'failure')
            continue

        results.sort()
        for type in results:
            outFile.write(type)
            outFile.write("\n")
            outFile.flush()

        findPlace.close()

    elif type == 4:
        if len(records_list) == 0:
            recordFile = open('records1.txt', 'a')
            records_list.append('records1.txt')
            fileContent = ""
            for i in range(PAGES_PER_FILE):
                pageHeader = ("PAGE:"+str(i+1) +",Empty:1-2-3-4-5-6-7-8-9-10,Records:0").ljust(89," ") + "\n"
                fileContent = fileContent + pageHeader
                for j in range(10):
                    fileContent = fileContent + " ".ljust(240," ") + "\n"
            recordFile.write(fileContent)
            recordFile.flush()
            recordFile.close()

        typeName = tokens[2]

        if searchTypes(typeName) == -1:
            log(line, 'failure')
            continue

        primaryKeyOrder = searchTypes(typeName)[2]
        primaryKey = tokens[2+int(primaryKeyOrder)] 

        bplustree = BPlusTree(order=4)
        
        if os.path.exists("B+"+typeName+".txt"):
            readLines = open("B+"+typeName+".txt",'r')
            while True:
                tree_line = readLines.readline()
                if not tree_line:
                    break
                bplustree.insert(tree_line.split("-")[0],tree_line.split("-")[1])
            readLines.close()

            if bplustree.retrieve(primaryKey) != None:
                log(line, 'failure')
                continue

        else:
            log(line, 'failure')
            continue

        recordInfo = typeName
        for token in tokens[3:]:
            recordInfo = recordInfo + " " + token
        
        #Find a place to insert new record info
        availableRecordFile = findRecordFile()
        findPlace = open(availableRecordFile,'r+')

        for i in range(PAGES_PER_FILE):
            page = findPlace.read(PAGE_SIZE)
            header = page.split("\n")[0]
            pageNo = header.split(",")[0].split(":")[1]
            recordNo = header.split(",")[2].split(":")[1]
            
            if recordNo.strip() == "10":
                continue

            emptySpots = header.split(",")[1].split(":")[1].split("-")
            firstEmptySpot = emptySpots[0]
            emptySpots.remove(firstEmptySpot)
            newEmptySpots = "-".join(emptySpots)
            newRecordNo = str(int(recordNo) + 1)
            newHeader = ("PAGE:" +str(i+1)+",Empty:" + newEmptySpots +",Records:"+newRecordNo).ljust(89," ") + "\n"
            lineToAdd = (firstEmptySpot +" " + recordInfo).ljust(240," ") + "\n"

            findPlace.seek(i*(PAGE_SIZE+11))
            findPlace.write(newHeader)
            findPlace.seek(i*(PAGE_SIZE+11) + (91) + (int(firstEmptySpot)-1)*242)
            findPlace.write(lineToAdd)
            findPlace.flush()
            findPlace.close()

            bTreeUpdate = open("B+"+typeName+".txt",'a')
            bTreeUpdate.write(primaryKey+"-"+availableRecordFile+':'+str(i+1)+":"+firstEmptySpot+"\n")
            bTreeUpdate.close()
            break

    elif type == 5:

        typeName = tokens[2]
        bplustree = BPlusTree(order=4)
        primaryKey = tokens[3]

        if os.path.exists("B+"+typeName+".txt"):
            newBTreeIfKeyExists = ""
            readLines = open("B+"+typeName+".txt",'r')
            while True:
                tree_line = readLines.readline()

                if tree_line.split("-")[0] != primaryKey:
                    newBTreeIfKeyExists = newBTreeIfKeyExists + tree_line

                if not tree_line:
                    break
                bplustree.insert(tree_line.split("-")[0],tree_line.split("-")[1])
            readLines.close()

            if bplustree.retrieve(primaryKey) == None:
                log(line, 'failure')
                continue
            #new b+ file with record removed
            else:
                writeLines = open("B+"+typeName+".txt",'w')
                writeLines.write(newBTreeIfKeyExists)
                writeLines.close()
            
        else:
            log(line, 'failure')
            continue
        
        data = bplustree.retrieve(primaryKey)[0][:-1]
        deleteRecord(data)
    
    elif type == 6:
        typeName = tokens[2]
        bplustree = BPlusTree(order=4)
        primaryKey = tokens[3]

        if os.path.exists("B+"+typeName+".txt"):
            readLines = open("B+"+typeName+".txt",'r')
            while True:
                tree_line = readLines.readline()

                if not tree_line:
                    break
                bplustree.insert(tree_line.split("-")[0],tree_line.split("-")[1])
            readLines.close()

            if bplustree.retrieve(primaryKey) == None:
                log(line, 'failure')
                continue
        else:
            log(line, 'failure')
            continue

        data = bplustree.retrieve(primaryKey)[0][:-1]
        file,pageNo,record = data.split(":")[0],data.split(":")[1],data.split(":")[2]

        #Bu primary key hep birinci mi yoksa type a bağlı mı öğren.

        updatedInfo = typeName
        for token in tokens[4:]:
            updatedInfo = updatedInfo + " " + token

        updateFile = open(file,'r+')

        lineToAdd =(record + " " +updatedInfo).ljust(240," ") +"\n"
        updateFile.seek((int(pageNo)-1)*(PAGE_SIZE+11) + (91) + (int(record)-1)*242)
        updateFile.write(lineToAdd)
        updateFile.flush()
        updateFile.close()  
       
    elif type == 7:
       
        typeName = tokens[2]
        bplustree = BPlusTree(order=4)
        primaryKey = tokens[3]

        if os.path.exists("B+"+typeName+".txt"):
            readLines = open("B+"+typeName+".txt",'r')
            
            while True:
                tree_line = readLines.readline()
                if not tree_line:
                    break
                bplustree.insert(tree_line.split("-")[0],tree_line.split("-")[1])
            readLines.close()

            if bplustree.retrieve(primaryKey) == None:
                log(line, 'failure')
                continue
        else:
            log(line, 'failure')
            continue

        data = bplustree.retrieve(primaryKey)[0][:-1]
        file,pageNo,record = data.split(":")[0],data.split(":")[1],data.split(":")[2]

        findPlace = open(file,'r+')

        findPlace.seek((int(pageNo)-1)*(PAGE_SIZE+11) + (91) + (int(record)-1)*242)
        searchedRecord= findPlace.readline().strip()

        findPlace.close()

        searchedRecord = " ".join(searchedRecord.split(" ")[2:])
        outFile.write(searchedRecord)
        outFile.write("\n")
        outFile.flush()
    
    elif type == 8:
        typeName = tokens[2]
        bplustree = BPlusTree(order=4)

        if os.path.exists("B+"+typeName+".txt"):
            readLines = open("B+"+typeName+".txt",'r')
            while True:
                tree_line = readLines.readline()
                if not tree_line:
                    break
                bplustree.insert(tree_line.split("-")[0],tree_line.split("-")[1])  
            readLines.close()

        else:
            log(line, 'failure')
            continue

        if searchTypes(typeName) == -1:
            log(line, 'failure')
            continue

        typeInformation = searchTypes(typeName)[3].split(" ")
        primaryKeyType = typeInformation[4]
        primaryKeyOrder = int(typeInformation[2])
        keys = bplustree.keyList
        results = []

        for key in keys:
            data = bplustree.retrieve(key)[0][:-1]
            file,pageNo,record = data.split(":")[0],data.split(":")[1],data.split(":")[2]

            findPlace = open(file,'r+')
            findPlace.seek((int(pageNo)-1)*(PAGE_SIZE+11) + (91) + (int(record)-1)*242)
            searchedRecord = findPlace.readline().strip()
            searchedRecord = " ".join(searchedRecord.split(" ")[2:])
            
            result = searchedRecord
            results.append(result)
            findPlace.close()
        
        if len(results)==0:
            log(line, 'failure')
            continue

        if primaryKeyType == "str":
            results.sort(key=lambda x:x[primaryKeyOrder-1])
        else:
            results.sort(key=lambda x: int(x[primaryKeyOrder-1]) )
        
        for result in results:
            outFile.write(result)
            outFile.write("\n")
            outFile.flush()
    
    elif type == 9:

        typeName = tokens[2]
        bplustree = BPlusTree(order=4)
        condition = tokens[3]

        if not os.path.exists("B+"+typeName+".txt"):
            log(line, 'failure')
            continue
            
        typeInformation = searchTypes(typeName)[3]
        fieldType = typeInformation.split(" ")[4]

        readLines = open("B+"+typeName+".txt",'r')
        while True:
            tree_line = readLines.readline()
            if not tree_line:
                break
            bplustree.insert(tree_line.split("-")[0],tree_line.split("-")[1],fieldType) 
        readLines.close()
        

        keys = bplustree.returnMatchingKeys(condition,fieldType)
        results = []

        for key in keys:

            data = bplustree.retrieve(key)[0][:-1]
            file,pageNo,record = data.split(":")[0],data.split(":")[1],data.split(":")[2]

            findPlace = open(file,'r+')
            findPlace.seek((int(pageNo)-1)*(PAGE_SIZE+11) + (91) + (int(record)-1)*242)
            filteredRecord = findPlace.readline().strip()
            filteredRecord = filteredRecord.split(" ")[2:]
            results.append(filteredRecord)
            findPlace.close()

        if len(results) == 0:
            log(line, 'failure')
            continue

        for result in results:
            outFile.write(" ".join(result))
            outFile.write("\n")
            outFile.flush()

    log(line, 'success')

outFile.close()
logFile.close()