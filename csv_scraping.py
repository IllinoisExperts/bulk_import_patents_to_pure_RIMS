# a library holding functions that scrape metadata from the patents csv file and prep it to be put into xml
from csv_processer import csv_to_dict
import re

def main():
    patents = csv_to_dict()
    i = 1
    for patent in patents:
        print(patent)
        authors = get_author_data(patent)
        for author in authors:
            print('author first:', get_author_first(author))
            print('author last:', get_author_last(author))
        date = get_date(patent)
        print('patent id:', get_patent_id(patent))
        print('date:', get_month(date)+'/'+get_day(date)+'/'+get_year(date, i))
        print('title:', get_title(patent))
        print('uuid: ', str(get_uuid(patent)))
        i += 1


# author related functions
def get_author_data(patent):
    author_list = patent['dc.creator']
    author_list = author_list.split('||')
    these_authors = []
    for author in author_list:
        first_name = get_author_first(author)
        last_name = get_author_last(author)
        these_authors.append({'first_name': first_name, 'last_name': last_name})
    return these_authors


def get_author_last(author_name):
    author_name = author_name.split(',')
    last_name = author_name[0]
    if len(author_name) > 2:
        last_name = last_name + ',' + author_name[1]
        return last_name.strip()
    else:
        return last_name.strip()


def get_author_first(author_name):
    author_name = author_name.split(',')
    if len(author_name) > 2:
        author_first = author_name[2].strip().title()
    else:
        author_first = author_name[1].strip().title()
    author_first = re.sub('\s\s+',' ', author_first)
    return author_first


# date related functions
def get_date(patent):
    a_date = str(patent['dc.date.issued'])
    date_list = a_date.split('-')
    return date_list


def get_year(my_date, i):
    if my_date[0] == '':
        print('The patent on line', i, 'must have a 4 digit integer publication year. Add a year or import will fail.')
    elif re.search('(\d{4,4})', my_date[0]) == None:
        print('The patent on line', i, 'must have a publication year that is a 4 digit integer.')
    elif len(list(my_date[0])) > 4:
        print('The patent on line', i, 'must have a publication year that is a 4 digit integer.')
    else:
        return my_date[0]


def get_month(my_date):
    try:
        return my_date[1]
    except IndexError:
        pass


def get_day(my_date):
    try:
        return my_date[2].split("T")[0]
    except IndexError:
        pass


# title related function(s) - right now we are assuming this is xml-ready
def get_title(patent):
    my_title = patent['dc.title']
    my_title = my_title.strip()
    return my_title


# patent ID number functions
def get_patent_id(patent):
    id = patent['dc.identifier.patentid'].strip().replace(',', '')
    return id


# created UUID
def get_uuid(patent):
    return 'patent' + patent['dc.identifier.uniqueid']


if __name__ == '__main__':
    main()
