import logging
logging.basicConfig(level=logging.INFO)

import subprocess #Es parte de libreria estandar de python y permite manipular archivos de terminal, tner terminal directamente en python


logger = logging.getLogger(__name__)
news_sites_uids = ['eluniversal', 'elpais']#, 'elpaisco']


def main():
  _extract()
  _transform()
  _load()


def _extract():
  for news_site_uid in news_sites_uids: #iteramos en cada uno de los newsites
    logger.info(f'Starting extract process for {news_site_uid}')
    subprocess.run(['python3', 'main.py', news_site_uid], cwd='./extract')  # correr subprocesos definir en python lo que hacemos en consola cwd, current working directory en carpeta de extract
    subprocess.run(['find', '.', '-name', f'{news_site_uid}*',  #dir windows, find, '.', '-name' linux, mover los archivos que se generaron por eso usamos find a partir de este directorio . que encuentre algo con cierto patron, el patron es nuestro newssite uid eso es lo que significa el asterisco
                    '-exec', 'cp', f'{news_site_uid}', f'../transform/{news_site_uid}_.csv', #queremos que ejecute mv moverlos {} nombre del archivo a directorio transform {} con nombre newssite.csv
                    ';'], cwd='./extract') #find le decimos que termine con un ';' 
    logger.info(f'{news_site_uid} moved to transform folder ') 


def _transform():
  logger.info('Starting transform process')
  for news_site_uid in news_sites_uids:
    dirty_data_filename = f'{news_site_uid}_.csv'
    clean_data_filename = f'clean_{dirty_data_filename}'
    subprocess.run(['python3', 'main.py', dirty_data_filename], cwd='./transform')
    #subprocess.run(['rm', dirty_data_filename], cwd='./transform') #Limpieza, eliminar el archivo sucio
    subprocess.run(['cp', clean_data_filename, f'../load/{news_site_uid}.csv'], cwd='./transform') #moverlo dentro de nuestro pipeline donde lo vamos a cargar a nuestro sistema de datos


def _load():
  logger.info('Starting load process')
  for news_site_uid in news_sites_uids:
    clean_data_filename = f'{news_site_uid}.csv'
    subprocess.run(['python3', 'main.py', clean_data_filename], cwd='./load')
    #subprocess.run(['rm', clean_data_filename], cwd='./load') #Limpieza, eliminar el archivo sucio


if __name__ == '__main__':
  main()