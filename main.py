# writes xml from the csv file
from csv_processer import csv_to_dict
from csv_scraping import get_author_data
from csv_scraping import get_date
from csv_scraping import get_day
from csv_scraping import get_month
from csv_scraping import get_year
from csv_scraping import get_uuid
from csv_scraping import get_patent_id
from csv_scraping import get_title
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import patentsview_scraper as pv
import time
import internal_persons_matcher as ip
import tqdm
import os

def main():
    print ('This program takes in a csv file containing patent metadata and a spreadsheet containing internal persons info and turns them into xml for bulk import to an instance of Pure.')
    print('The csv file must be formatted according to the schema described in program_requirements.txt in this python project.')
    print('First, we need to gather some information about the location of these files on your computer and your instance of Pure.')
    patents_file = input('enter complete path to the patents csv file: ')
    if os.path.isfile(patents_file):
        patents = csv_to_dict(patents_file)
    else:
        while not os.path.isfile(patents_file) and patents_file != 'quit':
            print(patents_file, 'is not a valid file. Enter a valid file name or "quit" to terminate the program.')
            patents_file = input('enter complete path to the patents csv file: ')
        patents = csv_to_dict(patents_file)
    setting = input('are you loading data to the public portal (enter y or n):')
    if setting == 'y':
        internal_persons_file = input('enter complete path to the production internal persons excel file: ')
        internal_persons = ip.access_internal_persons(internal_persons_file, 'production')
        university_uuid = input('enter the uuid associated with your university in the PRODUCTION portal of your Pure system.')
        # university_uuid = "Enter your university's uuid in PRODUCTION here and comment out the above to hardcode this step!"
    else:
        internal_persons_file = input('enter complete path to the staging internal persons excel file: ')
        internal_persons = ip.access_internal_persons(internal_persons_file, 'staging')
        university_uuid = input('enter the uuid associated with your university in the STAGING portal of your Pure system')
        # university_uuid = "Enter your university's uuid in STAGING here and comment out the above to hardcode this step!"
    university_name = input('enter the name of your university as you want it to appear on patents not affiliated with internal persons.')
    # university_name = "Enter your university's name (i.e., University of Illinois Urbana Champaign)
    # here to and comment out the above to hardcode this step!"
    pv_api_key = input('enter your API key to the patentsview API: ')
    # pv_api_key = "Kyu7KTO7.w1k5rarnrGRb6PUGjRX1vCrpRBJO939Z"
    outfile_name = str(input('enter the name of the output xml file: '))

    # prepping to start writing xml
    request_count = 0
    root = Element('publications')
    tree = ElementTree(root)
    root.set('xmlns', "v1.publication-import.base-uk.pure.atira.dk")
    root.set('xmlns:tns', "v3.commons.pure.atira.dk")
    outfile = open(outfile_name, 'wb')
    number_analyzed = 0
    api_connection_error_count = 0
    # iterating over the entire csv file to create xml
    for a_patent in tqdm.tqdm(patents):
        if request_count > 40:
            print('--------------waiting for 60 seconds to not crash PatentsView api----------------')
            time.sleep(60)
            api_connection_error_count = write_xml(a_patent, root, number_analyzed, setting, api_connection_error_count, internal_persons, university_uuid, university_name, pv_api_key)
            number_analyzed += 1
            request_count = 1
        else:
            api_connection_error_count = write_xml(a_patent, root, number_analyzed, setting, api_connection_error_count, internal_persons, university_uuid, university_name, pv_api_key)
            number_analyzed += 1
            request_count += 1
    # creates the xml outfile
    tree.write(outfile)
    print('***EXIT REPORT***')
    print(str(len(patents)), 'were analyzed.', number_analyzed, 'patents were written to xml')
    print(api_connection_error_count, 'patents were unable to connect to the API meaning they lack abstracts, '
                       'and their titles have not been checked against the USPTO database')
    print('Review the changes in changes_report.csv in this same directory.')


