#!/usr/bin/python2.7

from mustache import Mustache
from bs4 import BeautifulSoup


class Output_html():
    def __init__(self, template_path):
        with open(template_path, 'r') as template_file:
            self.template = template_file.read()

    def render_template(self, data):
        """
        Take the text (str) in template and replace values via 
        logic-less mustache.
        Returns the process text (str).
        """
        skeleton = Mustache(self.template)
  
        processed_text = skeleton.substitute(data)

        return processed_text
