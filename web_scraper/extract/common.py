import yaml


__config = None

# Codigo para cargar estructura de config.yaml
def config():
  global __config
  if not __config:
    with open('config.yaml', mode='r') as f:
      __config = yaml.safe_load(f)

  return __config
