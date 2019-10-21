import argparse #para convertir en un script ejecutable
import logging
logging.basicConfig(level=logging.INFO)

import pandas as pd
from article import Article
from base import Base, engine, session

from sqlalchemy.exc import DBAPIError

logger = logging.getLogger(__name__)


def main(filename):
  Base.metadata.create_all(engine) #Permite generar schema en nuestra db, Generar codigo bolder plate para poder configurar SQL alchemy en las bses de datos SQL normalmente se usan el concepto de sesion y de schema para poder determinar como estructura nuestros datos
  Session = session() # inicializar nuestra session
  articles = pd.read_csv(filename) # leemos articulos con pandas

  print(len(articles))
  for index, row in articles.iterrows(): #metodo de pandas que se llama iterrows, permite generar un loop adentro de cada una de nuestras filas de nuestra dataFrame
    #print(len(row)
    logger.info(f'Loading article uid {row["uid"]} into DB')
    article = Article(row['uid'],
                      row['body'],
                      row['host'],
                      row['newspaper_uid'],
                      row['n_tokens_body'],
                      row['n_tokens_title'],
                      row['title'],
                      row['url'])

    Session.add(article) # esto mete nuestro articulo a la DB
  
  #try:
  Session.commit()
  # except (DBAPIError) as e:
  #   logger.warning('Error loading article', exc_info=False)
  
  Session.close()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('filename',
                       help='The file you want to load into the db',
                       type=str)

  args = parser.parse_args()

  main(args.filename)