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

You will need to create a csv file for main.py to read in. Each patent should have a unique identifier, a title, a date issued, a creator(s), and a patent number. For example, for a patent titled "Important Invention" issued on 2023-04-12 to the creators Elizabeth Schwartz and Mark Zulauf, the patent should be rendered as follows
| dc.identifier.uniqueID      | dc.title | dc.date.issued | dc.creator| dc.identifier.patentID |
| --------------------------- | -------- | -------------- | ---------------------------------------- | ---------------------- |
| 000123                 | Important Invention    | 2023-04-12     | Schwartz, Elizabeth&#124;&#124;Zulauf, Mark |  123456

- **dc.identifier.uniqueID**: A unique identifier assigned to each patent. This will be used as the research output uuid in pure. It is essential to devise an immutable uuid for each patent so that you are able to update the patent via the bulk importer as opposed to creating anothter representation of it. 
- **dc.title**: The patent's title. This field can be ignored if you do not have this information as it is available through the PatentsView API as well.
- **dc.date.issued**: The issue date of the patent used in the publication date field in Pure. Must be formatted according to Dublin Core standards: YYYY-MM-DD. This information is also available through the PatentsView API. If you do not have it, you could modify the program to include it in your query.
- **dc.creator**: inventors first and last names separated by '||'. This information is also available through the PatentsView API. If you do not have it, you could modify the program to include it in your query.
- **dc.identifier.patentID**: The patent number. This field is necessary for us to search the PatentsView API. 


## Registering for a PatentsView API key
Registering for a PatentsView API key is completely free! Follow the (instructions)[https://patentsview.org/apis/keyrequest] on the PatentsView site.

## Setting up Python

## A brief tour of the program

## Running main.py

## Bulk importing to Pure

## Adding government interest statetments

## Current problems with the program in need of solving

If you use this program for any publication, please cite it as follows: 

Schwartz, Elizabeth, Mark Zulauf, Elias Hubbard, and Sara Rasmussen. Bulk Import Patents to Pure RIMS. 2023. 

