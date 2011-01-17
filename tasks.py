#
# Copyright 2011 Google Inc.
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

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import taskqueue

from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

import logging
import urllib
import settings

from pshb import HubSubscriber
import xml
from xml import sax

class ChangesHandler(sax.ContentHandler):
  def startElement(self, name, attrs):
    
    if name == "weblog":  
      blogUrl = attrs.get("url")
      taskqueue.add(
        queue_name = "subscribe",
        url = '/tasks/feed/subscribe',
        params = { 
          "url" : blogUrl
        })

class PubsubSubscribeHandler(webapp.RequestHandler):
  def post(self):
    '''
    We handle all requests to subscribe to an activity here
    '''
    url = self.request.get("url")
    
    hub = settings.DEFAULT_HUB
    
    subscriber = HubSubscriber()
    subscriber.subscribe(url, hub, settings.CALLBACK_URL)
    
class FetchHandler(webapp.RequestHandler):
  def get(self):
    '''
    Fetches the Changes.xml file and process it in one go 
      - We have long tasks so this is now possible
    '''
    url = "http://blogger.com/changes.xml"
    
    content = urlfetch.fetch(url, deadline = 60).content
    
    sax.parseString(content, ChangesHandler())
