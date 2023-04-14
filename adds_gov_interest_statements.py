import requests
import json
import patentsview_scraper as pv
from csv_scraping import csv_to_dict
import csv_scraping
import re
import time
import os
import tqdm


def main():
    patents_file = input('enter complete path to the otm csv file: ')
    if os.path.isfile(patents_file):
        patents = csv_to_dict(patents_file)
    else:
        while not os.path.isfile(patents_file) and patents_file != 'quit':
            print(patents_file, 'is not a valid file. Enter a valid file name or "quit" to terminate the program.')
            patents_file = input('enter complete path to the otm csv file: ')
        patents = csv_to_dict(patents_file)
    outfile_path = input('enter complete path to a txt file for writing results: ')
    while not os.path.isfile(outfile_path) and outfile_path != 'quit':
        print(outfile_path, 'is not a valid file. Enter a valid file name or "quit" to terminate the program.')
        outfile_path = input('enter complete path to the otm csv file: ')
    setting = input('are you loading data to the public portal (enter y or n): ')
    if setting == 'y':
        pure_api_key = input('enter your key to your Pure production API: ')
        api_url = input('enter the url for your Pure production API. For example, https://experts.illinois.edu/ws/api/ : ')
    else:
        pure_api_key = input('enter your key to your Pure staging API: ')
        api_url = input('enter the url for your Pure production API. For example, https://experts.illinois.edu/ws/api/ : ')
    pv_api_key = input('enter your API key to the PatentsView API: ')
    to_update = 0
    request_count = 0
    failed_puts = []
    patents_not_found = []
    for patent in tqdm.tqdm(patents):
        if request_count <= 40:
            patent_number = csv_scraping.get_patent_id(patent)
            pure_response = search_pure(patent_number, pure_api_key, api_url)
            if pure_response == 'null':
                patents_not_found.append(patent)
            else:
                updated_dict = adds_gov_stuff(patent_number, pure_response, pv_api_key)
                request_count += 1
                try:
                    if 'no orgs to report' in str(updated_dict):
                        pass
                    elif 'None' in str(updated_dict):
                        pass
                    else:
                        failed_puts.append(put_bib_note(updated_dict, pure_api_key, api_url))
                        to_update += 1
                except KeyError:
                    pass
        else:
            print('waiting to not crash patentsview api.........................')
            time.sleep(60)
            request_count = 0
            patent_number = csv_scraping.get_patent_id(patent)
            pure_response = search_pure(patent_number, pure_api_key, api_url)
            if pure_response == 'null':
                patents_not_found.append(patent)
            else:
                updated_dict = adds_gov_stuff(patent_number, pure_response, pv_api_key)
                request_count += 1
                try:
                    if 'no orgs to report' in str(updated_dict):
                        pass
                    elif 'None' in str(updated_dict):
                        pass
                    else:
                        failed_puts.append(put_bib_note(updated_dict, pure_api_key, api_url))
                        to_update += 1
                except KeyError:
                    pass
    i = 0
    with open(outfile_path, 'w') as outfile:
        for thing in patents_not_found:
            print(thing, file=outfile)
        print('-----------------------------------------------------------', file=outfile)
        print('failed put requests:', file=outfile)
        for item in failed_puts:
            if str(item) != 'None':
                i +=1
                print(item, file=outfile)
            else:
                pass
    print(to_update, 'patents should have been updated.')
    print(i, 'failed to update')


# searches pure for a research output record by supplied search string
def search_pure(search_string, api_key, api_url):
    print(search_string)
    app_json = 'application/json'
    headers = {'accept': app_json, 'api-key': api_key, 'Content-Type': app_json}
    # This is the search criteria sent to the API
    values = json.dumps({"size": 10, "offset": 0,"searchString": str(search_string), "orderBy": "ascending"})
    # Make request - Returns JSON of search results
    pure_response = requests.post(api_url + 'research-outputs/search/', headers=headers, data=values)
    # unpacks search results and returns them if they are not null
    if pure_response.status_code == requests.codes.ok:
        pure_response_json = pure_response.json()
        if pure_response_json['count'] != 0:
            return pure_response_json['items'][0]
        else:
            print(pure_response.reason)
            print(pure_response.url)
            print(pure_response)
            return 'null'
    else:
        print(pure_response.reason)
        print(pure_response.url)
        return 'null'


# adds government interest statements to patents via querying USPTO's API
def adds_gov_stuff(patent_number, pure_response, pv_api_key):
    # collects data from USPTO API
    uspto_response = pv.makes_patentsview_get_request(patent_number, pv_api_key)
    # unpacks the USPTO data
    try:
        interest_statement = pv.get_gov_statement(uspto_response['patents'][0])
        if interest_statement == '':
            return 'no orgs to report'
        elif interest_statement == 'None':
            return 'no orgs to report'
        # if there are gov interests, we write them into the bibliographicalNote field of the pure response
        else:
            pure_response['bibliographicalNote'] = {
            "en_US": str(interest_statement)
            }
            return pure_response
    # if there are no patents in the response, that means we don't have any gov interests as well.
    except IndexError:
        return 'no orgs to report'
        pass


# uploads government interest statements via read/write API
def put_bib_note(pure_response, api_key, api_url):
    # determining what server to use based on the api key passed
    app_json = 'application/json'
    headers = {'Accept': app_json, 'api-key': api_key, 'Content-Type': app_json}
    this_patent = pure_response['uuid']
    # encodes the pure response into valid JSON markup and utf-8
    values = process_pure_response(pure_response)
    values = values.encode('utf-8')
    # uploads the data to pure
    put_pure_response = requests.put(api_url + 'research-outputs/'+ str(this_patent), headers=headers, data=values)
    print(put_pure_response.url)
    print(pure_response['title']['value'], 'pure put api response:', put_pure_response.status_code)
    print('------------------------------------------------------------------------------')
    if put_pure_response.status_code != 200:
        print(put_pure_response.status_code)
        return pure_response


# encodes pure response str into JSON to prepare for put request
def process_pure_response(pure_response):
    # replaces any single quotes we want to preserve with '%' including single quotes in text fields for abstract, title, interest statements,& names
    pure_response['abstract']['en_US'] = re.sub('\'', '%', pure_response['abstract']['en_US'])
    pure_response['title']['value'] = re.sub('\'', '%', pure_response['title']['value'])
    pure_response['bibliographicalNote']['en_US'] = re.sub('\'', '%', pure_response['bibliographicalNote']['en_US'])
    for i in range(len(pure_response['contributors'])):
        pure_response['contributors'][i]['name']['firstName'] = re.sub('\'', '%', pure_response['contributors'][i]['name']['firstName'])
        pure_response['contributors'][i]['name']['lastName'] = re.sub('\'', '%', pure_response['contributors'][i]['name']['lastName'])
    # transforms unescaped single ' to " for JSON encoding
    pure_response = re.sub('\'', '"', str(pure_response))
    # wraps True and False binary values in " for JSON encoding
    pure_response = re.sub(' True', '"True"', str(pure_response))
    pure_response = re.sub(' False', '"False"', str(pure_response))
    # replaces % with ' to preserve wanted single quotes in abstracts, interest statements, titles, and names
    pure_response = re.sub('%', '\'', str(pure_response))
    return pure_response


main()
