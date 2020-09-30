#Safa Burak Altunel
#2017400207

import argparse
import os

#parsing inputs
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-r", action = "store_true") # record
group.add_argument("-t",action = "store_true")  # type
parser.add_argument("-l",action = "store_true") # list
parser.add_argument("-s",action = "store_true") # search
parser.add_argument("-c",action = "store_true") # create
parser.add_argument("-d",action = "store_true") # delete
parser.add_argument("inputs",nargs = '*', default = [])
args = parser.parse_args()

# Helper Functions

def fit11bytes(num): # type(num) = int
	return str(num).zfill(11)

def fit12bytes(str):
	while len(str) < 12:
		str = str + "!"
	return str

def getNumberOfFields(typeName):
	systemCatalog = open("systemCatalog.txt","r")
	pageNumber = 0
	fileSize = os.stat("systemCatalog.txt").st_size
	while pageNumber*1024 <= fileSize:
		systemCatalog.seek(pageNumber*1024)
		pageRange = 0
		if fileSize - pageNumber*1024 <= fileSize:
			pageRange = 1024
		else:
			pageRange = fileSize - pageNumber*1024
		page = systemCatalog.read(pageRange)
		i = 12
		while i < len(page):
			if page[i:i+12] == typeName and page[i + 13] != 0:
				systemCatalog.close()
				return page[i+12]
			i = i + 86
		pageNumber = pageNumber + 1

def extractTypeName(name):
	ans = ""
	i = 0
	while name[i] != "!":
		ans = ans + name[i]
		i = i+1
	return ans


# DDL Operations

def createType():
	typeName = fit12bytes(args.inputs[0])
	numberOfFields = int(args.inputs[1])
	fieldNames = []
	for i in range(numberOfFields):
		fieldName = fit12bytes(args.inputs[i+2])
		fieldNames.append(fieldName)

	for i in range(numberOfFields, 6):
		fieldNames.append(fit12bytes("NULL"))

	with open("systemCatalog.txt","r+") as systemCatalog:
		pageNumber = 0
		fileSize = os.stat("systemCatalog.txt").st_size
		while pageNumber*1024 <= fileSize:
			systemCatalog.seek(pageNumber*1024) # point cursor to the head of the page
			pageRange = 0
			if fileSize - pageNumber*1024 >= 1024:
				pageRange = 1024
			else:
				pageRange = fileSize - pageNumber*1024
			page = systemCatalog.read(pageRange)
			if len(page) == 0: # the page is empty
				systemCatalog.seek(pageNumber*1024)
				# filling the page header
				systemCatalog.write("1") # numberOfRecords will be 1 after inserting the first record
				systemCatalog.write(fit11bytes(pageNumber + 1))

				# filling the record header
				systemCatalog.write(typeName)
				systemCatalog.write(str(numberOfFields))
				systemCatalog.write("1") # isOccupied info

				# inserting field names
				for fieldName in fieldNames:
					systemCatalog.write(fit12bytes(fieldName))

				f = open(args.inputs[0] + ".txt", "w+")
				f.close()
				return
				

			elif page[0] == "b": # the page is full
				pageNumber = pageNumber + 1
			else: # there is space in the current page
				systemCatalog.seek(pageNumber*1024) # point cursor to the head of the page

				# updating the numberOfRecords field in the page header
				if page[0] == "a":
					systemCatalog.write("b")
				elif int(page[0]) == 9:
					systemCatalog.write("a")
				else :
					systemCatalog.write(str(int(page[0]) + 1))

				# looking for if there is deleted type in the systemCatalog. If the answer is yes, the new type is inserted on the deleted type.
				i = 1 + 11 + 12 + 1 # numberOfRecords(1) + pageNumber(11) + typeName(12) + numberOfFields(1)
				foundInPlace = False
				while i < len(page):
					if page[i] == "0":
						foundInPlace = True
						break
					i = i + 86 # typeName(12) + numberOfFields(1) + isOccupied(1) + 6*fieldName(12)
				if foundInPlace == True:
					systemCatalog.seek(pageNumber*1024 + i - 13)
				else:
					systemCatalog.seek(fileSize)

				f = open(args.inputs[0] + ".txt", "w+")
				f.close()

				# filling the record header
				systemCatalog.write(typeName)
				systemCatalog.write(str(numberOfFields))
				systemCatalog.write("1") # isOccupied info

				# inserting field names
				for fieldName in fieldNames:
					systemCatalog.write(fit12bytes(fieldName))
				if foundInPlace == True:
					return

				# if there is no space for another record, filling the page with dummy content
				if page[0] == "a":
					systemCatalog.seek(fileSize + 86)
					for i in range(66): # 1024 - 12 - 86*11 = 66. There is 66 bytes of empty space to be filled with dummy content
						systemCatalog.write("!")
				return

