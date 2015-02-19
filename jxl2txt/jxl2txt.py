#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command-line utility to transform a Trimble JobXML file using an XSLT stylesheet. Similar to Trimble ASCII File Generator.
Stylesheets, and ASCII File Generator are available from the Trimble website:
http://www.trimble.com/globalTRLTAB.asp?nav=Collection-62098

Examples:
python .\jxl2txt.py './data/Topo-20100331.jxl' './xslt/Comma Delimited with dates.xsl' -o text.csv --includeAttributes='No' --no-prompt

"""

from __future__ import print_function

import sys
import logging
import argparse

import json
from collections import OrderedDict
from lxml import etree

from jxl2txt.tools.console import *

def read_xml(filename, parser):
	"""
	Read an XML file and return an lxml ElementTree.

	Parameters
	----------
	filename : path to the file
	parser : lxml etree parser to use

	Returns
	-------
	xmlRoot : lxml ElementTree representing the XML document

	"""
	xml = open(filename).read().encode('utf-8')
	xmlRoot = etree.fromstring(xml, parser=parser)
	return xmlRoot

def parse_user_fields(xslRoot):
	"""
	Parse the userField* variables from a Trimble stylesheet and return a dict. Value is an array of field properties as described in the Trimble stylesheet comments.

	Parameters
	----------
	xslRoot : lxml ElementTree

	Returns
	-------
	fields : dict of user fields from a Trimble stylesheet: 

	"""
	fields = OrderedDict()
	# xpath 1.0
	for element in xslRoot.xpath("//xsl:variable[starts-with(@name, 'userField')]", namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'}):
	# xpath 2.0
	#for field in xslRoot.xpath("/variable[matches(@name, 'userField*')]"):
		select = element.attrib['select'].strip("'")
		properties = select.split('|')
		fields[properties[0]] = properties[1:]
	return fields

def get_variables(xslRoot, fields):
	"""
	Return a dict of variable elements from an XSL file. 

	Parameters
	----------
	xslRoot : lxml ElementTree
	fields : dict containing Trimble user field data

	Returns
	-------
	variables : dict containing the XSL variable element name and select attributes.

	"""
	variables = OrderedDict()
	for field in fields:
		variable = xslRoot.xpath("//xsl:variable[@name = '{0}']".format(field), namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'})
		variables[variable[0].attrib['name']] = variable[0].attrib['select'].strip("'")
	return variables

def set_variables(xslRoot, options):
	"""
	Set XSL stylesheet variables

	Parameters
	----------
	xslRoot : lxml ElementTree 
	options : dict of user field names and values.

	Returns
	-------
	xslRoot : updated ElementTree

	"""
	for option in options:
		variable = xslRoot.xpath("//xsl:variable[@name = '{0}']".format(option), namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'})
		variable[0].set('select', options[option])
	return xslRoot

def prompt_user(xslRoot):
	"""
	Prompts the user for input.

	Parameters
	----------
	xslRoot : lxml ElementTree

	Returns
	-------
	options : dict of user inputted values

	"""
	options = OrderedDict()
	fields = parse_user_fields(xslRoot)
	for field, props in fields.items():
		label = "{0}?".format(props[0])
		if props[1].lower()=='stringmenu':
			n = int(props[2])
			value = choice_prompt(props[-n:], label=label)
		elif props[1].lower()=='double':
			value = double_prompt(props[2], props[3], label=label)
		elif props[1].lower()=='integer':
			value = integer_prompt(props[2], props[3], label=label)
		elif props[1].lower()=='string':
			value = string_prompt(label=label)
		else:
			logging.warning('Unexpected field type: ', props[1])
		options[field] = "'{0}'".format(value)
	return options

def transform(xmlRoot, xslRoot, options=None):
	"""
	Transform an XML file given an XSL stylesheet. Options will be used to update XSL variables.

	Parameters
	----------
	xmlRoot : lxml ElementTree representing an XML (JobXML) document to transform.
	xslRoot : lxml ElementTree representing an XSL (Trimble stylesheet).
	options : dict of user field names and values.

	Returns
	-------
	transRoot : transformed document

	"""
	fields = parse_user_fields(xslRoot)

	if options is not None:
		xslRoot = set_variables(xslRoot, options)
		msg = 'options'
	else:
		msg = 'defaults'
	
	logging.info('Using {0}: {1}'.format(msg, json.dumps(get_variables(xslRoot, fields))))

	transform = etree.XSLT(xslRoot)
	transRoot = transform(xmlRoot)

	return transRoot

def main():

	argparser = argparse.ArgumentParser(description=__doc__)
	argparser.add_argument('xml_path', metavar='XML FILE', help="input JobXML path")
	argparser.add_argument('xsl_path', metavar='XSL FILE', help="input XSLT stylesheet path"),
	argparser.add_argument('-o', '--output', metavar='OUTPUT FILE', dest='output', type=argparse.FileType('wb', 0), help="output file name")
	
	argparser.add_argument('--prompt', dest='prompt', action='store_true', help="show user prompts for stylesheet options")
	argparser.add_argument('--no-prompt', dest='prompt', action='store_false', help="do not show user prompts for stylesheet options")
	argparser.set_defaults(prompt=True)

	args = argparser.parse_known_args()

	logging.basicConfig(stream=sys.stderr, level=args.loglevel or logging.INFO)

	parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
	xmlRoot = read_xml(args[0].xml_path, parser)
	xslRoot = read_xml(args[0].xsl_path, parser)

	fields = parse_user_fields(xslRoot)

	for field, props in fields.items():
		argparser.add_argument('--{0}'.format(field), help=props[0])

	group = argparser.add_mutually_exclusive_group()
	group.add_argument('-v', '--verbose', dest='loglevel', action='store_const', const=logging.DEBUG, help="Verbose (debug) logging")
	group.add_argument('-q', '--quiet', dest='loglevel', action='store_const', const=logging.WARN, help="Silent mode, only log warnings")

	args = argparser.parse_args()

	if args.prompt is True:
		options = prompt_user(xslRoot)
	else:
		# start with defaults
		options = get_variables(xslRoot, fields)
		arguments = (vars(args))
		for field in fields:
			# update based on option args
			if arguments[field] is not None:
				 options[field] = arguments[field]

	result = transform(xmlRoot, xslRoot, options=options)

	if args.output is not None:
		args.output.write(result)
	else:
		print(result)
		
if __name__ == '__main__':
	main()
