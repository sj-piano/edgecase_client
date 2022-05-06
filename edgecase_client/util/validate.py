# Imports
import os
import string
import re




# Notes:
# - We treat this module as foundational. It shouldn't import anything other than standard library modules.
# - Functions at the bottom are the most basic.
# -- Functions further up may use functions below them.




# ### SECTION
# Components.

# https://stackoverflow.com/a/45598540
date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
hex_digits = '0123456789abcdef'


def build_error_msg(msg, value, name=None, location=None, kind=None):
  # Build out an expanded error message with useful detail.
  m = ''
  if location is not None:
    m += "in location {}, ".format(repr(location))
  if name is not None:
    # This is a complicated way of putting single quotes around _only_ the first word in the name.
    # This means that a description can be added after the name.
    words = name.split(' ')
    name2 = "'{}'".format(words[0])
    if len(words) > 1:
      name2 += ' ' + ' '.join(words[1:])
    m += "for variable {}, ".format(name2)
  if kind is not None:
    m += "expected a {}, but ".format(repr(kind))
  m += "received value {}".format(repr(value))
  if msg != '':
    m += ', ' + msg
  m = m[0].capitalize() + m[1:]
  return m




# ### SECTION
# Article property validation functions.




def validate_datafeed_article_file_name(
    file_name = None,
    date = None,
    article = None,
    ):
  # Examples:
  # 2021-04-12_edgecase_datafeed_article_216_2021-04-12_stjohn_piano_discussion_crypto_messaging_apps.txt
  # 2017-06-28_edgecase_datafeed_article_1_2017-06-28_stjohn_piano_viewpoint.txt
  datafeed_name = 'edgecase_datafeed'
  child_article_type = article.article_type
  location = 'validate.py::validate_datafeed_article_file_name'
  validate_date(date)
  file_name_original = file_name
  file_name, ext = os.path.splitext(file_name)
  if ext != '.txt':
    msg = "Datafeed article filename ({}) does not have extension '.txt'.".format(file_name_original)
    raise ValueError(msg)
  d = file_name[:10]
  validate_date(d, 'date (in file name)', location)
  if d != date:
    msg = "Date ('{}') in datafeed article filename ({}) differs from date in article ('{}').".format(d, file_name_original, date)
    raise ValueError(msg)
  if file_name[10] != '_':
    msg = "In datafeed article filename ('{}'), expected char 11 to be an underscore ('_').".format(file_name_original)
    raise ValueError(msg)
  n = len(datafeed_name)
  dn = file_name[11:11+n]
  if dn != datafeed_name:
    msg = "Datafeed name ('{}') in datafeed article filename ({}) is not '{}'.".format(dn, file_name_original, datafeed_name)
    raise ValueError(msg)
  i = 11+n
  expected = '_article_'
  n2 = len(expected)
  i2 = i + n2
  if file_name[i:i2] != expected:
    msg = "In datafeed article filename ({f}), expected that chars {a}-{b} would be '{c}', not '{d}'.".format(
      f=file_name_original, a=i+1, b=i2+1, c=expected, d=file_name[i:i2]
    )
    raise ValueError(msg)
  section = file_name[i2:]
  # Example section:
  # 1_2017-06-28_stjohn_piano_viewpoint
  if '_' not in section:
    msg = "In datafeed article filename ({f}), in article filename section ({f2}), did not find an underscore ('_').".format(
      f=file_name_original, f2=section
    )
    raise ValueError(msg)
  # Confirming that an underscore is present allows us to now split by underscore.
  article_id = section.split('_')[0]
  validate_string_is_whole_number(article_id)
  n3 = len(article_id + '_')
  remaining = section[n3:]
  # The remaining section is the child article's filename.
  child_file_name = remaining + '.txt'
  # Example child_file_name:
  # 2017-06-28_stjohn_piano_viewpoint.txt
  # Select a validation function based on the child article type.
  if child_article_type in 'article signed_article'.split():
    validate_article_file_name(
      file_name = child_file_name,
      date = article.date,
      author_name = article.author_name,
      uri_title = article.uri_title,
    )
  elif child_article_type == 'checkpoint_article':
    validate_checkpoint_article_file_name(
      file_name = child_file_name,
      uri_title = article.uri_title,
    )
  else:
    msg = "Datafeed article contains an unrecognised article type: {}".format(child_article_type)
    raise ValueError(msg)




def validate_checkpoint_article_file_name(
    file_name = None,
    uri_title = None,
    ):
  # Example:
  # checkpoint_0.txt
  expected = uri_title + '.txt'
  if file_name != expected:
    msg = "Checkpoint uri_title is {}".format(repr(uri_title))
    msg += ", so expected checkpoint filename {}".format(repr(expected))
    msg += ", but instead found filename {}".format(repr(file_name))
    raise ValueError(msg)




