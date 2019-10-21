import yaml


__config = None


def config():
  global __config
  if not __config:
    with open('config.yaml', mode='r') as f:
      __config = yaml.safe_load(f)
  #print(__config)
  return __config

if __name__ == '__main__':
  ensayo = config()['news_sites']['elpais']
  print(ensayo)
#   print(ensayo['article_body'])
#   print(ensayo['article_body'])