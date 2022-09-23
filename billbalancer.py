"""
Takes a list of bills paid by multiple people and will balance them
and say who needs to pay who and how much
"""

import csv
import sys
import glob
import datetime
import re
import numpy as np

# pylint: disable=redefined-outer-name


def num_col(arr):
    """
    takes a numpy array and will return the number of columns.
    for 1D this is [0]
    for 2D this is [1]
    for 3D this should be [2] etc.
    Not fully tested!
    """
    # ensures its a numpy array before performing np operations on it.
    arr = np.asarray(arr)
    return arr.shape[arr.ndim - 1]


def process_data(arr, names):
    """
    takes a numpy array (1D) and converts it to comparison to average.
    """
    num_ppl = num_col(arr)

    total = np.sum(arr)
    average = total / num_ppl
    rel_to_avg = arr - average  # np arr of diff to avg

    # sum of all values in rel to avg > 0.
    sum_positive = rel_to_avg[rel_to_avg > 0].sum()

    # receive_money_weight is a percentage 0 -> 1.
    receive_money_weight = np.empty((num_ppl))
    for i in range(0, num_ppl):
        if rel_to_avg[i] > 0:
            receive_money_weight[i] = rel_to_avg[i] / sum_positive
        else:
            receive_money_weight[i] = 0

    # calculate who owes who what and prints it.
    # TODO add useful comments
    for i in range(0, num_ppl):
        if rel_to_avg[i] < 0:
            for j in range(0, num_ppl):
                if j != i:
                    value = abs(rel_to_avg[i] * receive_money_weight[j])

                    if value > 0:
                        print(names[i], 'owes', names[j], '£', end='')
                        print(f"{abs(value):0.2f}")  # format +ve, .XX

    # return rel_to_avg
    # TODO could return a matrix (arr) of who owes who


def parse_for_name(filename):
    """
    takes a file name in the format " *_name.* " and will extract name
    e.g. billbalancer_joe.csv => joe
    """
    try:
        result = re.search(
            '(?<=_).*(?=\.)', filename).group(0)  # pylint: disable=W1401
    except AttributeError:  # nothing found
        result = ''

    return result


