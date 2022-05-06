#!/usr/bin/python3




# Imports
import os
import sys
import argparse
import logging
import configparser
import requests




# Local imports
# (Can't use relative imports because this is a top-level script)
import edgecase_client




# Shortcuts
isfile = os.path.isfile
isdir = os.path.isdir
join = os.path.join
basename = os.path.basename
edgecase_article = edgecase_client.submodules.edgecase_article
stateless_gpg = edgecase_article.edgecase_article.submodules.stateless_gpg
gpg = stateless_gpg.gpg




# Set up logger for this module. By default, it produces no output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.ERROR)
log = logger.info
deb = logger.debug




# Settings
time_to_wait = 3  # seconds
edgecase_public_key_file_name = 'edgecase_datafeed_2_public_key.txt'
domain = 'edgecase.net'




# Shortcuts
ttw = time_to_wait




def setup(
    log_level = 'error',
    debug = False,
    log_timestamp = False,
    log_file = None,
    ):
  logger_name = 'cli'
  # Configure logger for this module.
  edgecase_client.util.module_logger.configure_module_logger(
    logger = logger,
    logger_name = logger_name,
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_file = log_file,
  )
  deb('Setup complete.')
  # Configure logging levels for edgecase_client package.
  # By default, without setup, it logs at ERROR level.
  # Optionally, the package could be configured here to use a different log level, by e.g. passing in 'error' instead of log_level.
  edgecase_client.setup(
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_file = log_file,
  )
  # Set edgecase_article logger to always be ERROR.
  edgecase_client.submodules.edgecase_article.setup(
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_file = log_file,
  )




def main():

  # Note: We use camelCase for option names because it's faster to type.

  parser = argparse.ArgumentParser(
    description='Command-Line Interface (CLI) for using the edgecase_client package.'
  )

  parser.add_argument(
    '-t', '--task',
    help="Task to perform (default: '%(default)s').",
    default='hello',
  )

  parser.add_argument(
    '-f', '--articleFile', dest='article_file',
    help="Path to article file (default: '%(default)s').",
    default='drafts/article.txt',
  )

  parser.add_argument(
    '-n', '--name',
    help="Name of article, page, or draft (default: '%(default)s').",
    default=None,
  )

  parser.add_argument(
    '--publicKeyDir', dest='public_key_dir',
    help="Path to directory containing public keys (default: '%(default)s').",
    default='../keys/public_keys',
  )

  parser.add_argument(
    '--privateKeyDir', dest='private_key_dir',
    help="Path to directory containing private keys (default: '%(default)s').",
    default='../keys/private_keys',
  )

  parser.add_argument(
    '-o', '--outputDir', dest='output_dir',
    help="Specify an output directory. (default: '%(default)s').",
    default='signed_articles',
  )

  parser.add_argument(
    '-l', '--logLevel', type=str, dest='log_level',
    choices=['debug', 'info', 'warning', 'error'],
    help="Choose logging level (default: '%(default)s').",
    default='error',
  )

  parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help="Sets logLevel to 'debug'. This overrides --logLevel.",
  )

  parser.add_argument(
    '-s', '--logTimestamp', dest='log_timestamp',
    action='store_true',
    help="Choose whether to prepend a timestamp to each log line.",
  )

  a = parser.parse_args()


  # Check and analyse arguments
  if a.task == 'uploadDraft':
    if not a.article_file:
      msg = "To use the 'uploadDraft' task, need to specify the path to the articleFile."
      raise ValueError(msg)

  if a.task == 'deleteDraft':
    if not a.name:
      msg = "To use the 'deleteDraft' task, need to specify the name of the draft."
      raise ValueError(msg)

  if a.task in 'uploadDraft signDraft'.split():
    if not isfile(a.article_file):
      msg = "File not found at path: {}".format(a.article_file)
      raise FileNotFoundError(msg)
    if not isdir(a.public_key_dir):
      msg = "Directory not found at publicKeyDir {}".format(repr(a.public_key_dir))
      raise FileNotFoundError(msg)
    if not isdir(a.private_key_dir):
      msg = "Directory not found at privateKeyDir {}".format(repr(a.private_key_dir))
      raise FileNotFoundError(msg)

  if a.task == 'signDraft':
    if not isdir(a.output_dir):
      os.makedirs(a.output_dir)


  # Derive new arguments
  edgecase_public_key_file = join(a.public_key_dir, edgecase_public_key_file_name)
  if not isfile(edgecase_public_key_file):
    msg = "Could not find Edgecase public key file at path: {}".format(edgecase_public_key_file)
    raise FileNotFoundError(msg)
  a.edgecase_public_key = open(edgecase_public_key_file).read()

  # Load config, validate it, and add its values to the argument namespace.
  config_file = 'config.ini'
  if not isfile(config_file):
    msg = "File not found at: {}".format(config_file)
    raise FileNotFoundError(msg)
  config = configparser.ConfigParser()
  config.read_file(open(config_file))
  # Check for expected config.
  expected_sections = 'user'.split()
  for section in expected_sections:
    if not config.has_section(section):
      raise KeyError
  user_section = config['user']
  expected_user_keys = 'author_name author_key_name long_user_id'.split()
  for user_key in expected_user_keys:
    if not config.has_option(section='user', option=user_key):
      raise KeyError
    value = config.get('user', user_key)
    setattr(a, user_key, value)

  # Setup
  setup(
    log_level = a.log_level,
    debug = a.debug,
    log_timestamp = a.log_timestamp,
  )

  # Run top-level function (i.e. the appropriate task).
  tasks = """
hello
uploadDraft listDrafts deleteDraft signDraft
""".split()
  if a.task not in tasks:
    msg = "Unrecognised task: {}".format(a.task)
    msg += "\nTask list: {}".format(tasks)
    stop(msg)
  globals()[a.task](a)  # run task.




