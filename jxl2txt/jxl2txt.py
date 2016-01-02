#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command-line utility to transform a Trimble JobXML file using a XSLT stylesheet, similar to Trimble ASCII File Generator.
Stylesheets are available from the Trimble website.

Examples:
python .\jxl2txt.py './data/Topo-20100331.jxl' './xslt/Comma Delimited with dates.xsl' -o text.csv --includeAttributes='No' --no-prompt

"""

from __future__ import print_function

import sys
import logging
import click

import json
from collections import OrderedDict
from lxml import etree

from jxl2txt.tools.console import *

def read_xml(filename, parser):
	xml = open(filename).read().encode('utf-8')
	xmlRoot = etree.fromstring(xml, parser=parser)

	return xmlRoot

def get_fields(xslRoot):
	fields = OrderedDict()

	# xpath 1.0
	for element in xslRoot.xpath("//xsl:variable[starts-with(@name, 'userField')]", namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'}):
	# xpath 2.0
	#for field in xslRoot.xpath("/variable[matches(@name, 'userField*')]"):
		select = element.attrib['select'].strip("'")
		properties = select.split('|')
		fields[properties[0]] = properties[1:]

	return fields

def get_options(xslRoot, options):
	settings = OrderedDict()

	for option in options:
		setting = xslRoot.xpath("//xsl:variable[@name = '{0}']".format(option), namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'})
		settings[setting[0].attrib['name']] = setting[0].attrib['select'].strip("'")
	return settings

def set_options(xslRoot, options):
	for option in options:
		current = xslRoot.xpath("//xsl:variable[@name = '{0}']".format(option), namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'})
		current[0].set('select', options[option])
	return xslRoot

def get_input(xslRoot):
	options = OrderedDict()
	fields = get_fields(xslRoot)
	for field in fields:
		props = fields[field]
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

	fields = get_fields(xslRoot)

	if options is not None:
		xslRoot = set_options(xslRoot, options)
		msg = 'options'
	else:
		msg = 'defaults'
	
	logging.info('Using {0}: {1}'.format(msg, json.dumps(get_options(xslRoot, fields))))

	transform = etree.XSLT(xslRoot)
	transRoot = transform(xmlRoot)

	return transRoot

@click.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument('xml_path', nargs=1, type=click.Path(exists=True), metavar='XML FILE')
@click.argument('xsl_path', nargs=1, type=click.Path(exists=True), metavar='XSL FILE')
@click.option('--output', type=click.File('wb', 0), metavar='OUTPUT FILE', help="output file name")
@click.option('--prompt/--no-prompt', default=True, help="show user prompts for stylesheet options")
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.argument('xslt_args', nargs=-1, type=click.UNPROCESSED)
def cli(xml_path, xsl_path, output, prompt, verbose, xslt_args):
	""" Apply an XSL stylesheet to a Trimble JXL file.

		xml_path : input JobXML path

		xsl_path : input XSLT stylesheet path
	"""
	if verbose is True:
		loglevel = 2
	else:
		loglevel = 0

	logging.basicConfig(stream=sys.stderr, level=loglevel or logging.INFO)

	parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

	xmlRoot = read_xml(xml_path, parser)
	xslRoot = read_xml(xsl_path, parser)
	fields = get_fields(xslRoot)

	if prompt is True:
		options = get_input(xslRoot)
	else:
		options = get_options(xslRoot, fields)
		kwds = [s.strip('-') for s in xslt_args[0::2]]
		args = dict(zip(kwds, xslt_args[1::2]))
		for arg in args:
			try:
				options[arg] = "'{0}'".format(args[arg])
			except:
				logging.info("Argument, {}, is not an available option.".format(arg))

	result = transform(xmlRoot, xslRoot, options=options)

	if output is not None:
		output.write(result)
	else:
		print(result)
