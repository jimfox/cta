#!/usr/bin/env python

# CTA webapp

import sys
import os
import urllib
import logging
import re

from google.appengine.api import users

import json
import jinja2
import webapp2

from ctalib import Agent
from ctalib import htmlify
from ctalib import load_agents
from ctalib import save_agents
from ctalib import save_medex

from ctalib import log_agent
from ctalib import agent_list


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


agents = None
    
class MainPage(webapp2.RequestHandler):

    def get(self):

        global agents
        # test_put()

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        if agents is None:
            logging.info('loading agents')
            agents = load_agents()
            if len(agents) < 20:
               logging.critical('Too few agents! {}'.format(len(agents)))
               return;

        uname = ''
        if user is not None:
            uname = user.nickname()
        template_values = {
            'username': uname,
            'agent_list': json.dumps(agent_list(agents)),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class AgentHandler(webapp2.RequestHandler):


    def get(self):
        global agents
        agent_name = self.request.get('agent')
        if agents is None:
            agents = load_agents()

        logging.info('"' + agent_name + '"')
        self.response.write(agents[agent_name].text)

    def put(self):
        global agents
        agent_name = self.request.get('agent')
        if agents is None:
            agents = load_agents()

        logging.info('update ' + agent_name)
        put_text = urllib.unquote_plus(self.request.body)
        lines = put_text.split('\n')
        if lines[0].find('\\ag ') == 0 and lines[0][4:].strip() == agent_name:
            logging.info('put agent name OK')
            if agent_name in agents:
                agents[agent_name].text = put_text
            else:
                agent = Agent(agent_name)
                for l in lines:
                    if l.find('\\syn ') == 0:
                        agent.add_syn(l[5:].strip())
                    if l.find('\\abs ') == 0:
                        break
                agent.text = put_text
                agents[agent_name] = agent
            log_agent(agents[agent_name])
            save_agents(agents)
            save_medex(agents)
            self.response.write("OK")
        else:
            self.response.write("error: agent names do not match")

    def delete(self):
        global agents
        agent_name = self.request.get('agent')
        if agents is None:
            agents = load_agents()

        logging.info('delete ' + agent_name)
        if agent_name in agents:
            log_agent(agents[agent_name])
            del agents[agent_name] 
        save_agents(agents)
        self.response.write("OK")



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/agent', AgentHandler),
], debug=True)
