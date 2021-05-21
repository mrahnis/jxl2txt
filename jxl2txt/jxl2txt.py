#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command-line utility to transform a Trimble JobXML file using a XSLT stylesheet, similar to Trimble ASCII File Generator.
Stylesheets are available from the Trimble website.

Examples:
jxl2txt convert './data/Topo-20100331.jxl' './xslt/Comma Delimited with dates.xsl' -o text.csv --includeAttributes No --no-prompt

"""

import sys
import logging
from typing import OrderedDict, Union

import click
import json
from collections import OrderedDict
from lxml import etree

from jxl2txt.tools.console import choice_prompt, double_prompt, integer_prompt, string_prompt


def read_xml(filename: str, parser: etree.XMLParser) -> etree.ElementTree:
    xml = open(filename).read().encode('utf-8')
    xmlRoot = etree.fromstring(xml, parser=parser)

    return xmlRoot


def get_fields(xslRoot: etree.ElementTree) -> OrderedDict:
    fields = OrderedDict()

    # xpath 2.0
    # for field in xslRoot.xpath("/variable[matches(@name, 'userField*')]"):
    # xpath 1.0
    for element in xslRoot.xpath("//xsl:variable[starts-with(@name, 'userField')]", namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'}):
        select = element.attrib['select'].strip("'")
        properties = select.split('|')
        fields[properties[0]] = properties[1:]

    return fields


def get_options(xslRoot: etree.ElementTree, options: OrderedDict) -> OrderedDict:
    settings = OrderedDict()

    for option in options:
        setting = xslRoot.xpath("//xsl:variable[@name = '{0}']".format(option), namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'})
        settings[setting[0].attrib['name']] = setting[0].attrib['select'].strip("'")
    return settings


def set_options(xslRoot: etree.ElementTree, options: OrderedDict) -> etree.ElementTree:
    for option in options:
        current = xslRoot.xpath("//xsl:variable[@name = '{0}']".format(option), namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'})
        current[0].set('select', options[option])
    return xslRoot


def get_input(xslRoot: etree.ElementTree) -> OrderedDict:
    options = OrderedDict()
    fields = get_fields(xslRoot)
    for field in fields:
        props = fields[field]
        label = "{0}?".format(props[0])
        if props[1].lower() == 'stringmenu':
            n = int(props[2])
            value = choice_prompt(props[-n:], label=label)
        elif props[1].lower() == 'double':
            value = double_prompt(props[2], props[3], label=label)
        elif props[1].lower() == 'integer':
            value = integer_prompt(props[2], props[3], label=label)
        elif props[1].lower() == 'string':
            value = string_prompt(label=label)
        else:
            logging.warning('Unexpected field type: ', props[1])
        options[field] = "'{0}'".format(value)
    return options


def transform(
    xmlRoot: etree.ElementTree,
    xslRoot: etree.ElementTree,
    options: Union[None, OrderedDict] = None
) -> etree.ElementTree:

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


@click.group()
def cli():
    pass


@click.command(context_settings=dict(ignore_unknown_options=True,))
@click.argument('xml_path', nargs=1, type=click.Path(exists=True), metavar='XML_FILE')
@click.argument('xsl_path', nargs=1, type=click.Path(exists=True), metavar='XSL_FILE')
@click.option('--output', type=click.File('wb', None), metavar='OUTPUT_FILE', help="output file name")
@click.option('--prompt/--no-prompt', default=True, help="show user prompts for stylesheet options, or use command line arguments")
@click.option('-v', '--verbose', is_flag=True, help='enables verbose mode')
@click.argument('xslt_args', nargs=-1, type=click.UNPROCESSED)
def convert(xml_path, xsl_path, output, prompt, verbose, xslt_args):
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


@click.command(help="Print information about an XSL stylesheet")
@click.argument('xml_path', nargs=1, type=click.Path(exists=True), metavar='XML_FILE')
def info(xml_path):
    """ Print information about a JobXML file or XSL stylesheet.

        xml_path : input XML file path
    """

    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

    """
    Trimble stylesheets
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" >
        get_fields()
    JobXML files
        <JOBFile jobName="control" version="5.3" product="Trimble Survey Controller" productVersion="12.45" productDBVersion="1245-4" TimeStamp="2010-03-31T10:10:51"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.trimble.com/schema/JobXML/5_3 http://www.trimble.com/schema/JobXML/5_3/JobXMLSchema-5.3.xsd">
         print(some jobfile info)
    """

    root = read_xml(xml_path, parser)

    if root.tag == 'JOBFile':
        print("Document Type: JobXML")
        print("")
        print("Job Properties")
        print("==============")
        print("Reference: {}".format(root.find('FieldBook/JobPropertiesRecord/Reference').text))
        print("Description: {}".format(root.find('FieldBook/JobPropertiesRecord/Description').text))
        print("Operator: {}".format(root.find('FieldBook/JobPropertiesRecord/Operator').text))
        print("Job Note: {}".format(root.find('FieldBook/JobPropertiesRecord/JobNote').text))
    elif root.tag == '{http://www.w3.org/1999/XSL/Transform}stylesheet':
        fields = get_fields(root)
        print("Document Type: Trimble XSL Stylesheet")
        print("")
        print("Available Options")
        print("=================")
        for field in fields:
            props = fields[field]
            label = "{0}".format(props[0])
            if props[1].lower() == 'stringmenu':
                n = int(props[2])
                print("{0} : {1} {2}".format(field, label, props[-n:]))
            elif props[1].lower() == 'double':
                print("{0} : {1} low={2}, high={3}".format(field, label, props[2], props[3]))
            elif props[1].lower() == 'integer':
                print("{0} : {1} low={2}, high={3}".format(field, label, props[2], props[3]))
            elif props[1].lower() == 'string':
                print("{0} : {1}".format(field, label))
            else:
                logging.warning('Unexpected field type: ', props[1])
    else:
        print("Document Type: not recognized")


cli.add_command(convert)
cli.add_command(info)
