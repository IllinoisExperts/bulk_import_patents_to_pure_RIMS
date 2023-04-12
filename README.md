# bulk_import_patents_to_pure_RIMS

bulk_import-patents_to_pure_RIMS is a python program that transforms a csv of patent metadata into xml for bulk upload to an instance of Elsevier's Pure research information managemeent system. This project was initially developed at the University of Illinois Urbana Champaign's University Library by the Research Information System Coordinator through a partnership with the Office of Technology Management. This program ingests a csv file with patent unique idntifiers, patent numbers, granted date, titles, and inventors and supplements these with data scraped from the USPTO's PatentsView API. As of 2023-03-22, the program covers the following metadata fields (when available):

- patent title
- patent number
- inventors names (and internal persons matching)
- published date
- filing date
- abstracts
- government interest statements

The following is a brief overview of the program and import process.

## CSV file preparation 

You will need to create a csv file for main.py to read in. The file should be formatted as follows: 
| dc.identifier.uniqueID      | dc.title | dc.date.issued | dc.creator                               | dc.identifier.patentID |
| --------------------------- | -------- | -------------- | ---------------------------------------- | ---------------------- |
| a unique ID                 | Title    | issue date     | inventor names separated by double pipes |  patent number


## Registering for a PatentsView API key

## Setting up Python

## A brief tour of the program

## Running main.py

## Bulk importing to Pure

## Adding government interest statetments

## Current problems with the program in need of solving

If you use this program for any publication, please cite it as follows: 

Schwartz, Elizabeth, Mark Zulauf, Elias Hubbard, and Sara Rasmussen. Bulk Import Patents to Pure RIMS. 2023. 