def validate_article_file_name(
    file_name = None,
    date = None,
    author_name = None,
    uri_title = None,
    ):
  # Note: To validate its filename, a signed article will call this method on its internal article.
  # Example:
  # 2019-04-14_stjohn_piano_a_simple_api__json_input_output.txt
  validate_date(date)
  validate_author_name(author_name)
  validate_uri_title(uri_title)
  file_name_original = file_name
  file_name, ext = os.path.splitext(file_name)
  if ext != '.txt':
    msg = "Article filename ({}) does not have extension '.txt'.".format(file_name_original)
    raise ValueError(msg)
  d = file_name[:10]
  validate_date(d)
  if d != date:
    msg = "Date ('{}') in article filename ({}) differs from date in article ('{}').".format(d, file_name_original, date)
    raise ValueError(msg)
  if file_name[10] != '_':
    msg = "In article filename ('{}'), expected char 11 to be an underscore ('_').".format(file_name_original)
    raise ValueError(msg)
  n = len(author_name)
  an = file_name[11:11+n]
  if an != author_name:
    msg = "Author name ('{}') in datafeed article filename ({}) is not the author name found within the article ('{}').".format(an, file_name_original, author_name)
    raise ValueError(msg)
  i = 11+n
  if file_name[i] != '_':
    msg = 'Char between author_name and uri_title (index {i}, in this case) must be an underscore. Instead, it is {c}.'.format(i=i, c=file_name[i])
    raise ValueError(msg)
  remaining = file_name[i+1:]
  if uri_title != remaining:
    msg = "Remaining portion of file_name ({r}) is not the same as the uri_title ({u})".format(r=remaining, u=uri_title)
    raise ValueError(msg)




def validate_datafeed_name(s):
  # For now, this check is sufficient.
  expected = 'edgecase_datafeed'
  if s != expected:
    msg = "Expected datafeed_name {}".format(repr(expected))
    msg += ", but found {}".format(repr(s))
    raise ValueError(msg)




def validate_blockchain_name(s):
  # For now, this check is sufficient.
  expected = 'bitcoin'
  if s != expected:
    msg = "Expected blockchain_name {}".format(repr(expected))
    msg += ", but found {}".format(repr(s))
    raise ValueError(msg)




def validate_signed_by_author(s):
  permitted = 'no yes'.split()
  if s not in permitted:
    msg = "Expected a 'signed_by_author' value in the list {}. Instead, found '{}'.".format(permitted, s)
    raise ValueError(msg)




def validate_date(d, name=None, location=None, kind='date'):
  # Example: 2017-06-28
  if len(d) != 10:
    msg = "which is {} chars, but must be 10 chars.".format(len(d))
    msg = build_error_msg(msg, d, name, location, kind)
    raise ValueError(msg)
  for i in [4, 7]:
    if d[i] != '-':
      msg = "where char {i} ('{c}') in {d} must be a hyphen ('-'), but isn't.".format(i=i, c=d[i], d=repr(d))
      msg = build_error_msg(msg, d, name, location, kind)
      raise ValueError(msg)
  d2 = d[:4] + d[5:7] + d[8:]
  if not d2.isdigit():
    msg = "where, once hyphens are removed, the date must contain only digits, but doesn't."
    msg = build_error_msg(msg, d, name, location, kind)
    raise ValueError(msg)




def validate_author_name(n):
  # Example: stjohn_piano
  permitted = string.ascii_lowercase + string.digits + '_'
  for c in n:
    if c not in permitted:
      msg = 'Character [{}] not permitted in article author_name.'.format(repr(c))
      raise ValueError(msg)




def validate_uri_title(u):
  # Examples:
  # stalky__co__by_rudyard_kipling_in_ambush
  # recipe_for_installing_kafka_2_5_0_as_a_systemd_service_on_ubuntu_16_04
  permitted = string.ascii_lowercase + string.digits + '_'
  for c in u:
    if c not in permitted:
      msg = 'Character [{}] not permitted in uri_title.'.format(repr(c))
      raise ValueError(msg)




def validate_title(t, article_type):
  if article_type == 'checkpoint_article':
    # Example: checkpoint_0
    if t[:10] != 'checkpoint':
      raise ValueError
    if t[10] != '_':
      raise ValueError
    if not t[11:].isdigit():
      raise ValueError
  else:
    # Example: Discussion:_Crypto_Messaging_Apps
    if t[0] not in string.ascii_uppercase:
      raise ValueError('First character must be uppercase')
    permitted = string.ascii_letters + string.digits + "#&'(),-./:_" + '"'
    for c in t:
      if c not in permitted:
        msg = 'Character [{}] not permitted in article title.'.format(repr(c))
        raise ValueError(msg)




def validate_article_type(article_type, name=None, location=None, kind='article_type'):
  article_types = """
article signed_article checkpoint_article
datafeed_article signed_datafeed_article
""".split()
  if article_type not in article_types:
    msg = "Unrecognised article_type: {}".format(article_type)
    raise ValueError(msg)








