#!/bin/bash

set -o nounset
if [ $2 = "beta" ];then
    if [[ $1 =~ "searcher" ]];then
        fab -f beta_machInfo.py -R beta_searcher restart_searcher
    elif [[ $1 =~ "aggregator" ]];then
        fab -f beta_machInfo.py -R beta_aggregator restart_aggregator
    else
        echo "the parameter is wrong~~"
    fi
elif [ $2 = "ppe" ];then
    if [ $3 = "distshop" ];then
        if [[ $1 =~ "searcher" ]];then
            fab -f ppe_machInfo.py -R distshop_ppe_searcher restart_distshop_searcher
        elif [[ $1 =~ "aggregator" ]];then
            fab -f ppe_machInfo.py -R distshop_aggregator restart_distshop_aggregator
        else
            echo "the parameter is wrong~~"
        fi
    elif [ $3 = "mainshop" ];then
        if [[ $1 =~ "searcher" ]];then
            fab -f ppe_machInfo.py -R mainshop_ppe_searcher restart_mainshop_searcher
        elif [[ $1 =~ "aggregator" ]];then
            fab -f ppe_machInfo.py -R mainshop_ppe_aggregator restart_mainshop_aggregator
        else
            echo "the parameter is wrong~~"
        fi
    fi

fi