#!/bin/bash

DIR=$( cd $( dirname -- "$0" ) > /dev/null ; pwd )
cd $DIR
source env.sh

SearchBuildNumber=$1
jobname=$2
grep ERROR $jenkinsJobsPath/${jobname}/builds/${SearchBuildNumber}/log > $autoPath1/errorInJenkinsConsoleLog