def deleteType():
	typeName = args.inputs[0]
	with open("systemCatalog.txt","r+") as systemCatalog:
		pageNumber = 0
		fileSize = os.stat("systemCatalog.txt").st_size
		while pageNumber*1024 <= fileSize:
			systemCatalog.seek(pageNumber*1024) # point cursor to the head of the page
			pageRange = 0
			if fileSize - pageNumber*1024 >= 1024:
				pageRange = 1024
			else:
				pageRange = fileSize - pageNumber*1024
			page = systemCatalog.read(pageRange)
			i = 12
			while i < len(page):
				if page[i:i+12] == fit12bytes(typeName):
					systemCatalog.seek(pageNumber*1024 + i + 13)
					systemCatalog.write("0")
					os.remove(typeName + ".txt")
					systemCatalog.seek(pageNumber*1024)
					if page[0] == "b":
						systemCatalog.write("a")
					elif page[0] == "a":
						systemCatalog.write("9")
					else :
						systemCatalog.write(str(int(page[0]) - 1))
					return
				i = i + 86
			pageNumber = pageNumber + 1

def listTypes():
	allTypes = []

	with open("systemCatalog.txt","r") as systemCatalog:
		pageNumber = 0
		fileSize = os.stat("systemCatalog.txt").st_size
		while pageNumber*1024 <= fileSize:
			systemCatalog.seek(pageNumber*1024) # point cursor to the head of the page
			pageRange = 0
			if fileSize - pageNumber*1024 >= 1024:
				pageRange = 1024
			else:
				pageRange = fileSize - pageNumber*1024
			page = systemCatalog.read(pageRange)
			i = 1 + 11 + 12 + 1 # numberOfRecords(1) + pageNumber(11) + typeName(12) + numberOfFields(1) 
			while i < len(page):
				if page[i] == "1" :
					fieldNames = []
					k = i+1
					for j in range(int(getNumberOfFields(page[i-13:i-1]))):
						fieldNames.append(extractTypeName(page[k:k+12]))
						k = k + 12
					theType = (extractTypeName(page[i-13:i-1]), getNumberOfFields(page[i-13:i-1]), fieldNames)
					allTypes.append(theType)
				i = i + 86
			pageNumber = pageNumber + 1
		print(allTypes)

# DML Operations


def createRecord():
	typeName = fit12bytes(args.inputs[0])
	numberOfFields = int(getNumberOfFields(typeName))
	maxNumOfRecords = (1024 - 22) // (1 + numberOfFields*11)
	fieldValues = []
	for i in range(numberOfFields):
		fieldValue = int(args.inputs[i+1])
		fieldValues.append(fieldValue)


	with open(args.inputs[0] + ".txt","r+") as dataFile:
		pageNumber = 0
		fileSize = os.stat(args.inputs[0] + ".txt").st_size
		while pageNumber*1024 <= fileSize:
			dataFile.seek(pageNumber*1024) # point cursor to the head of the page
			pageRange = 0
			if fileSize - pageNumber*1024 >= 1024:
				pageRange = 1024
			else:
				pageRange = fileSize - pageNumber*1024
			page = dataFile.read(pageRange)
			if len(page) == 0: # the page is empty
				dataFile.seek(pageNumber*1024)
				# filling the page header
				dataFile.write(fit11bytes(1)) # numberOfRecords will be 1 after inserting the first record
				dataFile.write(fit11bytes(pageNumber + 1)) # pageNumber

				# filling the record header
				dataFile.write("1") # isOccupied info

				# inserting field values
				for fieldValue in fieldValues:
					dataFile.write(fit11bytes(fieldValue))
				return
				

			elif int(page[0:11]) == maxNumOfRecords: # the page is full
				pageNumber = pageNumber + 1
			else: # there is space in the current page
				dataFile.seek(pageNumber*1024) # point cursor to the head of the page
				recordSize = 1 + 11*numberOfFields

				# updating the numberOfRecords field in the page header
				dataFile.write(fit11bytes(int(page[0:11])+ 1))

				# looking for if there is deleted record in the dataFile. If the answer is yes, the new record is inserted on the deleted type.
				i = 22
				foundInPlace = False
				while i < len(page):
					if page[i] == "!":
						break
					elif int(page[i]) == 0:
						foundInPlace = True
						break
					i = i + recordSize
				if foundInPlace == True:
					dataFile.seek(pageNumber*1024 + i)
				else:
					dataFile.seek(fileSize)
				# filling the record header
				dataFile.write("1") # isOccupied info

				# inserting field values
				for fieldValue in fieldValues:
					dataFile.write(fit11bytes(fieldValue))
				if foundInPlace == True:
					return

				# if there is no space for another record, filling the page with dummy content
				if int(page[0:11]) == maxNumOfRecords-1:
					dataFile.seek(fileSize+recordSize)
					n = 1024 - 22 - recordSize*maxNumOfRecords
					i = 0
					while i < n:
						dataFile.write("!")
						i = i+1
				return


