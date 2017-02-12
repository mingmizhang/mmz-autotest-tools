#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from fabric.api import *



def restart_aggregator():
    run('/data/webapps/mainshop_aggregator/current/bin/server.sh restart')

def restart_searcher():
    run('/data/webapps/mainshop_searcher/current/bin/server.sh restart')

env.password="*"
env.user="****"
env.port="58422"
roles={}
roles["beta_searcher"]=["test-distshop02.beta","test-distshop03.beta","test-distshop04.beta"]
roles["beta_searcher1"]=["test-distshop01.beta"]
roles["beta_aggregator"]=["128.7.66.34"]
env.roledefs=roles

##运行的时候执行fab -f protect_env.py -R beta_searcher1 restart_searcher