def write_xml(this_patent, root, csv_line_number, setting, api_connection_error_count, internal_persons, university_uuid, university_name, pv_api_key):
    # calling uspto api on patent based on its number
    this_patent_number = get_patent_id(this_patent)
    uspto_api_response = pv.makes_patentsview_get_request(str(this_patent_number), pv_api_key)
    patent = SubElement(root, 'patent')
    # need to generate a unique ID that won't change (based on patent metadata)
    patent.set('id', get_uuid(this_patent))
    patent.set('subType', 'patent')
    # peer review info - patents are never peer reviewed
    peer_review = SubElement(patent, 'peerReviewed')
    peer_review.text = 'false'
    # pub status info- assume all patents are published
    pub_statuses = SubElement(patent, 'publicationStatuses')
    pub_status = SubElement(pub_statuses, 'publicationStatus')
    status_type = SubElement(pub_status, 'statusType')
    status_type.text = 'published'
    # getting date data (subelement of pub status)
    this_date = get_date(this_patent)
    date = SubElement(pub_status, 'date')
    year = SubElement(date, "tns:year")
    year.text = get_year(this_date, csv_line_number)
    month = SubElement(date, 'tns:month')
    month.text = get_month(this_date)
    day = SubElement(date, 'tns:day')
    day.text = get_day(this_date)
    # language info - assuming always english US
    language = SubElement(patent, 'language')
    language.text = 'en_US'
    # title info - from uspto
    title = SubElement(patent, 'title')
    title_text = SubElement(title, 'tns:text')
    title_text.set('lang', 'en')
    title_text.set('country', 'US')
    try:
        title_text.text = pv.get_this_title(uspto_api_response['patents'][0])
    except IndexError:
        title_text.text = get_title(this_patent)
    except TypeError:
        title_text.text = get_title(this_patent)
    except KeyError:
        title_text.text = get_title(this_patent)
    # abstract info from USPTO
    abstract = SubElement(patent, 'abstract')
    abstract_text = SubElement(abstract, 'tns:text')
    abstract_text.set('lang', 'en')
    abstract_text.set('country', 'US')
    try:
        abstract_text.text = pv.get_this_abstract(uspto_api_response['patents'][0])
        # abstract_text.text = 'this is a test!'
    except IndexError:
        print('patent on line number', csv_line_number, 'has a malformed number:',
              str(this_patent_number) + '. API data cannot be fetched. IndexError.')
        api_connection_error_count += 1
        pass
    except TypeError:
        print('patent on line number', csv_line_number, 'could not connect to the api. Caused a TypeError')
        api_connection_error_count += 1
        pass
    except KeyError:
        print('patent on line number', csv_line_number, 'could not connect to the api. Caused a TypeError')
        api_connection_error_count += 1
        pass
    # writing author xml and assigning internal authors pure uuids
    persons = SubElement(patent, 'persons')
    write_author_xml(this_patent, persons, internal_persons, university_uuid, patent, university_name)
    # makes your university the managing unit of the patent (i.e., for any patent at UIUC, UIUC is the managing unit
    # we can fix this once in the portal)
    owner = SubElement(patent, 'owner')
    owner.set('id', university_uuid)
    # patent number- from patents csv file
    patent_number = SubElement(patent, 'patentNumber')
    patent_number.text = get_patent_id(this_patent)
    # filing date - just called "date"- from USPTO
    try:
        this_filing_date = pv.get_filing_date(uspto_api_response['patents'][0])
        if type(uspto_api_response) != None:
            filing_date = SubElement(patent, 'date')
            filing_date.text = str(get_year(this_filing_date, csv_line_number)) + "-" + str(get_month(this_filing_date)) + "-" + str(get_day(this_filing_date))
    except TypeError:
        pass
    except IndexError:
        pass
    # coutry/territory- just called "country"- we always assume US
    country = SubElement(patent, 'country')
    country.text = 'us'
    # # pure can't recognize uploaded bibliographical notes, so this is currently retired as of 2023-03-23
    # instead, we are using the write API to add these after XML upload in adds_gov_ints.py 
    # we would put government granting info here if this xsd gets fixed
    # bibliographic notes (government funding info)
    # try:
    #     bibliographic_notes = SubElement(patent, 'bibliographicalNotes')
    #     bibliographic_note = SubElement(bibliographic_notes, 'bibliographicalNote')
    #     bibliographic_note_text = SubElement(bibliographic_note, 'tns:text')
    #     bibliographic_note_text.set("lang", "en")
    #     bibliographic_note_text.set("country", "US")
    #     bibliographic_note_text.text = str(pv.get_gov_awards(uspto_api_response['patents'][0]))
    # except IndexError:
    #     pass
    # urls would go here if we want to include them
    # urls = SubElement(patent, 'urls')
    # url = SubElement(urls, 'url')
    # this_url = SubElement(url, 'url')
    # description_url = SubElement(url, 'description')
    # description_url_text = SubElement(description_url, 'ns2:text')
    # type_url = SubElement(url, 'type')
    return api_connection_error_count


def write_author_xml(patent, persons, internal_persons, university_uuid, xml_patent, university_name):
    authors = get_author_data(patent)
    these_authors = []
    no_internals = True
    for an_author in authors:
        these_authors.append(ip.matches_internal_person(an_author,internal_persons))
    for an_author in these_authors:
        author = SubElement(persons, 'author')
        role = SubElement(author, 'role')
        role.text = 'inventor'
        person = SubElement(author, 'person')
        person.set('id', str(an_author['person']['author_id']))
        first_name = SubElement(person, 'firstName')
        first_name.text = an_author['first_name']
        last_name = SubElement(person, 'lastName')
        last_name.text = an_author['last_name']
        if 'imported' in str(an_author['person']['author_id']):
                 pass
        else:
            no_internals = False
            organizational_units = SubElement(author, 'organisations')
            organizational_unit = SubElement(organizational_units, 'organisation')
            organizational_unit.set('id', university_uuid)
            organizational_unit.set('origin', 'internal')
            org_unit_name = SubElement(organizational_unit, 'name')
            org_name_text = SubElement(org_unit_name, 'tns:text')
            org_name_text.text = university_name
    # if there are no internal inventors, your university is added as an organizational inventor
    if no_internals:
        organizations = SubElement(xml_patent, 'organisations')
        an_organization = SubElement(organizations, 'organisation')
        an_organization.set('id', university_uuid)



main()
