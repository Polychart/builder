#!/usr/bin/env python
import argparse
import glob
import json
import os
import re

def _parse_stream(stream):
  from lxml import etree
  parser = etree.HTMLParser()
  # parse the <script> tags.
  tree = etree.parse(stream, parser)
  scripts = tree.xpath('//script')
  for script in scripts:
    if 'id' in script.attrib and script.attrib.get('type', None) == 'text/html':
      value = script.text
      value = value.strip()
      # compress whitespace.
      value = re.sub(r"([\t ]+)", " ", value)
      value = re.sub(r"(\s*\n\s*)", "\n", value)
      yield (script.attrib['id'], value)

def parse_comment(html_string):
  import lxml.html
  # tree = lxml.etree.parse(stream, parser)
  tree = lxml.html.fragment_fromstring(html_string,create_parent=1)
  # print etree.tostring(tree, pretty_print=1)
  if len(tree.getchildren()) > 0:
    children = tree.getchildren()
    cmt = children[0]
    if isinstance(cmt, lxml.html.HtmlComment):
      text = cmt.text.strip()
      if not text.startswith('ko'):
        return text
  return None

def parse_scripts(filenames):
  result = {}
  for html_file in filenames:
    stream = open(html_file, 'rb')
    for key, text in _parse_stream(stream):
      if key in result:
        assert False, 'template with duplicate id "%s".' % key
      result[key] = {
        'html':text,
        'filename':html_file,
      }
  return result

def generate_template(html_files, output_file):
  raw_result = parse_scripts(html_files)
  result = {}
  for (key, value) in raw_result.iteritems():
    # only extract out the HTML part.
    result[key] = value['html']
  output = open(output_file, 'wb')
  output.write("""require('poly/main/template').loadTemplateEngine(%s)""" % json.dumps(result))
  output.close()

def list_all_tmpl_files(dirpath):
  for dirname, subdirnames, filenames in os.walk(dirpath):
    for f in filenames:
      if f.lower().endswith('.tmpl'):
        yield os.path.join(dirname, f)

def main():
  parser = argparse.ArgumentParser(description='Turn ko templates into JavaScript.')
  parser.add_argument('--source', dest='source', help="Path to source folder.")
  parser.add_argument('--dest',  dest='dest', help="Path to destination.")
  parsed = parser.parse_args()
  root_dir = os.getcwd()
  source = list_all_tmpl_files(os.path.join(root_dir, parsed.source))
  dest   = os.path.join(root_dir, parsed.dest)
  generate_template(source, dest)

if __name__ == '__main__':
  main()
