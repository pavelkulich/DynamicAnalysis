from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
            Session = sessionmaker(bind=self.db_engine)
            self.session = Session()
        else:
            print("DBType is not found in DB_ENGINE")

    def get_session(self):
        return self.session

    def create_db_tables(self):
        Base.metadata.create_all(self.db_engine)

    def insert_train(self):
        train1 = Trains(train="Rychlik")
        train2 = Trains(train="Osobak")

        self.session.bulk_save_objects([train1, train2])
        self.session.commit()

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
        else:
            print('Table does not exists!')

    def delete_last_row(self, table):
        index = self.get_max_id(table)[0]
        if index > 0:
            with self.db_engine.connect() as connection:
                connection.execute(f'DELETE FROM {table} WHERE "id" = {index}')

    def set_metatable_data(self, location, date, track, train, usp, crossing, filename):
        location_obj = self.session.query(Locations).filter(Locations.location == location).first()
        if not location_obj:
            location_obj = Locations(location=location)
            self.session.add(location_obj)

        train_obj = self.session.query(Trains).filter(Trains.train == train).first()
        if not train_obj:
            train_obj = Trains(train=train)
            self.session.add(train_obj)

        metatable = MetaTable(date=date, location=location_obj, track=track, train=train_obj, usp=usp,
                              crossing=crossing, filename=filename)

        self.session.add(metatable)
        self.session.commit()

        return metatable.id

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

