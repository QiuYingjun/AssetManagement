from sqlalchemy import Column, String, create_engine, Integer, Date, Float, ForeignKey, MetaData, text, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///../data/asset.db', echo=True, connect_args={"check_same_thread": False})
DBSession = sessionmaker(bind=engine)
Base = declarative_base()
session = DBSession()


class Asset(Base):
    __tablename__ = 'asset'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    date = Column(Date, nullable=False)
    accountId = Column(Integer, ForeignKey('account.id'))
    amount = Column(Float, nullable=False, default=0)


class Account(Base):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String(20))
    currency = Column(String(5))
    is_active = Column(Boolean)


class FXRate(Base):
    __tablename__ = 'fx_rate'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    date = Column(Date, nullable=False)
    rate = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
