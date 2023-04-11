# small library containing functions to process csv files
import csv

def csv_to_dict(csv_file_name):

    prizes = []
    with open(csv_file_name, 'r', newline='', encoding='utf-8') as infile:
        csvin = csv.reader(infile)
        headers = next(csvin)
        headers = [header.strip().lower() for header in headers]
        for row in csvin:
            n = 0
            your_dict = {}
            for column in row:
                your_dict[headers[n]] = column
                n += 1
            prizes.append(your_dict)
    return prizes


def makes_results_csv(results, outfile_name):
    headers = results[0].keys()
    rows = results
    with open(outfile_name, 'w', encoding='UTF-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            try:
                writer.writerow(row)
            except AttributeError:
                pass

