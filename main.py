#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import urllib
import cgi
import logging 
from google.appengine.api import users
from google.appengine.ext import ndb

from google.appengine.api import urlfetch
import sys
import json

import jinja2
import webapp2


CMS_APP_TOKEN = "QsPJzBHtT7FAtkgEOmbi8vry8"


JINJA_ENVIRONMENT = jinja2.Environment(
                            loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                            extensions=['jinja2.ext.autoescape'])


DEFAULT_GUESTBOOK_NAME = "default"

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
  """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
  return ndb.Key('Guestbook', guestbook_name)


class Greeting(ndb.Model):
  """Models an individual Guestbook entry with author, content, and date."""
  author = ndb.UserProperty()
  content = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)

class myResult(object):
  pass

def getDataPerZipCode():
  r = urlfetch.fetch('https://data.cms.gov/resource/inpatient-charge-data-FY2011.json?provider_zip_code=94305', payload=None, method=urlfetch.GET, headers={'X-App-Token': CMS_APP_TOKEN}, allow_truncated=False, follow_redirects=True, deadline=5, validate_certificate=False)
  #print r.content
  query_response=r.content
  query_response = query_response.replace("[","").replace("{","").replace("]","").replace(")","")
  query_response =query_response.split(",")
  
  query_response = json.loads(r.content)
  myQuery = []
  
  for item in query_response:
    myQueryItem = myResult()
    myQueryItem.drg_definition = item["drg_definition"]
    myQueryItem.price = item["average_covered_charges"]
    myQueryItem.hospital = item["provider_name"]
    myQueryItem.address = item["provider_street_address"]

    myQuery.append(myQueryItem)
  
  return myQuery

class MainPage(webapp2.RequestHandler):
  def get(self):
    
    myQuery = getDataPerZipCode()
    print myQuery
    
    # print myQuery
    template_values = {
      'query_response': myQuery 
    }
        
    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
                                       ('/', MainPage),
                                       ], debug=True)

