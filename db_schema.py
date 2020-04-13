from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean

import db_config as cfg

Base = declarative_base()


class DataTable(Base):
    __tablename__ = cfg.DATATABLE
    id = Column('id', Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    time = Column('time', Float, nullable=False)
    dat1 = Column('s0-hp_1-s0', Float, nullable=False)
    dat2 = Column('s1-k1_1-s1', Float, nullable=False)
    dat3 = Column('s2-k2_1-s2', Float, nullable=False)
    dat4 = Column('s3-p1_3-s3', Float, nullable=False)
    dat5 = Column('s4-p2_3-s4', Float, nullable=False)
    dat6 = Column('s5-k3_2-s5', Float, nullable=False)
    dat7 = Column('s6-k4_2-s6', Float, nullable=False)
    dat8 = Column('s7-hp_2-s7', Float, nullable=False)
    dat9 = Column('az_kl1', Float, nullable=False)
    dat10 = Column('az_p1', Float, nullable=False)
    dat11 = Column('az_k1', Float, nullable=False)
    dat12 = Column('az_pstred', Float, nullable=False)
    dat13 = Column('az_k2', Float, nullable=False)
    dat14 = Column('az_p2', Float, nullable=False)
    dat15 = Column('az_kl2', Float, nullable=False)

    meta_id = Column('meta_id', Integer, ForeignKey(f'{cfg.METATABLE}.id'), nullable=False)

    def __repr__(self):
        return '<Accel model {}>'.format(self.id)


class MetaTable(Base):
    __tablename__ = cfg.METATABLE

    id = Column('id', Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    date = Column('date', String, nullable=False)
    location_id = Column('location_id', Integer, ForeignKey(f'{cfg.LOCATIONS}.id'), nullable=False)
    track = Column('track', Integer, nullable=False)
    train_id = Column('train_id', Integer, ForeignKey(f'{cfg.TRAINS}.id'), nullable=False)
    usp = Column('usp', Boolean, nullable=False)
    crossing = Column('crossing', Boolean, nullable=False)
    filename = Column('filename', String, nullable=False)

    def __repr__(self):
        return '<Train model {}>'.format(self.id)


class Trains(Base):
    __tablename__ = cfg.TRAINS

    id = Column('id', Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    train = Column('train', String, nullable=False, unique=True)

    def __repr__(self):
        return '<Train model {}>'.format(self.id)


class Locations(Base):
    __tablename__ = cfg.LOCATIONS

    id = Column('id', Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    location = Column('location', String, nullable=False, unique=True)

    def __repr__(self):
        return '<Locations model {}>'.format(self.id)
