# Simple-Storage-Manager
A storage manager which can handle different DDL and DML operations.

This program takes different flags as arguments.

-r flag stands for record

-t flag stands for type

-c flag stands for create

-d flag stands for delete

-l flag stands for list

-s flag stands for search

## Creating Type
So if a user wants to create a type, he/she should use -ct flag and he/she should give typeName, numberOfFields
and fieldNames arguments. For example, if a user wants to create a type named "dummyType" and this type has 3 fields,
user should give names to these fields and run the program using this command:
```bash
python storageManager.py -ct dummyType 3 fieldName1 fieldName2 fieldName3
```

## Deleting Type
If a user wants to delete a type, he/she should specify the name of the type and run the program using this command:
```
python storageManager.py -dt dummyType
```

## Listing All Types
If a user wants to list all types, he/she should run the program as:
```
python storageManager.py -lt
```
Output of this program is an array of type tuples. the tuple is in the form of (typeName, numberOfFields, namesOfTheFields)


## Creating Record
If user wants to create a record, he/she should specify the name of the type of this record and give the field values.
So if a user wants to create a record of "dummyType" he/she should run the program as:
```
python storageManager.py -cr dummyType 1 2 3 // assuming field values are 1,2 and 3.
```


## Deleting Record
If user wants to delete a record, he/she should specify the type name of this record and the primary key:
```
python storageManager.py -dr dummyType 1
```

## Listing All Records
If user wants to list all records of a type, he/she should specify the type name:
```
python storageManager.py -lr dummyType
```

## Searching For A Record
If user wants to search for a record, he/she should specify the type name and the primary key:
```
python storageManager.py -sr dummyType 1
```
