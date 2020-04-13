from glob import glob
from datetime import datetime as dt
from termcolor import colored
from tkinter import filedialog
import click
import pandas as pd

from db_manager import DBImporter
import db_config as cfg

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)

################
# those variables need to be set
# also need to be set variable YEAR in db_config
LOCATION = 'Planá nad Lužnicí'  # measuring location
USP = True  # under sleeper pads
CROSSING = False  # measured at crossing
TRACK = 1  # measured track
#################

DUPLICITYCHECK = True  # Check if file is imported yet
SEPARATOR = '\t'


class Importer:

    def __init__(self, location: str, usp: bool, crossing: bool, track: int):
        self.location = location
        self.usp = usp
        self.crossing = crossing
        self.track = track
        self.db = DBImporter(dbtype='sqlite', dbname='avut_db.sqlite')
        self.db.create_db_tables()
        self.path = None
        self.filename = None

    def import_data(self, extension='.txt', sep=';'):

        # path = filedialog.askdirectory()
        files = glob(f'D:\Pavel\Repos\DynamicAnalysis\data\*{extension}')

        # files = glob(f'{path}\*{extension}')

        # Function prevents data duplicity
        def _check_duplicity():
            print(colored('Checking duplicity', "yellow"))
            mdata = self.db.get_column_from_table('filename', cfg.METATABLE)
            mdata_list = [item[0] for item in mdata]
            if mdata:
                filename = file.split('\\')[-1]
                if filename in list(mdata_list):
                    return True

            return False

        # Function repairs unpaired columns
        def _repair_columns():
            print(colored('Start column repairing...', "yellow"))
            while len(unmatched_cols):
                for unmatched in unmatched_cols:
                    for i in range(len(old_columns)):
                        print(f'{i} - {old_columns[i]}')
                    while True:
                        index = click.prompt(f'Link value to {unmatched} by index', type=int)
                        if index < len(old_columns):
                            break
                        print(colored('Invalid index, try again!', "red"))

                    data.rename(columns={old_columns[index]: unmatched_cols[index]}, inplace=True)
                    unmatched_cols.pop(index)
                    old_columns.pop(index)

        for file in files:
            if DUPLICITYCHECK:
                if _check_duplicity():
                    print('File already imported!')
                    continue
                print(colored('File is not duplicit. Import starts.', "yellow"))

            self.filename = file
            if extension == '.txt' or '.csv':
                data = pd.read_csv(file, sep=sep).dropna(axis='columns')
                print(data)
                print(f'In file: {file}')
                abort = False
                while True:
                    answ = click.prompt('Does data look correct? y/n', type=str, default='y')
                    if answ == 'y':
                        break
                    elif answ == 'n':
                        abort = True
                        break

                if abort:
                    print(colored('Skipping incorrect data!', 'red'))
                    print('************************')
                    continue

            else:
                print(f'File type not implementer! Please implement reading extension {extension}')
                break

            old_columns = list(data.columns)
            new_columns = []
            for column in old_columns:
                if '[' in column:
                    end = column.find('[')
                    new_column = column[:end].replace(' ', '').lower()
                else:
                    new_column = column.replace(' ', '').lower()

                new_columns.append(new_column)

            table_columns = DBImporter.get_column_names(cfg.DATATABLE)

            unmatched_cols = []
            for table_column in table_columns:
                # if column names match
                if table_column in new_columns:
                    idx = new_columns.index(table_column)
                    data.rename(columns={old_columns[idx]: new_columns[idx]}, inplace=True)
                    old_columns.pop(idx)
                    new_columns.pop(idx)

                else:
                    unmatched_cols.append(table_column)

            # if there are unpaired columns
            if len(unmatched_cols):
                _repair_columns()

            if len(data.columns) != len(table_columns):
                print(colored('Number of DB columns do not match with number of data columns', 'red'))
                print('************************')
                continue

            for idx in range(len(old_columns)):
                data.rename(columns={old_columns[idx]: new_columns[idx]}, inplace=True)

            new_data = data.loc[:, data.columns.isin(table_columns)].copy()

            if new_data.size:
                metatable_id = self.db.set_metatable_data(location=self.location, date=self._get_date(),
                                                                  track=self.track,
                                                                  train=self._get_train(), usp=self.usp,
                                                                  crossing=self.crossing,
                                                                  filename=self.filename.split('\\')[-1])

                new_data['meta_id'] = metatable_id

                if self.db.insert_data(new_data, cfg.DATATABLE):
                    continue

            # delete metadata if new_data not inserted
            self.db.delete_last_row(cfg.METATABLE)

    # returns location id of self.location
    def _get_item_index(self, table):
        if table == cfg.LOCATIONS:
            attribute = self.location
        elif table == cfg.TRAINS:
            attribute = self._get_train()
        else:
            return None

        attributes = self.db.get_all_table_data(table)
        if not attributes:
            self.db.insert_data([attribute], table)
            return 1

        for index, item in attributes:
            if attribute == item:
                return index

        self.db.insert_data([attribute], table)
        index = self.db.get_item_index(attribute, table)[0]
        return index

    # returns datetime
    def _get_date(self):
        file_list = self._split_filename()
        date = f'{file_list[4]}/{file_list[3]}/{file_list[2]}'
        while True:
            print(f'Date: {colored(date, "yellow")}')
            answ = click.prompt(f'Does date look correct? y/n', type=str, default='y')
            if len(answ) == 0:
                answ = 'y'
            if answ == 'y':
                break
            elif answ == 'n':
                day = click.prompt(f'Enter day', type=int)
                month = click.prompt(f'Enter month', type=int)
                year = click.prompt(f'Enter year', type=int)
                date = dt(year, month, day).strftime("%d/%m/%Y")
                print('########################')

        return date

    def _get_train(self):
        file_list = self._split_filename()
        train = file_list[1]
        while True:
            print(f'Train: {colored(train, "yellow")}')
            answ = click.prompt(f'Does train look correct? y/n', type=str, default='y')
            if len(answ) == 0:
                answ = 'y'
            if answ == 'y':
                break
            elif answ == 'n':
                train = click.prompt(f'Enter train label', type=str)
                print('########################')

        return train

    def _split_filename(self):
        filename = self.filename.split('\\')[-1]
        file_list = filename.split('_')
        return file_list


if __name__ == '__main__':
    importer = Importer(location=LOCATION, usp=USP, crossing=CROSSING, track=TRACK)
    importer.import_data(sep=SEPARATOR)
