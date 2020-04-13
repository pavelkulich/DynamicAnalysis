from sqlalchemy import create_engine
from termcolor import colored
import pandas as pd

from db_schema import Base, DataTable, Locations, Trains, MetaTable
import db_config as cfg

# Global Variables
SQLITE = 'sqlite'


class DBManager:
    DB_ENGINE = {
        SQLITE: 'sqlite:///db/{DB}'
    }

    db_engine = None

    def __init__(self, dbtype, dbname=''):
        dbtype = dbtype.lower()
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
            self.db_engine = create_engine(engine_url, echo=False)
            print(self.db_engine)
        else:
            print("DBType is not found in DB_ENGINE")

    def create_db_tables(self):
        Base.metadata.create_all(self.db_engine)

    def get_all_table_data(self, table):
        with self.db_engine.connect() as connection:
            query = connection.execute(f'SELECT * FROM {table}')
            data = query.fetchall()
        return data

    def get_column_from_table(self, col, table):
        with self.db_engine.connect() as connection:
            query = connection.execute(f'SELECT {col} FROM {table}')
            data = query.fetchall()
        return data

    def get_max_id(self, table):
        with self.db_engine.connect() as connection:
            query = connection.execute(f'SELECT MAX("id") FROM {table}')
            data = query.fetchone()
        return data

    def get_item_index(self, item, table):
        if table == cfg.LOCATIONS:
            column = 'location'
        elif table == cfg.TRAINS:
            column = 'train'
        else:
            return

        with self.db_engine.connect() as connection:
            query = connection.execute(f'SELECT id FROM {table} WHERE {column} = "{item}"')
            index = query.fetchone()
        return index


class DBImporter(DBManager):
    def insert_data(self, data: list, table=''):
        if table == '':
            print('Table has not bees specified!')
        elif table == cfg.DATATABLE:
            df = pd.DataFrame(data,
                              columns=DataTable.__table__.columns.keys()[1::])
            try:
                df.to_sql(cfg.DATATABLE, con=self.db_engine, index=False, if_exists='append')
                print(colored('Data inserted!', 'yellow'))
                print('************************')
                return True
            except Exception as e:
                print('Data not inserted. Probably inappropriate number of columns.')
                print('Please check number of columns and columns names.')
                print(e)
                return False

        elif table == cfg.TRAINS:
            df = pd.DataFrame(data,
                              columns=Trains.__table__.columns.keys()[1::])
            df.to_sql(cfg.TRAINS, con=self.db_engine, index=False, if_exists='append')
        elif table == cfg.LOCATIONS:
            df = pd.DataFrame(data,
                              columns=Locations.__table__.columns.keys()[1::])
            df.to_sql(cfg.LOCATIONS, con=self.db_engine, index=False, if_exists='append')
        elif table == cfg.METATABLE:
            df = pd.DataFrame(data,
                              columns=MetaTable.__table__.columns.keys()[1::])
            df.to_sql(cfg.METATABLE, con=self.db_engine, index=False, if_exists='append')
        else:
            print('Table does not exists!')

    def delete_last_row(self, table):
        index = self.get_max_id(table)[0]
        if index > 0:
            with self.db_engine.connect() as connection:
                connection.execute(f'DELETE FROM {table} WHERE "id" = {index}')

    @staticmethod
    def get_column_names(table=''):
        if table == cfg.DATATABLE:
            return DataTable.__table__.columns.keys()[1:-1]
        elif table == cfg.METATABLE:
            return MetaTable.__table__.columns.keys()[1::]
        else:
            return None


class DBExporter(DBManager):
    pass
