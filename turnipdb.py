from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date\
        , ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import config

engine = create_engine('sqlite:///%s' % config.SQLITE_PATH)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User( Base ):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    discord_id = Column( String(32) )
    friend_code = Column( String(32) )
    island_name = Column( String(32) )
    prices = relationship( 'Price', back_populates="user" )

class Price( Base ):
    __tablename__ = "prices"

    id = Column(Integer, primary_key = True)
    is_sell_price = Column(Boolean, default = False)
    is_am_price = Column(Boolean, default = False)
    date = Column(Date)
    price = Column(Integer)
    comment = Column( String( 64 ) )
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates="prices")

Base.metadata.create_all( engine )
