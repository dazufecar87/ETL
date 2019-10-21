from sqlalchemy import create_engine # 
from sqlalchemy.ext.declarative import declarative_base # nos va permitir tener acceso a las funcionalidades de ORM(Object Relation and Mapping) nos permite trabajar con objetos de python en lugar de queries de SQL directamente
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://dazufecar87:P1C1@localhost/newspaper')# sqlite:///newspaper.db') # nuestro motor, sqlite viene dentro de nuestra libreria de python

session = sessionmaker(bind=engine) # le pasamos nuestro motor

Base = declarative_base() # clase base de la cual van a extender todos nuestros modelos
