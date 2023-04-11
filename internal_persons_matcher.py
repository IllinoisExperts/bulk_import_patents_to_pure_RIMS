# matches internal people and rewrites them to a csv file
import pandas as pd
import random
from fuzzywuzzy import fuzz
import numpy as np
from csv_processer import csv_to_dict
from csv_scraping import get_author_data, get_patent_id
from patentsview_scraper import makes_patentsview_get_request, get_inventors

def main():
    ip_file_name = "/Users/elizabethschwartz/Documents/assistantships/scp/patents_proj/data/Pure persons - 92322.xls"
    ip = access_internal_persons(ip_file_name, "production")
    records = csv_to_dict("/Users/elizabethschwartz/Documents/assistantships/scp/patents_proj/data/test_cleaned_otm_patents.csv")
    internal_external_list = []
    for record in records:
        pv_response = makes_patentsview_get_request(get_patent_id(record))
        try:
            inventors = get_inventors(pv_response['patents'][0])
            print(inventors)
        except IndexError:
            pass
        except TypeError:
            pass
        person_list = []
        person_list.append(get_author_data(record))
        record['person'] = []
        i = 0
        for this_person in person_list[0]:
            print(this_person)
            record['person'].append(get_internal_external_authors(this_person, ip, 85))
            print(record['person'][i])
            i += 1

        print('--------------------------------------------------------------------')
        internal_external_list.append(record['person'])


def matches_internal_person(this_record, ip):
    this_person = {"first_name": this_record["first_name"], "last_name": this_record["last_name"]}
    this_record['person'] = get_internal_external_authors(this_person, ip, 83)
    return this_record


def clean_external_names(external_person):
    external_person['person'][0]['author']['first_name'] = input('first name: ')
    external_person['person'][0]['author']['last_name'] = input('last name: ')
    return external_person


def access_internal_persons(ip_file: str, mode) -> pd.DataFrame:
    """
    Create DataFrame containing internal persons; read in last name, first name, Pure ID
    :param ip_file: Str reference to Pure - Internal Persons file against which to validate the list of authors in csv_data.
    :return: DataFrame of internal_persons
    """
    if mode == 'production':
        df = pd.read_excel(ip_file, sheet_name="Persons (0)_1",
                           usecols=["3 Last, first name", "4 Name > Last name", "5 Name > First name", "21 ID",
                                    "10.1 Organizations > Organizational unit[1]"])
        columns_mapper = {"3 Last, first name":"3 Last, first name" , "4 Name > Last name": "4 Name > Last name", "5 Name > First name":"5 Name > First name", "21 ID":"21 ID","10.1 Organizations > Organizational unit[1]": "unit"}
        df = df.rename(columns=columns_mapper)
        return df
    else:
        df = pd.read_excel(ip_file, sheet_name="Persons (0)_1",
                           usecols=["1 Last, first name", "8.1 ID > Scopus Author ID[1]",
                                    "2.1 Organizations > Organizational unit[1]"])
        columns_mapper = {"1 Last, first name": "3 Last, first name", "8.1 ID > Scopus Author ID[1]": "21 ID", '2.1 Organizations > Organizational unit[1]': 'unit'}
        df = df.rename(columns=columns_mapper)
        return df



def get_internal_external_authors(an_author, internal_persons: pd.DataFrame, custom_ratio: int) -> tuple:
    """
    Read in list of 1+ reformatted authors (scope: 1 research output) and Internal Persons file.
    For each author in author_list,
        Use fuzzy matching to compare author with all persons in Internal Persons.
        Where a match is found, grab PureID and first Unit Affiliation; else, generate random ID and unit = np.nan.
    Add each author consecutively to new validated_authors list.
    returns a dictionary containing a list of internal and external authors. use to process author data.

    NOTE: Beware of false matches where author names are very similar but represent different people. Set detailed_output=True for report.
    """
    if type(an_author) == list:
        an_author = an_author[0][0]
    matches_log = []
    external_authors = []
    strings_to_check = internal_persons["3 Last, first name"].to_list()
    # print(an_author)
    correct_string =str(an_author["last_name"]) + " " + str(an_author["first_name"])
    ratios = []
    for string in strings_to_check:
        # Exact match
        if string == correct_string:
            ratios.append((string, 100))
            break
        else:
            ratio = fuzz.ratio(string, correct_string)
            if ratio > custom_ratio:
                ratios.append((string, ratio))
    try:
        if len(ratios) == 1:
                # Look up ratios[0] in df, return the ID of that match using .loc
            select_row = internal_persons.loc[internal_persons["3 Last, first name"] == ratios[0][0]]
            auth_dupes = select_row.reset_index()
            idx_len = auth_dupes.index.tolist()
            if len(idx_len) > 1:
                print("Warning! More than one UIUC faculty has the same name. Selecting the first author in list. You may want to fix this manually!")
                auth_row_one = select_row.head(1)
                auth_id = auth_row_one["21 ID"].item()
                auth_id = int(auth_id)
                unit_affiliation = auth_row_one['unit'].item()
            else:
                auth_id = select_row["21 ID"].item()
                auth_id = int(auth_id)
                unit_affiliation = select_row['unit'].item()
            matches_log.append((correct_string, ratios))
        elif len(ratios) == 0:
            # Author not found in Internal Persons file - assign random ID
            auth_id = "imported_person_" + str(random.randrange(0, 1000000)) + str(random.randrange(0, 1000000))
            unit_affiliation = np.nan
        else:
            # If more than 1 person from Internal Persons file matched, return highest match
            ratios.sort(key=lambda x: x[1], reverse=True)
            matches_log.append((correct_string, ratios))
            # Use position within list to get back to the string, look up string in df to return ID using .loc
            select_row = internal_persons.loc[internal_persons["3 Last, first name"] == ratios[0][0]]
            auth_id = select_row["21 ID"].tolist()[0]
            auth_id = int(auth_id)
            unit_affiliation = select_row['unit'].tolist()[0]
    except ValueError:
        auth_id  = "imported_person_" + str(random.randrange(0, 1000000)) + str(random.randrange(0, 1000000))
        unit_affiliation = np.nan
    author_dict = {"author_id": auth_id, "author": an_author, "unit_affiliation": unit_affiliation}
    return author_dict



if __name__ == '__main__':
    main()
