from databasedata import engine
from sqlalchemy import Column, Integer, ForeignKey, Text, VARCHAR
from sqlalchemy.orm import declarative_base,relationship

table_base = declarative_base()

class contactstable(table_base): # contacts Table
    __tablename__ = 'contactstable'
    contactId = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    firstName = Column(VARCHAR(25))
    lastName = Column(VARCHAR(25))
    notes = Column(Text)
    companyName = Column(VARCHAR(50))
    jobTitle = Column(VARCHAR(30))
    relation = relationship("contactemails", back_populates="contactstable", cascade="all, delete", passive_deletes=True)
    relation = relationship("contactphones", back_populates="contactstable", cascade="all, delete", passive_deletes=True)



class contactemails(table_base): # contact emails Table
    __tablename__ = 'contactemails'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    contactId = Column(Integer, ForeignKey("contactstable.contactId"))
    type = Column(VARCHAR(25))
    emailValue = Column(Text)
    childrelation = relationship("contactstable", back_populates="contactemails")


class contactphones(table_base): # contact numbers Table
    __tablename__ = 'contactphones'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    contactId = Column(Integer, ForeignKey("contactstable.contactId"))
    type = Column(VARCHAR(25))
    phoneNumber = Column(VARCHAR(15))
    childrelation = relationship("contactstable", back_populates="contactphones")

table_base.metadata.create_all(engine)
