"""
Takes a list of bills paid by multiple people and will balance them
and say who needs to pay who and how much
"""
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name

import os
import csv
import sys
import glob
import datetime
import regex
import numpy as np
import pandas as pd

USER_PATH = 'example_csv' + os.path.sep

# Utility fns
# - Numpy fns


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

# - pandas fns


def print_pd(df, max_length=0):
    """
    takes a pd data frame and prints it nicely
    obeying max_length given. ignores if 0.
    """
    row_count = df.shape[0]
    if max_length and (row_count > max_length):
        print('Table is', row_count,
              'lines long, only showing first', max_length, 'lines.')
        print(df.head(max_length))
    else:
        print(df)

# - file fns


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


def csv_write_data(filename, data, open_method):
    """
    takes a filename and data, then writes to the csv file with that and closes it
    works for one or multiple rows
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


# - other fns
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


# billbalancer specific fns
def init_file(file_path):
    """
    makes a new empty .csv file with inputted name
    In directory of file_path
    """
    while True:
        name = str(input('Enter the persons name for this file: '))
        if name:
            break
        print('Nothing entered, try again.')
    header = ['Date', 'Description', 'Value', 'Processed']
    # print(header)
    filename = file_path + 'billbalancer_' + name + '.csv'

    filenames = find_files('billbalancer_*.csv')
    for file in filenames:  # TODO make use of csv FileExistsError

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


def parse_for_name(filename):
    """
    takes a file name in the format " *_name.* " and will extract name
    e.g. billbalancer_joe.csv => joe
    """
    try:
        # have to use regex instead of re as `\k` isn't supported.
        # last underscore, match until dot.
        result = regex.search(
            '^.*_\K[^.]+', filename).group(0)  # pylint: disable=W1401
    except AttributeError:  # nothing found
        result = ''

    return result


def row_edit(df):
    """
    takes a pd df and allows for row editing. billbalancer specific
    """
    print('Full file:')
    print_pd(df)
    while True:  # checks something was entered
        try:
            row_num = int(input('Enter the row number to edit: '))
            break
        except ValueError:
            print('#### Warning: invalid option ####')

    print('Chosen row:')
    print(df.loc[[row_num]])

    print('\n~~ Column Options ~~')
    print('0 - Date')
    print('1 - Description')
    print('2 - Value')
    print('3 - Processed tag')
    while True:  # checks its valid
        try:
            col_num = int(input('Select column to edit: '))
            if 0 <= col_num <= 3:
                break
        except ValueError:
            pass
        print('#### Warning: invalid option ####')

    value = input('New value: ')
    # replaces cell with that value
    df.iat[row_num, col_num] = value

    if input('type "y" to edit more rows, leave blank to save file: '):
        return row_edit(df)
    return df


def file_edit(filename):
    """
    takes a filename and gives the user options for manipulating the file
    """
    # reads file into pd data frame.
    df = pd.read_csv(filename)

    # prints file (first 15 lines only)
    print('\nChosen file:')
    print_pd(df, 15)

    # menu - asks for manual row edit, row addition, file deletion.
    print('\n~~ Edit File Options ~~')
    print('- To manually edit a row, type "m"')
    print('- To add rows to the file, type "a"')
    print('- To permanently delete the file, type "delete"')
    print('- Leave blank to return to the main menu')
    edit_answer = input('Choice: ')
    # TODO add file renaming

    if edit_answer:
        # if nothing typed it will skip around to start of while
        if edit_answer in {'m', 'M', 'manual'}:
            print('Editing rows manually...')
            df = row_edit(df)
            print('Saving file:')
            print(df)
            df.to_csv(filename, index=False)

        elif edit_answer in {'a', 'A', 'add'}:
            print('Adding row(s) to this file')
            add_rows(filename)

        elif edit_answer in {'delete', 'Delete'}:
            print('deleting file...')
            # TODO file deletion with type name protection.

        else:
            print('#### Warning: invalid option ####')
            return file_edit(filename)
    return None


def add_rows(filename):
    """
    takes a file and will add row(s) to it with given data
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
        # TODO force non empty description.
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

        if str(input('type "n" to stop, or blank to add more rows: ')):
            # == 1 if any key is typed which ends the loop
            break  # end of: while add more rows

    csv_write_data(filename, data, 'a')


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
        return enter_date()  # prompts retry


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
        return enter_money()  # prompts retry


