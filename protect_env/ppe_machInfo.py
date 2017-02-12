#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from fabric.api import *



def restart_mainshop_aggregator():
    run('/data/webapps/mainshop_aggregator/current/bin/server.sh restart')

def restart_mainshop_searcher():
    run('/data/webapps/mainshop_searcher/current/bin/server.sh restart')

def restart_distshop_aggregator():
    run('/data/webapps/distshop_aggregator/current/bin/server.sh restart')

def restart_distshop_searcher():
    run('/data/webapps/distshop_searcher/current/bin/server.sh restart')

env.password="XXX"
env.user="mingmi.zhang"
env.port="58422"
roles={}
roles["mainshop_ppe_searcher"]=["test-mainshop-ppe01.tx","test-mainshop-ppe02.tx","test-mainshop-ppe03.tx","test-mainshop-ppe04.tx","test-mainshop-ppe05.tx","test-mainshop-ppe06.tx"]
roles["mainshop_ppe_searcher1"]=["test-mainshop-ppe01.tx"]
roles["mainshop_ppe_aggregator"]=["search-aggregator-mainshop-ppe01.tx"]

roles["distshop_ppe_searcher"]=["test-distshop-ppe01.hm","test-distshop-ppe01.tx","test-distshop-ppe02.hm","test-distshop-ppe02.tx","test-distshop-ppe03.hm","test-distshop-ppe04.hm"]
roles["distshop_ppe_searcher1"]=["test-distshop-ppe01.hm"]
roles["distshop_ppe_aggregator"]=["search-aggregator-distshop-ppe02.tx"]

env.roledefs=roles




