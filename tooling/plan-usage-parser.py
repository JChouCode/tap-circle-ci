import csv
from datetime import datetime
from datetime import timezone
import io
import re
import sys


def is_row_empty(row):
    '''
    CircleCI uses blank rows to divide up visual sections in the Usage report
    '''
    return not [x for x in row if x]


def slurp_next_section(reader):
    '''
    Simple helper, which returns all of the rows between two empty (or EOF) rows
    '''
    section = []
    while not is_row_empty(row := next(reader, [])):
        section.append(row)
    return section


def parse_number_percent(text):
    '''
    '25929 (0.24%)' -> 25929
    '1475000' -> 1475000
    '''
    return int(re.search(r'(^\d+)', text).group(1))


def parse_date_header(date_header):
    '''
    'Mar 01, 2023 - Mar 31, 2023' -> 2023-03-01T00:00:00+00:00
    '''
    date = re.search(r'^(.*?) -', date_header).group(1)
    return datetime.strptime(date, '%b %d, %Y').replace(tzinfo=timezone.utc).isoformat()


def parse_summary_to_date_headers(rows):
    '''
    Extract the date headers present in the summary section.

    eg,
    ,"Jan 01, 2023 - Jan 31, 2023","Feb 01, 2023 - Feb 28, 2023","Mar 01, 2023 - Mar 31, 2023",...
    Total Credits used #,1580,1081,17009,...
    ...

    ->

    ['2023-01-01T00:00:00+00:00', '2023-02-01T00:00:00+00:00', '2023-03-01T00:00:00+00:00']
    '''
    date_headers = rows[0][1:]
    return [parse_date_header(date_header) for date_header in date_headers]


def parse_usage_row_to_dicts(usage_type, row, date_headers):
    detail = row[0]
    for credits_as_number_percent, date_header in zip(row[1:], date_headers):
        yield {
            'year_month': date_header,
            'detail': detail,
            'usage_type': usage_type,
            'credits': parse_number_percent(credits_as_number_percent)
        }


def parse_usage_rows_to_dicts(usage_type, rows, date_headers):
    result = []
    for row in rows[1:]:
        result += parse_usage_row_to_dicts(usage_type, row, date_headers)
    return result


def parse(file_path):
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile)

        # Slurp each section
        header = slurp_next_section(reader)
        summary = slurp_next_section(reader)
        slurp_next_section(reader) # We can ignore the "Credit breakdown:" section as it's just a divider
        project_based_credit_usage = slurp_next_section(reader)
        resource_based_credit_usage = slurp_next_section(reader)
        user_seat_based_credit_usage = slurp_next_section(reader)

        # Parse out the date_headers to be used throughout
        date_headers = parse_summary_to_date_headers(summary)
        # Unpack all results into a single array
        return [
            *parse_usage_rows_to_dicts('project', project_based_credit_usage, date_headers),
            *parse_usage_rows_to_dicts('resource', resource_based_credit_usage, date_headers),
            *parse_usage_row_to_dicts('user_seat', user_seat_based_credit_usage[0], date_headers)
        ]


def spit(dicts):
    output = io.StringIO()
    
    writer = csv.DictWriter(output, fieldnames=dicts[0].keys())
    writer.writeheader()
    for d in dicts:
        writer.writerow(d)
    
    return output.getvalue().rstrip()


def main(args):
    input_file_path = args[1]
    parsed = parse(input_file_path)
    print(spit(parsed), end='')


main(sys.argv)