import argparse
import logging
import hashlib
import re
logging.basicConfig(level=logging.INFO)
from urllib.parse import urlparse
import nltk
#nltk.download('stopwords') #Solo se ejecuta la primera vez que se corre nltk
#nltk.download('punkt') #Solo se ejecuta la primera vez que se corre nltk
from nltk.corpus import stopwords 

import pandas as pd


logger = logging.getLogger(__name__) 
# name nombre interno que tiene python en nuestro archivo, para que sepamos que e slo que se esta ejecutando en nuestro codigo
stop_words = set(stopwords.words('spanish'))

def main(filename):
  logger.info('Start cleaning process')  #Para que nos de informacion de que es lo que esta sucediendo

  df = _read_data(filename) # 1. leer el archivo de datos
  newspaper_uid = _extract_newspaper_uid(filename) # 2. Anadir el newspaper uid es la primera palabra del arcgivo
  df = _add_newspaper_uid_column(df, newspaper_uid) #funcion para anadirlo a la columna, regresa el dataframe modificado
  df = _extract_host(df) #Ultimo paso es extraer el host del dataFrame
  df = _fill_missing_titles(df)# LLenamos los missing titles
  df = _generate_uid_for_rows(df)
  df = _remove_new_lines(df, 'title')  #limpia el body de nuestra df quitandole caracteres indeseados
  df = _remove_new_lines(df, 'body')
  df = _tokenise_column(df, 'title')
  df = _tokenise_column(df, 'body')
  df = _remove_duplicates(df)
  df = _drop_rows_with_missing_values(df)
  _save_data(df, filename)

  return df
  

def _read_data(filename):
  logger.info(f'Reading file {filename}')

  return pd.read_csv(filename, encoding = 'utf-8')
  #retornamos nuestro dataframe


def _extract_newspaper_uid(filename):
  logger.info('Extracting newspaper uid')
  newspaper_uid = filename.split('_')[0]

  logger.info(f'Newspaper uid detected: {newspaper_uid}')

  return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
  logger.info(f'Filling newspaper_uid column with {newspaper_uid}')
  df['newspaper_uid'] =  newspaper_uid # anadimos columna newspaper_uid

  return df


def _extract_host(df):
  logger.info('Extracting host from urls')
  df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)

  return df


def _fill_missing_titles(df):
  logger.info('Filling missing titles')
  missing_titles_mask = df['title'].isna()

  missing_titles = (df[missing_titles_mask]['url'].str.extract(r'(?P<missing_titles>[^/]+)$')
                      .applymap(lambda title: title.split('-'))
                      .applymap(lambda title_word_list: ' '.join(title_word_list)))

  df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']

  return df


def _generate_uid_for_rows(df):
  logger.info('Generating uids for table rows')
  uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1) #axis=1 son las filas, axis=0 columnas, hashlib.md5 funcion rtiene problemas criptograficos, pero en nuestro caso nos da un numero de 128 bit de manera hexa, al no pasarle parametros a encode() codifica en utf-8 por default
            .apply(lambda hash_object: hash_object.hexdigest())
          )

  df['uid'] = uids
  df.set_index('uid', inplace=True)  #definimos que queremos los uid como index,

  return df


def _remove_new_lines(df, column_name):
  logger.info(f'Removing new lines from {column_name}')
  stripped_body = (df
                     .apply(lambda row: row[column_name], axis=1) #recibe solo el row 'body', axis=1 son las filas, axis=0 columnas
                     .apply(lambda body: list(body)) #convertir los elementos en lista de letras
                     #.apply(lambda body: re.sub(r'(\n|\r)+', r'', body))
                     .apply(lambda letters: list(map(lambda letters: letters.replace('\n',''), letters))) # iteramos a traves de cada una de las letras, recibe las letras en una lista y reemplaza valores \n por espacio vacio, funcion map es para aplicarle funciones a los elementos especificados y lo convertivos a lista
                     .apply(lambda letters: list(map(lambda letters: letters.replace('\r',''), letters)))
                     .apply(lambda letters: list(map(lambda letters: letters.replace('¿',''), letters)))
                     .apply(lambda letters: list(map(lambda letters: letters.replace('?',''), letters)))
                     .apply(lambda letters: ''.join(letters)) #Unir todas las palabras
                  )
  df[column_name] = stripped_body

  return df


def _tokenise_column(df, column_name):
  logger.info('Tokenising {}'.format(column_name))
  tokeniser = (df
                .dropna()  # eliminamos si nos queda algo con na, porque o sino ntk falla
                .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1) # tokenise palabras,  como estamos trabajando con rows le decimos que estamos en axis 1
                #.apply(lambda body: re.sub(r'(\n|\r|\?|\?)+', r'', body))
                .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens))) #Eliminar palabras que no sean alfanumericas filter regresa iterador y lo convertimos en lista para seguir con analisis
                .apply(lambda tokens: list(map(lambda token: token.lower(), tokens))) #convertir todos los tokens a lower o upper case para compararlos con posterioridad conlos stopwords que vienen en inusculas, aqui tenemos palabras en minusculas y divididas por palabras
                .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list))) # Eliminamos las palabras que son stopwords, filter es para filtrarlas, quedamos con lista de palabras
                .apply(lambda valid_word_list: len(valid_word_list)) # No queremos una lista de palabras si no una longitud, de cuantas son               
           )

  df[f'n_tokens_{column_name}'] = tokeniser

  return df


def _remove_duplicates(df):
  logger.info('Removing duplicates')
  df.drop_duplicates(subset=['title'], keep='first', inplace=True)

  return df


def _drop_rows_with_missing_values(df):
  logger.info('Dropping rows with missing values')
  df.dropna(inplace=True)

  return df


def _save_data(df, filename):
  clean_filename = f'clean_{filename}'
  logger.info(f'Saving data at {clean_filename}')
  df.to_csv(clean_filename)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()  #preguntarle al usuario cual va a ser el archivo que queremos trabajar
  parser.add_argument('filename',
                      help='The path to the dirty data',
                      type=str)
  args = parser.parse_args() #parseamos los argumentos
  df = main(args.filename) #Se lo pasamos como argumento a funcion filename

  print(df)