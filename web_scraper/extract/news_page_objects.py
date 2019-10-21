import bs4
import requests

from common import config


class NewsPage:
  
  def __init__(self, news_site_uid, url):
    self._config = config()['news_sites'][news_site_uid] # self._config = base de periodico
    self._queries = self._config['queries'] # Accede a las queries segun periodico definido
    self._html = None
    self._url = url

    self._visit(url) 


  def _select(self, query_string):
    return self._html.select(query_string) # extrae de html la parte de query_string


  def _visit(self, url): # aplicacion de beautiful soup para extraer html de la pagina en url
    response = requests.get(url)

    response.raise_for_status()

    self._html = bs4.BeautifulSoup(response.text, 'html.parser')


class HomePage(NewsPage): # Es una clase que hereda de NewsPage

  def __init__(self, news_site_uid, url):
    super().__init__(news_site_uid, url)

  
  @property
  def article_links(self): # Se retornan los links de los articulos de la pagina principal
    link_list = []
    # Va a _select para traer los links href relacionados con titulos de la pagina
    for link in self._select(self._queries['homepage_article_links']):
      if link and link.has_attr('href'):
        link_list.append(link)

    return set(link['href'] for link in link_list)


class ArticlePage(NewsPage): # Clase que hereda de NewsPage

  def __init__(self, news_site_uid, url):
    super().__init__(news_site_uid, url)


  @property
  def body(self): 
    # Va a _select y trae el cuerpo del articulo
    result = self._select(self._queries['article_body'])

    #Se retorna el texto mientras exista
    return result[0].text if len(result) else ''

  @property
  def title(self):
    # Va a _select y trae el titulo del articulo
    result = self._select(self._queries['article_title'])

    #Se retorna el texto del titulo mientras exista
    return result[0].text if len(result) else ''


  @property
  def url(self):
    result = self._url

    #Retorna el url de la pagina
    return result
