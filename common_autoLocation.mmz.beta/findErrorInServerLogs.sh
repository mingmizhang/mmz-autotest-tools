#!/bin/bash

#读取环境变量信息

bizname=$1

DIR=$( cd $( dirname -- "$0" ) > /dev/null ; pwd )
cd $DIR
#source env.sh

#去除biz.log和search.log日志里面的WARN和INFO日志
grep -v  "WARN" /data/webapps/${bizname}_bizer/logs/biz.log | grep -v "INFO" > ./errorInBizLog
grep -v  "WARN" /data/webapps/${bizname}_searcher/logs/search.log | grep -v "INFO" >  ./errorInSearchLog

case $bizname in 
shop)
   sed -i '/fail to read wedding banquet conversion rate score/d' ./errorInSearchLog #去除错误日志里并没影响的ERROR
   sed -i '/fail to read brand keyword boost info/d' ./errorInSearchLog
   sed -i '/NativaAdAlert: sc data is too old/d'  ./errorInSearchLog
   ;;
tuangou)
  sed -i '/hotel data validation failure!/d' ./errorInSearchLog
  ;;
*)
  echo "nothing to del" 
  ;;
esac
  
sshpass -p jenkins@search scp -o StrictHostKeyChecking=no -P 58422 ./errorInBizLog  jenkins@******:/data/webapps/common_autoLocation
sshpass -p jenkins@search scp -o StrictHostKeyChecking=no  -P 58422 ./errorInSearchLog jenkins@******:/data/webapps/common_autoLocation
exit #返回******
