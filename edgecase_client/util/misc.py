# Imports
import string
import subprocess




# Relative imports
from . import validate as v




def title_to_display_title(title):
  x = title.replace('_', ' ')
  # Capitalise first letter (checkpoint article titles have a lowercase first letter).
  x = x[0].upper() + x[1:]
  return x




def get_integers_separated_by_hyphens(s):
  items = s.split('-')
  for x in items:
    if not x.isdigit():
      msg = s + ' does not consist of digits strings separated by hyphens.'
      raise ValueError(msg)
  return [int(x) for x in items]




def shell_tool_exists(tool):
  if ' ' in tool:
    raise ValueError
  tool = 'command -v {}'.format(tool)
  output, exit_code = run_local_cmd(tool)
  return not exit_code




def run_local_cmd(cmd):
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  exit_code = proc.wait()
  output = out.decode('ascii')
  err = err.decode('ascii')
  if err != '':
    output = 'COMMAND FAILED\n' + '$ ' + cmd + '\n' + err
    exit_code = 1
  return output, exit_code




def stop(msg=None):
  if msg is not None:
    print(msg)
  import sys
  sys.exit()