def csv_sum_non_processed(filename, PROCESSED=True):
    """
    takes a file name, returns a sum of all values that haven't been processed.
    PROCESSED - sets processed tag to 1, indicating it has been processed.
    """
    df = pd.read_csv(filename)
    unprocessed = df[df['Processed'] == 0]

    if PROCESSED:
        df['Processed'] = 1
        df.to_csv(filename, index=False)

    return unprocessed['Value'].sum()


def process_files(filenames):
    """
    takes a list of filenames, opens each, sums the values
    (that havent already been processed - processed tag == 0),
    returns a list with one total value per person, lines up with names
    """
    totals = []
    for filename in filenames:
        # print(filename)
        totals.append(csv_sum_non_processed(filename))
        # totals.append(csv_sum_non_processed(filename, False))
    return totals


def process_data(arr, names):
    """
    takes a numpy array (1D) and list of names
    balances the arr and determines who owes who
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
                        print(f"{abs(value):0.2f}")  # formats +ve, .XX
    # TODO print no change if nothing needs doing.
    # TODO could return a matrix (arr) of who owes who


if __name__ == "__main__":
    print('################ Running Main ###############')
    # TODO revamp menu with a qt gui system?
    # learn qt first with https://realpython.com/python-pyqt-gui-calculator/
    # then implement the stuff in here.

    # choose file path
    while True:
        print('\n~~ File Path Options ~~')
        print('- To load example files, type "e"')
        print('- To load a code defined folder, type "c"')
        print('- To use the current directory, leave blank')
        path_answer = str(input('Choice: '))
        if path_answer:
            if path_answer in {'e', 'E', 'example'}:
                print('Using example files...')
                FILE_PATH = 'example_csv' + os.path.sep

            elif path_answer in {'c', 'C', 'code'}:
                print('Using Code defined folder. To edit, modify USER_PATH')
                FILE_PATH = USER_PATH

            else:
                print('#### Warning: invalid option ####', end='\n\n')
                continue

        else:
            FILE_PATH = ''

        break

    while True:
        filenames = find_files(FILE_PATH + 'billbalancer_*.csv')
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
                PERSON_NAME = init_file(FILE_PATH)
                FILENAME = FILE_PATH + 'billbalancer_' + PERSON_NAME + '.csv'
                if str(input('type "y" to add rows to this file, or blank to exit: ')):
                    add_rows(FILENAME)
                    continue
            # otherwise exit
            break

        # main menu
        print('\n~~ Main Menu Options ~~')
        print('- Type a file number to edit the file')
        print('- To create a new file, type "n"')
        print('- To balance all outstanding bills, type "b"')
        print('- Leave blank to quit')
        answer = input('Choice: ')

        if answer:  # not left blank
            if is_integer(answer):
                # now editing the chosen file
                # note: was type str from input.
                file_edit(filenames[int(answer)])

            elif answer in {'n', 'N', 'new'}:
                print('Creating a new file')
                PERSON_NAME = init_file(FILE_PATH)
                FILENAME = FILE_PATH + 'billbalancer_' + PERSON_NAME + '.csv'
                if str(input('type "y" to add rows to this file, or blank to continue: ')):
                    add_rows(FILENAME)

            elif answer in {'b', 'B', 'balance'}:
                bills_to_balance = process_files(filenames)
                process_data(bills_to_balance, names)
                print('Returning to main menu...')
                str(input('Press enter to continue'))

            else:
                print('#### Warning: invalid option ####')

        else:
            break