def hello(a):
  # Confirm:
  # - that we can run a simple task.
  # - that this tool has working logging.
  log('Log statement at INFO level')
  deb('Log statement at DEBUG level')
  print('hello world')




def uploadDraft(a):
  a.draft_article = edgecase_article.verify(
    article_file = a.article_file,
    article_type = 'article',
    verify_file_name = False,
    verify_signature = False,
    verify_content = True,
    public_key_dir = None,
    #verify_assets = True,
    verify_assets = False, # use when testing.
  )
  log("Draft article format is valid.")
  if a.draft_article.author_name != a.author_key_name:
    msg = "Author key name is '{k}', but author name found in draft is '{d}'."
    msg = msg.format(d=a.draft_article.author_name, k=a.author_key_name)
    raise ValueError(msg)
  private_key_file = join(a.private_key_dir, a.author_key_name + '_private_key.txt')
  if not isfile(private_key_file):
    msg = "Author private key file not found at path: {}".format(private_key_file)
    raise FileNotFoundError(msg)
  author_private_key = open(private_key_file).read()
  data = a.draft_article.data
  wrapped_data = gpg.wrap_data(author_private_key, a.edgecase_public_key, data)
  # Send request
  uri = '{d}/api/v1/authors/{a}/upload/draft'.format(d=domain, a=a.author_name)
  uri = 'http://' + uri
  cookies = {'edgecase_long_user_id': a.long_user_id}
  files = {'data': wrapped_data}
  response = requests.post(uri, timeout=ttw, cookies=cookies, files=files)
  result = response.text.strip()
  print(result)




def listDrafts(a):
  uri = '{d}/api/v1/authors/{a}/drafts'.format(d=domain, a=a.author_name)
  uri = 'http://' + uri
  cookies = None
  response = requests.get(uri, timeout=ttw, cookies=cookies)
  result = response.json()
  drafts = result['data']
  draft_names = [x['name'] for x in drafts]
  for draft_name in draft_names:
    print('- ' + draft_name)




def deleteDraft(a):
  uri = '{d}/api/v1/authors/{a}/delete/draft/'.format(d=domain, a=a.author_name)
  uri = 'http://' + uri + a.name
  cookies = {'edgecase_long_user_id': a.long_user_id}
  response = requests.get(uri, timeout=ttw, cookies=cookies)
  result = response.text.strip()
  print(result)




def signDraft(a):
  a.draft_article = edgecase_article.verify(
    article_file = a.article_file,
    article_type = 'article',
    verify_file_name = False,
    verify_signature = False,
    verify_content = True,
    public_key_dir = None,
    #verify_assets = True,
    verify_assets = False, # use when testing.
  )
  log("Draft article format is valid.")
  #print(a.draft_article.uri_title)
  signed_article = edgecase_article.edgecase_article.code.sign.sign(
    article_file = a.article_file,
    public_key_dir = a.public_key_dir,
    private_key_dir = a.private_key_dir,
  )
  output_file_name = signed_article.construct_file_name()
  output_file = join(a.output_dir, output_file_name)
  with open(output_file, 'w') as f:
    f.write(signed_article.data + '\n')




def stop(msg=None):
  if msg is not None:
    print(msg)
  import sys
  sys.exit()




if __name__ == '__main__':
  main()