def csv_write_data(filename, data, open_method):
    """
    takes a filename and data, then writes to the csv file with that and closes it
    """
    # uses numpy to find the dimension of the list (of possibly lists)
    data_np = np.asarray(data)
    ndim = np.ndim(data_np)
    # print(ndim)

    # open and write to file
    with open(filename, open_method, encoding='UTF8', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # check dimension before writing with a function
        if ndim == 1:
            writer.writerow(data)
        elif ndim == 2:
            writer.writerows(data)
        else:
            print('unknown number of dimensions: ', ndim)
            sys.exit()

        csv_file.close()


def init_file():
    """
    makes a new empty .csv file with inputted name in current dir.
    """
    # TODO check something was entered (name not blank)
    name = str(input('Enter the persons name for this file: '))
    header = ['Date', 'Description', 'Value', 'Processed']
    # print(header)
    filename = 'billbalancer_' + name + '.csv'

    filenames = find_files('billbalancer_*.csv')
    for file in filenames:

        # file matches one already in directory
        if file == filename:
            input_text = '\n' + 'a file with this name already exists!' + \
                '\n' + 'type "y" to overwrite, leave blank to cancel: '
            overwrite_decision = str(input(input_text))

            if overwrite_decision == "y":
                print('overwriting file')
                break

            print('not overwriting file')
            # no file being initialised so exit.
            return name

    csv_write_data(filename, header, 'w')
    return name


def enter_date():
    """
    prompts user to enter the desired date which is returned
    """
    date_message = ['year', 'month', 'day']
    date_entry = []
    current_date = datetime.date.today()
    current_date = [current_date.year, current_date.month, current_date.day]
    # print(current_date)
    try:
        for i in range(3):
            print('leave blank for current', date_message[i], end=' ')
            print('(', current_date[i], ')', sep='')
            print('enter', date_message[i], '(int): ', end='')
            date_tmp = input()
            if date_tmp:
                date_entry.append(int(date_tmp))
            else:
                date_entry.append(current_date[i])

        return datetime.date(date_entry[0], date_entry[1], date_entry[2])

    except ValueError:
        print('value entered out of range, enter a valid date!')
        return enter_date()


def enter_money():
    """
    prompts user to enter a money value and returns it,
    errors for too many dp and non numbers -> forces retry
    """
    try:
        value = float(input('Enter value of bill (£): £'))

        # checks number of dp
        if len(str(value).split('.')[1]) <= 2:
            return value

        print('warning: enter a value with less than 2dp')
        return enter_money()

    except ValueError:
        print('warning: please enter a number')
        print('note: XX, XX.X, XX.XX are all valid')
        return enter_money()


def add_rows(filename):
    """
    takes a person name and will find the file and add row(s) to it with given data
    """
    data = []
    description = ''

    # input data (date, description, value, processed)
    # (processed: a tag that goes to 1 when bills have been balanced to that point)
    while True:  # start of: while add more rows

        # date
        date = enter_date()
        # print(date)

        # description
        if description:
            input_text = 'leave blank to reuse last description ("' + description + '")' + \
                '\n' + 'or enter a description of the bill: '
        else:
            input_text = 'enter a description of the bill: '
        temp_description = str(input(input_text))
        # if left blank ^ it will reuse the last one, otherwise writes new.
        if temp_description:
            description = temp_description

        # value
        value = enter_money()

        # add row to the data list (of lists)
        data.append([date, description, value, 0])

        # == 1 if any key is typed which ends the loop
        if str(input('type "n" to stop, or blank to add more rows: ')):
            break  # end of: while add more rows

    csv_write_data(filename, data, 'a')


def find_files(query):
    """
    takes the search query and looks for all files in the current dir that matches it
    and returns a list with the names of them.
    """
    filenames = []
    for filename in glob.glob(query):
        filenames.append(filename)
    # print(filenames)
    return filenames


def print_list(plist, INDEX=False):  # pylint: disable=c0103
    """
    takes a list and prints it one element / line in the terminal.
    INDEX: optionally will print a number by each element
    """
    for i, value in enumerate(plist):
        if INDEX:
            print(i, ':', end=' ')
        print(value)


def process_files(filenames):
    """
    takes a list of filenames, opens each, sums the values
    (that havent already been processed - processed tag == 0),
    returns a list with one total value per person, lines up with filenames
    """
    totals = []
    for filename in filenames:
        # print(filename)
        values = np.asarray(csv_read_non_processed_values(filename))
        totals.append(np.sum(values))
    return totals


def csv_read_non_processed_values(filename):
    """
    takes a file name, extracts column 3 for all where col 4 is 0, returns a list
    col 3 = value, col 4 = processed tag
    """
    values = []
    with open(filename, 'r', encoding='UTF8', newline='') as data_file:
        reader = csv.reader(data_file)

        # skips header
        next(reader, None)

        for row in reader:
            # print(row[2], row[3])
            if row[3] == '0':
                values.append(float(row[2]))
                # TODO write flag to 1 as now processed

    return values


def is_integer(test_string):
    """
    checks a string to see if it's an int or not
    credit: https://note.nkmk.me/en/python-check-int-float/
    """
    try:
        float(test_string)
    except ValueError:
        return False
    else:
        return float(test_string).is_integer()


if __name__ == "__main__":
    print('################ Running Main ###############')
    # TODO revamp menu with a qt gui system?

    while True:
        filenames = find_files('billbalancer_*.csv')
        names = []
        for filename in filenames:
            names.append(parse_for_name(filename))

        # TODO offset this so the file numbers start from 1 not 0.
        if names:
            print('\nExisting files in directory:')
            print_list(names, INDEX=True)
        else:
            print('No files found')

            # create file?
            if str(input('Type "y" to create a new file, leave blank to exit: ')):
                PERSON_NAME = init_file()
                FILENAME = 'billbalancer_' + PERSON_NAME + '.csv'
                if str(input('type "y" to add rows to this file, or blank to exit: ')):
                    add_rows(FILENAME)
                    continue
            # otherwise exit
            break

        print('\nOptions:')
        print('- Type a file number to edit the file')
        print('- To create a new file, type "n"')
        print('- To balance all outstanding bills, type "b"')
        print('- Leave blank to quit')
        answer = input('Choice: ')

        # TODO tidy up the numerous `continue`  and `break`
        if answer:  # not left blank
            if is_integer(answer):
                answer = int(answer)

                # TODO allow for proper file editing:
                # printing of file (if not too long, two parts?)
                # editing rows (inc mark/unmark processed)
                # deleting file
                # or adding rows.


                # add rows to that file
                add_rows(filenames[answer])

            elif answer in {'n', 'N', 'new'}:
                print('Creating a new file')
                PERSON_NAME = init_file()
                FILENAME = 'billbalancer_' + PERSON_NAME + '.csv'
                if str(input('type "y" to add rows to this file, or blank to continue: ')):
                    add_rows(FILENAME)

            elif answer in {'b', 'B', 'balance'}:
                bills_to_balance = process_files(filenames)
                process_data(bills_to_balance, names)
                if str(input('Type "y" to continue, leave blank to exit: ')):
                    continue
                break

            else:
                print('#### Warning: invalid option ####')

        else:
            break
