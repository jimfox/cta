#!/usr/bin/env python

# CTA webapp

import sys
import os
import urllib
import logging
import re
from datetime import date

from google.appengine.api import users

import json
import jinja2
import webapp2

from ctalib import Agent
from ctalib import htmlify
from ctalib import load_agents
from ctalib import save_agents
from ctalib import gen_medex

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
        if agent_name in agents:
            self.response.write(agents[agent_name].text)
        else:
            self.response.write('error: agent {} not found'.format(agent_name))

    def put(self):
        global agents
        agent_name = self.request.get('agent')
        mode = self.request.get('mode')
        if agents is None:
            agents = load_agents()

        if mode == 'i':
            agent_name = None  # will get from text

        put_text = urllib.unquote_plus(self.request.body)
        lines = put_text.split('\n')
        if lines[0].find('\\ag ') == 0:
            put_name = lines[0][4:].strip()
            if agent_name is None:
                agent_name = put_name
                logging.info('new agent: ' + agent_name)
                if agent_name in agents:
                    self.response.write('error: agent {} already exists'.format(agent_name))
                    return
            else:
                logging.info('update agent: ' + agent_name)
                if agent_name != put_name:
                    self.response.write('error: agent name does not match')
                    return
                if agent_name not in agents:
                    self.response.write('error: agent {} not found'.format(agent_name))
                    return
               
            agent = Agent(agent_name)
            lnum = 0
            need_mod = True
            for l in lines:
                if l.find('\\syn ') == 0:
                    agent.add_syn(l[5:].strip())
                if need_mod and l.find('\\mod ') == 0:
                    lines[lnum] = '\\mod: Last modified: ' + date.today().strftime('%Y/%m/%d')
                    need_mod = False
                if need_mod and l.find('\\forcemod ') == 0:
                    lines[lnum] = '\\mod: ' + l[10:])
                    need_mod = False
                if need_mod and l.find('\\abs ') == 0:
                    lines.insert(lnum, '\\mod Last modified: ' + date.today().strftime('%Y/%m/%d'))
                    need_mod = False
                    break
            agent.text = '\n'.join(lines) + '\n'
            agents[agent_name] = agent
            log_agent(agents[agent_name])
            save_agents(agents)
            self.response.write("OK")
        else:
            self.response.write("error: invalid agent text")

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


class MedexHandler(webapp2.RequestHandler):

    def get(self):
        global agents
        if agents is None:
            agents = load_agents()

        self.response.headers.add_header('Content-type', 'text/plain; charset=us-ascii')
        self.response.headers.add_header('Content-Disposition', 'attachment; filename=medex.txt')
        self.response.write(gen_medex(agents))



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/agent', AgentHandler),
    ('/medex/medex.txt', MedexHandler),
], debug=True)