def deleteRecord():
	typeName = args.inputs[0]
	primaryKey = args.inputs[1]
	with open(typeName + ".txt","r+") as dataFile:
		pageNumber = 0
		fileSize = os.stat(typeName + ".txt").st_size
		numberOfFields = int(getNumberOfFields(fit12bytes(typeName)))
		while pageNumber*1024 <= fileSize:
			dataFile.seek(pageNumber*1024) # point cursor to the head of the page
			pageRange = 0
			if fileSize - pageNumber*1024 >= 1024:
				pageRange = 1024
			else:
				pageRange = fileSize - pageNumber*1024
			page = dataFile.read(pageRange)
			i = 23
			while i < len(page):
				if page[i:i+11] == fit11bytes(primaryKey):
					dataFile.seek(pageNumber*1024 + i -1)
					dataFile.write("0")
					dataFile.seek(pageNumber*1024)
					dataFile.write(fit11bytes(int(page[0:11]) - 1)) # number of records will decrease 1
					return
				i = i + (numberOfFields*11 + 1)
			pageNumber = pageNumber + 1

def searchRecord():
	typeName = fit12bytes(args.inputs[0])
	primaryKey = int(args.inputs[1])
	numberOfFields = int(getNumberOfFields(typeName))
	record = []
	with open(args.inputs[0] + ".txt", "r") as dataFile:
		pageNumber = 0
		fileSize = os.stat(args.inputs[0] + ".txt").st_size
		while  pageNumber*1024 <= fileSize:
			dataFile.seek(pageNumber*1024)
			pageRange = 0
			if fileSize - pageNumber*1024 >= 1024:
				pageRange = 1024
			else:
				pageRange = fileSize - pageNumber*1024
			page = dataFile.read(pageRange)
			i = 11 + 11 # numberOfRecords(11) + pageNumber(11)
			while i < len(page):
				if page[i] == "1" and int(page[i+1:i+12]) == primaryKey:
					j = i+1
					for k in range(numberOfFields):
						record.append(int(page[j:j+11]))
						j = j + 11
					print("primary key: ", end = "")
					print(record[0])
					print("other field values: ", end = "")
					print(record[1:])
					return
				i = i + (numberOfFields*11 + 1)
			pageNumber = pageNumber + 1



def listAllRecords():
	typeName = fit12bytes(args.inputs[0])
	numberOfFields = int(getNumberOfFields(typeName))
	allRecords = []
	with open(args.inputs[0] + ".txt","r") as dataFile:
		pageNumber = 0
		fileSize = os.stat(args.inputs[0] + ".txt").st_size
		while pageNumber*1024 <= fileSize:
			dataFile.seek(pageNumber*1024) # point cursor to the head of the page
			pageRange = 0
			if fileSize - pageNumber*1024 >= 1024:
				pageRange = 1024
			else:
				pageRange = fileSize - pageNumber*1024
			page = dataFile.read(pageRange)
			i = 11 + 11 # numberOfRecords(11) + pageNumber(11) 
			while i < len(page):
				if page[i] == "1" :
					records = []
					j = i+1
					for k in range(numberOfFields):
						records.append(int(page[j:j+11]))
						j = j + 11
					allRecords.append(records)
				i = i + (numberOfFields*11 + 1)
			pageNumber = pageNumber + 1
		print(allRecords)


if args.t and args.c:
	createType()

elif args.t and args.d:
	deleteType()

elif args.t and args.l:
	listTypes()

elif args.c and args.r:
	createRecord()

elif args.d and args.r:
	deleteRecord()

elif args.l and args.r:
	listAllRecords()

elif args.s and args.r:
	searchRecord()