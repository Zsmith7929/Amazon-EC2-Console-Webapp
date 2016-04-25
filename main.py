#!/usr/bin/env python
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

#add lib folder with 3rd party libraries
from google.appengine.ext import vendor
vendor.add('lib')

import webapp2
import os
import string
import json
import ast
from google.appengine.api import urlfetch
import boto.ec2
import time

EMAILS = ['emails@domains']

class BotoHandler(webapp2.RequestHandler):
	def post(self):
		
		conn = boto.ec2.connect_to_region("us-west-1", aws_access_key_id='key', aws_secret_access_key='secret')
		
		r = self.request.get("onoffswitch")
		self.response.write(r)
		
		if r == "on":
			reply = conn.start_instances(instance_ids=['i-374ae382'])
			self.response.write("Instance is starting. Allow up to 60 seconds.")
			
					
		else:
			reply = conn.stop_instances(instance_ids=['i-374ae382'])
			self.response.write("Instance is stopping. Allow up to 60 seconds for the status to update.")

class ValidateHandler(webapp2.RequestHandler):
	def post(self):
		
		if self.request.get('email').lower() in EMAILS:
			r = urlfetch.fetch('https://mcapi.us/server/status?ip=52.8.14.154')
			j = json.loads(r.content)
			with open('main.html') as f:
				page = f.read()
				conn = boto.ec2.connect_to_region("us-west-1", aws_access_key_id='key', aws_secret_access_key='secret')
				reservations = conn.get_all_instances()
				instances = [i for r in reservations for i in r.instances]
				if instances[0].__dict__["_state"].__dict__["name"] == "running":
					self.response.write(page.format("checked"))
					with open('table.html') as g:
						table = g.read()
						self.response.write(table.format(j["status"],j["online"],j["motd"],j["players"]["now"],j["server"]["name"],"None"))
				else:
					self.response.write(page.format("unchecked"))
					with open('table.html') as g:
						table = g.read()
						self.response.write(table.format(j["status"],j["online"],j["motd"],j["players"]["now"],j["server"]["name"],"None"))
		else:
			self.response.write("Frag off.")

class MainHandler(webapp2.RequestHandler):
    def get(self):
		with open("index.html") as f:
			page = f.read()
			self.response.write(page)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
	('/main', ValidateHandler),
	('/off', BotoHandler)
], debug=True)
