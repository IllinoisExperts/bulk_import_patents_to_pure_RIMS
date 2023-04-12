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
Registering for a PatentsView API key is completely free! Follow the [instructions](https://patentsview.org/apis/keyrequest) on the PatentsView site.

## Setting up Python

After you have created the csv file and registered for a PatentsView API key, you're ready to move over to Python. 

### Installing Python (if you haven't before)
If you have not downloaded Python before, visit Python's [website](https://www.python.org/downloads/) and download the most recent package that correlates with your particular machine (windows, macOS, or linux). Check out this [tutorial](https://realpython.com/installing-python/) for help with installations on windows, mac, or linux.

Next, you will probably want to install a virtual environment. Virtual environments allow you to download different python packages that may modify how your computer works without applying those changes to your entire machine. There are many types of virtual environments, but Anaconda navigator is probably the most popular and it's *free*. Install Anaconda following the instructions on its [website](https://docs.anaconda.com/anaconda/install/index.html). After installing Anaconda, you need to set up your first conda virtual environment. Follow [this](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) tutorial. 

We will need to install a number of python libraries in the Anaconda virtual environment. See **Dependencies Installation** below and install the packages using their conda installation guides.

Finally, you probably want to work with python in an IDE or integrated development environment. IDEs allow you to create, edit, and run python code in a more user friendly environment. There are many popular and free IDEs. VSCode is one of the more popular free IDEs. You can download it following the directions on its [website](https://code.visualstudio.com/download). You'll want to install VSCode's [python extension](https://code.visualstudio.com/docs/python/python-tutorial) to use it as a python IDE. Next we need to make sure that VSCode can find the [anaconda virtual environment](https://code.visualstudio.com/docs/python/environments) we just created so that it can access all the python libraries we just downloaded.

### Downloading this github repo

Download this github repo using whatever method you prefer. If you don't have a preference, I recommend locating the code button on the right hand side of the screen, clicking it, and selecting Download ZIP. 

### Dependencies Installation 

**bulk_import_patents_to_pure_RIMS** requires the installation of a number of python packages some of which come with standard Python and others that need to be installed in a virtual environment. Their names, documentation, and installation instructions are available below: 
- [tqdm.tqdm](https://tqdm.github.io/)  
- [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/) or for [conda](https://anaconda.org/conda-forge/fuzzywuzzy) install
- [pandas](https://pandas.pydata.org/docs/getting_started/install.html): for an anaconda environment, enter the following command in the terminal "conda install pandas" after activating the environment
- [numpy](https://numpy.org/install/): for an anaconda environment, enter the following command in the terminal "conda install numpy" after activating the environment
- [json](https://docs.python.org/3/library/json.html): comes with python standard install
- [random](https://docs.python.org/3/library/random.html): comes with python standard install
- [csv](https://docs.python.org/3/library/csv.html): comes with python standard install
- [re](https://docs.python.org/3/library/re.html): comes with python standard install
- [requests](https://docs.python-requests.org/en/latest/): comes with python standard install
- [ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html): comes with python standard install
- [time](https://docs.python.org/3/library/time.html): comes with python standard install


## A brief tour of the program

In addition to the external libraries discussed above, this program relies on five custom libraries created for this program: csv_scraping.py, internal_persons_matcher.py, csv_processor.py, compares_inventor_lists.py, and patentsview_scraper.py. These programs hold a variety of functions that scrape and format metadata from the csv file to be put in xml, supplement patents with metadata from the USPTO API, match names to internal persons, and create logs of changes in inventor lists between files. There is no need to run these libraries because main.py and adds_gov_ints.py invoke them as they execute.

patents.xml is the outfile to which you will write the xml rendered using ElementTree. This is the file you should upload to Pure’s bulk importer. If you prefer to change the files’s name, you can do so by renaming the outfile.

main.py and add_gov_int.py are the only 2 programs you will run.

## Running main.py

- Navigate main.py program and run it.
- First, the programm will ask you to enter the complete path to the csv file you just created.
- answer the prompt in the console by typing "y" if you are going to bulk import the xml file into the public portal (for production) or "n" if you are going to upload the xml file into the test portal.
- provide the complete path to the internal persons excel file you will be using to match people to internal persons. This file will be different dependent on whether or not you are uploading to staging or production.
- enter the UUID associated with your organization in backend of the associated instance (staging or production). 
- enter the name of your organization
- enter your PatentsView API key
- finally enter the name of the xml file you want to create. I.e., 'uiuc_patents_2023-01-25.xml'

The program will commence writing an xml rendered patent object out to patents.xml for every row in the csv file. If any the date field is missing a year or is not formatted properly, the program will send an error message asking you to write a four digit integer date for a patent on the corresponding line. For example, entering nothing for the date field will cause an error as will entering the year 1996 as ’96. Additionally, for each row in the file it will use the patent’s number to query the PatentsView api for title, abstract, and filing date information. If the query is unsuccessful, the program prints an associated error message. Note that none of the fields from the uspto api are mandatory.

The program will stop after it sends 40 requests to the api and wait 60 seconds to restart. This is intentional. PatentsView can only process 45 requests/minute/user. To prevent the server from sending us 500 errors, we have to wait between request batches.

The program may take around an hour to run (it takes about 50 minutes to process 1600 patents). This is not cause for concern.
Once the program finishes running, it will print and exit report and produce two files. The exit report explains how many patents failed to connect to the API. If this number makes up a significant portion of the total, it is likely that something went wrong with the API. The xml file the program produces is that which you will upload to Pure.

## Bulk importing to Pure
Once the program finishes running navigate to the Pure bulk importer and upload the patents.xml file for validation. On the “Verify/Configure” tab, toggle the “Updating Existing Publications” option to “on.” Continue through the import Wizard.
After successfully importing the patents, you will need to run the SDG keywords task because reuploading abstracts automatically overwrites these keywords. Also, rerun the re-affiliation task to reaffiliate internal people with their organizational units. Uploading xml automatically overwrites these.

## Adding government interest statetments

## Current problems with the program in need of solving

If you use this program for any publication, please cite it as follows: 

Schwartz, Elizabeth, Mark Zulauf, Elias Hubbard, and Sara Rasmussen. Bulk Import Patents to Pure RIMS. 2023. 