# ### SECTION
# Basic validation functions.




def validate_whole_number(n, name=None, location=None, kind='whole_number'):
  # 0 is a whole number.
  if n == 0:
    return
  validate_positive_integer(n, name, location, kind)


wn = validate_whole_number


def validate_positive_integer(n, name=None, location=None, kind='positive_integer'):
  validate_integer(n, name, location, kind)
  if n < 0:
    msg = "which is less than 0."
    msg = build_error_msg(msg, n, name, location, kind)
    raise ValueError(msg)


pi = validate_positive_integer


def validate_integer(n, name=None, location=None, kind='integer'):
  if not isinstance(n, int):
    msg = "which has type '{}', not 'int'.".format(type(n).__name__)
    msg = build_error_msg(msg, n, name, location, kind)
    raise TypeError(msg)


i = validate_integer


def validate_boolean(b, name=None, location=None, kind='boolean'):
  if type(b) != bool:
    msg = "which has type '{}', not 'bool'.".format(type(b).__name__)
    msg = build_error_msg(msg, b, name, location, kind)
    raise TypeError(msg)


b = validate_boolean


def validate_hex_length(s, n, name=None, location=None, kind=None):
  if kind is None:
    kind = 'hex_length_{}_bytes'.format(n)
  validate_hex(s, name, location, kind)
  if not isinstance(n, int):
    msg = "which has type '{}', not 'int'.".format(type(n).__name__)
    name2 = 'n (i.e. the hex length)'
    msg = build_error_msg(msg, n, name=name2, location=location, kind=None)
    raise TypeError(msg)
  # 1 byte is 2 hex chars.
  if len(s) != n * 2:
    msg = "whose length is {} chars, not {} chars.".format(len(s), n * 2)
    msg = build_error_msg(msg, s, name, location, kind)
    raise ValueError(msg)


def validate_hex(s, name=None, location=None, kind='hex'):
  validate_string(s, name, location, kind)
  # find indices of non-hex characters in the string.
  indices = [i for i in range(len(s)) if s[i] not in hex_digits]
  if len(indices) > 0:
    non_hex_chars = [s[i] for i in indices]
    msg = "where the chars at indices {} (with values {}) are not hex chars.".format(indices, ','.join(non_hex_chars))
    msg = build_error_msg(msg, s, name, location, kind)
    raise ValueError(msg)


def validate_string_is_decimal(
    s, dp=2, name=None, location=None, kind='integer',
    ):
  # dp = decimal places
  string(s, name, location, kind)
  if not isinstance(dp, int):
    msg = "which has type '{}', not 'int'.".format(type(dp).__name__)
    name2 = 'dp (i.e. the number of decimal places)'
    msg = build_error_msg(msg, dp, name=name2, location=location, kind=None)
    raise TypeError(msg)
  regex = r'^\d*.\d{%d}$' % dp
  decimal_pattern = re.compile(regex)
  if not decimal_pattern.match(s):
    msg = 'which is not a valid {}-decimal-place decimal value.'.format(dp)
    msg = build_error_msg(msg, s, name, location, kind)
    raise ValueError(msg)


sd = validate_string_is_decimal


def validate_string_is_whole_number(
    s, name=None, location=None, kind='string_is_whole_number',
    ):
  # 0 is a whole number.
  validate_string(s, name, location, kind)
  if s == '0':
    return
  validate_string_is_positive_integer(s, name, location, kind)


swn = validate_string_is_whole_number


def validate_string_is_positive_integer(
    s, name=None, location=None, kind='string_is_positive_integer',
    ):
  validate_string(s, name, location, kind)
  if s == '0':
    raise ValueError('0 is not a positive number.')
  # find indices of non-digit characters in the string.
  indices = [i for i in range(len(s)) if not s[i].isdigit()]
  if len(indices) > 0:
    non_digit_chars = [s[i] for i in indices]
    msg = "where the chars at indices {} (with values {}) are not digits.".format(indices, ','.join(non_digit_chars))
    msg = build_error_msg(msg, s, name, non_digit_chars, kind)
    raise ValueError(msg)


spi = validate_string_is_positive_integer


def validate_string_is_date(s, name=None, location=None, kind='string_is_date'):
  validate_string(s, name, location, kind)
  if not date_pattern.match(s):
    msg = 'which is not a valid YYYY-MM-DD date string.'
    msg = build_error_msg(msg, s, name, location, kind)
    raise ValueError(msg)


sdate = validate_string_is_date


def validate_string(s, name=None, location=None, kind='string'):
  if not isinstance(s, str):
    msg = "which has type '{}', not 'str'.".format(type(s).__name__)
    msg = build_error_msg(msg, s, name, location, kind)
    raise TypeError(msg)


s = validate_string
