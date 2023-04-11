# makes a get request to the patentsview api using a patent number
# used to get patent title, filing date, and abstracts. Could use to get government interests in the future.
import requests
from csv_processer import csv_to_dict
import time
from csv_scraping import get_patent_id
import re

def main():
    i = 0
    request_count = 0
    the_patents = csv_to_dict("/Users/elizabethschwartz/Documents/assistantships/scp/patents_proj/data/patents_added_patentsview_2022-7_to_2022-9.csv")
    for this_patent in the_patents:
        if request_count <= 42:
            patent_number = get_patent_id(this_patent)
            response_dict = makes_patentsview_get_request(patent_number)
            # if response_dict['count'] > 0:
            try:
                print('patentsview response for patent with number', patent_number + ': ')
                print(response_dict)
                print('title:', get_this_title(response_dict['patents'][0]))
                print('filing date:', get_filing_date(response_dict['patents'][0]))
                print('abstract:', get_this_abstract(response_dict['patents'][0]))
                # print('government awards:', get_gov_awards(response_dict['patents'][0]))
                # print('government orgs:', get_government_orgs(response_dict['patents'][0]))
                # print('inventor info:', get_inventors(response_dict['patents'][0]))
                print()
            except IndexError:
                print(this_patent, 'had no results from uspto')
            # else: pass
            request_count += 1
        else:
            print('--------------waiting for 60 seconds to not crash PatentsView api----------------')
            time.sleep(60)
            request_count = 0


def makes_patentsview_get_request(patent_number, api_key):

    header_args = {"accept": "application/json",
                   "X-Api-Key": api_key,
                   "Content-Type": "application/json"
                   }
    this_url = 'https://search.patentsview.org/api/v1/patent/?q={"patent_id":"' + patent_number+ '"}&f=["patent_title", "assignees", "patent_abstract", "patent_date", "patent_earliest_application_date", "gov_interest_statement"]'
    r = requests.get(this_url, headers=header_args)
    if r.status_code == 200:
        return r.json()
    else:
        print('something went wrong')
        print(r.status_code)
        print(r.headers)
        print(r.url)
        print(r.reason)
        pass


def get_gov_statement(response_dict):
    statement = str(response_dict['gov_interest_statement'])
    statement = re.sub('\\n',' ', statement)
    statement = re.sub('  ', ' ', statement)

    return statement

def get_inventors(response_dict):
    return response_dict['inventors']


def get_government_orgs(response_dict):
    try:
        interests = response_dict['gov_interest_organizations']
        # print(response_dict['gov_interest_organizations'])
        interest_list = []
        for interest in interests:
            interest_list.append(interest['fedagency_name'])
        return interest_list
    except KeyError:
        return 'no orgs to report'


def get_gov_awards(response_dict):
    try:
        awards =  response_dict['gov_interest_contract_award_numbers']
        award_list = []
        for an_award in awards:
            award_list.append(an_award['award_number'])
        return award_list
    except KeyError:
        return 'no interests to report'

def get_this_abstract(response_dict):
    return response_dict['patent_abstract']


def get_this_title(response_dict):
    return response_dict['patent_title']


def get_filing_date(response_dict):
    print(response_dict)
    filing_date = response_dict['patent_earliest_application_date']
    try:
        return filing_date.split('-')
    except AttributeError:
        pass


if __name__ == '__main__':
    main()

