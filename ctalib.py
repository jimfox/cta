
# CTA webapp library 

import sys
import os
import urllib
import logging
import re
import datetime

import cloudstorage as gcs
import webapp2
from google.appengine.api import app_identity


class Agent():

    def __init__(self, agent_name):
        self.name = agent_name
        self.syns = []
        self.text = ''

    def add_syn(self, syn_name):
        self.syns.append(syn_name)

    def add_text(self, text_content):
        self.text = text_content

def _catalog_filename():
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    catalog_name = os.environ.get('CATALOG_NAME', 'catalog.tex')
    filename = '/' + bucket_name + '/' + catalog_name
    return filename

def _medex_filename():
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    medex_name = os.environ.get('MEDEX_NAME', 'shep.dat')
    filename = '/' + bucket_name + '/' + medex_name
    return filename

def _agent_filename():
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    log_name = 'agent.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    filename = '/' + bucket_name + '/' + log_name
    return filename

def load_agents():
    agents = {}

    if os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine/'):
        filename = _catalog_filename()
        logging.info('Loading catalog from file: ' + filename)
        f = gcs.open(filename)
    else:
        f = open('cat.tex','r')
    agent = None
    text = ''
    while True:
        l = f.readline()
        if l == '': break
        if l.find('\\ag ') == 0:
            if agent is not None: 
                agent.add_text(text)
                agents[agent.name] = agent
            l = re.sub('\\\\-', '', l)
            agent = Agent(l[4:].strip())
            text = ''
        if l.find('\\syn ') == 0:
            l = re.sub('\\\\-', '', l)
            agent.add_syn(l[5:].strip())
        text = text + l

    agent.add_text(text)
    agents[agent.name] = agent
    
    logging.info('Found {} agents'.format(len(agents)))
    f.close()
    return agents

def save_agents(agents):
    if not os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine/'):
        print 'no local save'
        return
    filename = _catalog_filename()
    logging.info('Saving catalog to: ' + filename)
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    with gcs.open(filename, 'w', content_type='text/plain', retry_params=write_retry_params) as cloudstorage_file:
        for a in sorted(agents):
            cloudstorage_file.write(agents[a].text)

    logging.info('save completed')

def log_agent(agent):
    if not os.getenv('SERVER_SOFTWARE','').startswith('Google App Engine/'):
        print 'no local agent log'
        return
    filename = _agent_filename()
    logging.info('Logging agent to: ' + filename)
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    with gcs.open(filename, 'w', content_type='text/plain', retry_params=write_retry_params) as cloudstorage_file:
        cloudstorage_file.write(agent.text)
    logging.info('agent log completed')



_html_subs = [
 ('\\\\-', ''),
 ('\\\\{','{'),
 ('\\\\}','}'),
 ('---','&mdash;'),
 ('--','&ndash;'),
 ('\$\\\\alpha\$','&alpha;'),
 ('\$\\\\beta\$','&beta;'),
 ('\$\\\\gamma\$','&gamma;'),
 ('\$\^[\{]+(.*)[\}]+\$',r'<sup>\1</sup>'),
 ('\$\_[\{]+(.*)[\}]+\$',r'<sub>\1</sub>'),
 ('"','&rdquo;'),
 ('\'','&rsquo;'),
 ('\\\\','&#92;'),
]

def htmlify(text):
    for p,r in _html_subs:
        text = re.sub(p, r, text)
    return text
   

def agent_list(agents):
    list = []
    for a in agents.itervalues():
        list.append([a.name, htmlify(a.name), 'a'])
        for s in a.syns:
            list.append([a.name, htmlify(s), 's'])
    return sorted(list, key=lambda x: x[0])


# medex translations

_medex_subs = [
  ('\\\\-',''),
  ('\\\\bb',''),
  ('\\\\eb',''),
  ('\\\\tm',''),
  ('\`\`','"'),
  ('\'\'','"'),
  ('^\$',''),
  ('(?P<d>[^\\\\])\$','\g<d>'),
  ('\\\\\$','$'),
  ('\\\\alpha','alpha'),
  ('\\\\beta','beta'),
  ('\\\\delta','delta'),
  ('\\\\gamma','gamma'),
  ('\\\\also','also'),
  ('{\\\\bf(?P<a>[^}]*)}','\g<a>'),
  ('\\\\b(?P<a>\d)','\g<a>'),
  ('--','-'),
  ('\^{(?P<a>[^\]]*)}','\g<a>'),
  ('\_{(?P<a>[^\]]*)}','\g<a>')
]

def save_medex(agents):
    filename = _medex_filename()
    logging.info('Saving medex to: ' + filename)
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    with gcs.open(filename, 'w', content_type='text/plain', retry_params=write_retry_params) as cloudstorage_file:
        for a in sorted(agents):
            text = agents[a].text
            for p,r in _medex_subs:
                text = re.sub(p, r, text)
            cloudstorage_file.write(text)
    logging.info('save completed')
