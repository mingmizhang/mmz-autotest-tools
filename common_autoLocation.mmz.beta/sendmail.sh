#! /bin/bash

#获取自动化运行的IP地址
Get_TestCase_RunIP()
{
  if [ "`cat log|grep "Building on"`" ]; then
     ip=******
  else
    ip=`grep "Building remotely on" log|grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'`
  fi
  echo ${ip} 
}


#判断前一次构建是否成功，如果否，先修复
Judge_LastRun_ISPASS()
{
   SearchBuildNum=`expr $SearchBuildNum - 1`
   cd ../$SearchBuildNum
   echo $SearchBuildNum
   if [ "`cat log|grep "Finished: FAILURE"`" ]; then
      echo "Please fix last mistake"
      exit 0
   elif [ "`cat log|grep "Finished: ABORTED"`" ];then
      echo "the last job is not success,it is aborted by others"
      exit 0
   elif [ "`cat log|grep "Finished: SUCCESS"`" ];then
       echo "LastRun is PASS"
       SearchBuildNum=`expr $SearchBuildNum + 1`
       cd ../$SearchBuildNum
   else
       echo "Something is wrong!"
       exit 0
  fi
}

#获取当前job的总的case个数
Get_Case_Number()
{
   SearchBuildNum=`expr $SearchBuildNum - 1`
   cd ../$SearchBuildNum/robot-plugin
   grep "window.output.*All Test" report.html > test.txt
   echo `head -n 1 test.txt|awk -F 'elapsed' '{for(n=1;n<=NF;n++) if($n~".*All Tests") {print $n}}'` > test.txt
   Case_Num=`awk -F ',' '{for(n=1;n<=NF;n++) if($n~".*pass") {print $n}}' test.txt|grep -o "[0-9]\{1,5\}"`
   rm -rf test.txt
   SearchBuildNum=`expr $SearchBuildNum + 1`
   cd ../../$SearchBuildNum
   echo $Case_Num
}

jobname=$1
##find the business name 找到当前job的业务名
tmp=`echo $jobname|awk -F '-' '{for (i=1;i<=NF;i++) {print $i}}'|wc -l`
echo $tmp
if [ $tmp -eq 3 ];then
   bizname=`echo $jobname|awk -F '-' '{print $1}'`
elif [ $tmp -eq 4 ];then
   bizname=`echo $jobname|awk -F '-' '{print $2}'`
fi
echo ${bizname}
source env.sh

if [ $# -lt 1 ]; then
    echo "usage: $0 <jobname>"
    exit 1
fi

cd $jenkinsJobsPath/${jobname}/builds
pwd
echo $jobname
ls -l $jenkinsJobsPath/${jobname}/builds>a.txt

#获取最新自动化case执行的编译号，并进入对应目录
awk -F ' ' ' {if($10=="->")print $9 }' a.txt > b.txt
#cat b.txt
#SearchBuildNum=`tac b.txt |sed -n 6p`
#grep -vE '[:digit:]' b.txt > c.txt
grep  -E '[0-9]' b.txt > c.txt
SearchBuildNum=`cat c.txt|sort -n|tac|head -n 1`
#SearchBuildNum=762
#SearchBuildNum=1822
#SearchBuildNum=117
#SearchBuildNum=3669
echo $SearchBuildNum
cd  $SearchBuildNum
save_job_num=$SearchBuildNum
fail_reason="other"
#判断当前构建的结果并是什么原因的构建
  if [ "`cat log|grep  "Finished: SUCCESS"`" ];then
      echo "the latest job is success"
  elif [ "`cat log|grep "Started by Naginator"`" ]; then
   SearchBuildNum=`expr $SearchBuildNum - 1`
   cd ../$SearchBuildNum
   #=========判断是第一次重试还是第二次重试，如果是第一次重试，直接退出，不进行定位=============
   if [ "`cat log|grep "Started by Naginator"`" ]; then
        echo "Continue to check reason"
   else 
        echo "It's not the last run for code change,please check next build"
        exit 0
   fi  
  #============找到触发失败的代码提交===========================
     SearchBuildNum=`expr $SearchBuildNum - 1` 
     cd ../$SearchBuildNum
     if [ "`cat log|grep  "Started by upstream project"`" ] ;then
        echo "${jobname} build is caused by a SCM change"
     #=======search-it-automation修改================================
     elif [ "`grep "Started by an SCM change" log`" -a  "`grep "originally caused by" log`" == "" ]; then
        Judge_LastRun_ISPASS
        echo "search-it-automation has been changed and cause some test cases fail,please check!"
        Get_Case_Number
	Case_Num=`Get_Case_Number`
	#Case_Num=1
        echo $Case_Num
        mail=`sed -n 5p changelog.xml|cut -d '<' -f2|cut -d '>' -f1`    #从这提取修改代码者邮箱
        echo $mail
        commiter=`echo $mail|awk -F '@' '{print $1}'`
        mlist="${commiter}@163.com"
        echo $mlist
        ##如果服务未启动时，没有robot-plugin文件夹
        if [ ! -d ../$save_job_num/robot-plugin ];then
	  	Pass=0
		report_url="http://******:8000/jenkins/job/${jobname}/${save_job_num}/console"
		fail_reason="qa"
		echo $Case_Num
        	echo python /data/webapps/common_autoLocation.mmz/send1.py $Pass $Case_Num $jobname $mlist $report_url $fail_reason
		python /data/webapps/common_autoLocation.mmz/send1.py $Pass $Case_Num $jobname $mlist $report_url $fail_reason
                exit 0
        fi
        ##提取报告中Total Passed Failed的case个数
        cd ../$save_job_num/robot-plugin
        grep "window.output.*All Test" report.html > test.txt
        echo `head -n 1 test.txt|awk -F 'elapsed' '{for(n=1;n<=NF;n++) if($n~".*All Tests") {print $n}}'` > test.txt
        Fail=`awk -F ',' '{for(n=1;n<=NF;n++) if($n~".*fail") {print $n}}' test.txt|grep -o "[0-9]\{1,5\}"`
        Pass=`awk -F ',' '{for(n=1;n<=NF;n++) if($n~".*pass") {print $n}}' test.txt|grep -o "[0-9]\{1,5\}"`
        rm -rf test.txt
        cd ../../$SearchBuildNum
        if [ "`cat log|grep "run tests for"`" ];then
        	report_url="http://******:8000/jenkins/job/${jobname}/${save_job_num}/robot/report/report.html"
        else
        	report_url="http://******:8000/jenkins/job/${jobname}/${save_job_num}/console"
                Fail=$Pass
                Pass=0
	fi
	fail_reason="qa"
        python /data/webapps/common_autoLocation.mmz/send1.py $Pass $Fail $jobname $mlist $report_url $fail_reason
        exit 0
     else
        echo "${jobname} build is caused by other ways"
        exit 0 
      fi     
     Judge_LastRun_ISPASS
    a=`grep "Started by upstream project" log|awk -F ' ' '{print $NF}'`
    artsCodeBuildNum=${a##*[a-zA-Z]}                ##删除最后一个出现字母的左边所有字符串，保留最后的数字
    #find the upstream job
    upstreamJob=`head -n 1 log|awk -F '\"' '{print $2}'|awk -F 'arts' '{print $2}'`
    upstreamJobName=arts${upstreamJob}
    if [ $jobname="tuangourec-search-tests" ];then
        upstreamJobName=arts-rec-
    fi
    echo $artsCodeBuildNum
    echo $upstreamJobName
   #===============================================================


   #==========打包失败、自动化运行失败日志信息处理=================
      cd $jenkinsJobsPath/${upstreamJobName}/builds/${artsCodeBuildNum}
      if [ "`cat log|grep "Started by an SCM change"`" ]; then  #grep -c 用起来有问题，待看
           echo "arts-${bizname}-build was started by SCM change"
      else
            echo "arts-${bizname}-build was started by other ways"
            exit 0
      fi
      comment=`sed -n 7p changelog.xml`
      echo $comment
      cd $jenkinsJobsPath/${jobname}/builds/$SearchBuildNum
      TestRunIP=$(Get_TestCase_RunIP)
      echo $TestRunIP
      #打包失败情况
      if [ "`cat log|grep "fail to exec: Library/script/deploy.sh"`" ] ; then
         echo "package,failed"
         #$autoPath1/findErrorInJenkinsLog.sh $SearchBuildNum ${jobname}
         fail_reason="developer_package"
         report_url="http://******:8000/jenkins/job/$jobname/$save_job_num/console"
      #打包正确，服务正常启动，case有失败的情况
      elif [ "`cat log|grep "run tests for"`" ];then
         cd ../$save_job_num/robot-plugin
         grep "window.output.*All Test" report.html > test.txt
         echo `head -n 1 test.txt|awk -F 'elapsed' '{for(n=1;n<=NF;n++) if($n~".*All Tests") {print $n}}'` > test.txt
         Fail=`awk -F ',' '{for(n=1;n<=NF;n++) if($n~".*fail") {print $n}}' test.txt|grep -o "[0-9]\{1,5\}"`
         Pass=`awk -F ',' '{for(n=1;n<=NF;n++) if($n~".*pass") {print $n}}' test.txt|grep -o "[0-9]\{1,5\}"`
         rm -rf test.txt
         fail_reason="developer_case"
         echo $fail_reason
         cd ../../$SearchBuildNum
	 report_url="http://******:8000/jenkins/job/${jobname}/${save_job_num}/robot/report/report.html"
      else
          echo "package ,succeeded"
          sshpass -p jenkins@search ssh -p 58422 jenkins@${TestRunIP} "rm -rf /data/webapps/autoLocation2/;mkdir -p /data/webapps/autoLocation2/"
          sshpass -p jenkins@search scp -o StrictHostKeyChecking=no -P 58422 /data/webapps/common_autoLocation/findErrorInServerLogs.sh jenkins@${TestRunIP}:/data/webapps/autoLocation2/
          sshpass -p jenkins@search ssh -p 58422 jenkins@${TestRunIP} "sh /data/webapps/autoLocation2/findErrorInServerLogs.sh ${bizname}"
          fail_reason="developer_down"
          pwd
       fi
  #==========代码提交者和comment提取=========================================
       cd $jenkinsJobsPath/${upstreamJobName}/builds/$artsCodeBuildNum
       mail=`sed -n 5p changelog.xml|cut -d '<' -f2|cut -d '>' -f1`    #从这提取修改代码者邮箱
       echo $mail
      if [ `echo $mail|grep "Mac"` ];then
		echo "the committer is committed by mac"
		person=`echo $mail|awk -F '@' '{print $1}'`
		commiter=`cat /data/webapps/common_autoLocation.mmz/committer_data.txt|awk -F '\t' -v per=$person '{ if($1 == ""per"") print $2 }'`
		echo $commiter
      else
       		commiter=`echo $mail|awk -F '@' '{print $1}'`
      fi
      echo "the commiter is $commiter"
      # MailContent=$autoPath1/mailcontent
       #echo > $MailContent
       #echo $mail
       mlist="${commiter}@163.com"
       echo $mlist
	echo $comment > tmp.txt
	comment=`cat tmp.txt|sed "s/ /_/g" tmp.txt`
       if [ $fail_reason == "developer_package" ];then
	   echo python /data/webapps/common_autoLocation.mmz/send1.py $jobname $mlist $report_url $fail_reason $comment 
	   python /data/webapps/common_autoLocation.mmz/send1.py $jobname $mlist $report_url $fail_reason $comment
	   exit 0
       elif [ $fail_reason == "developer_case" ];then
	     #echo "text"
             echo python /data/webapps/common_autoLocation.mmz/send1.py $Pass $Fail $jobname $mlist $report_url $fail_reason $comment
	     #echo $comment > tmp.txt
             #comment=`cat tmp.txt|sed "s/ /_/g" tmp.txt`
             python /data/webapps/common_autoLocation.mmz/send1.py $Pass $Fail $jobname $mlist $report_url $fail_reason $comment
             exit 0
       elif [ $fail_reason == "developer_down" ];then
	     echo "the server is not up"
	     python /data/webapps/common_autoLocation.mmz/send1.py $jobname $comment $mlist $TestRunIP
	     exit 0
       fi
  #==========业务代码第一次提交导致自动化失败，针对这种情况忽略，继续观察后续运行==============
  elif [ "`cat log|grep  "Started by upstream project"`" ]; then 
      echo "Ignore this failure and wait for next build!"
  elif [ "`cat log|grep  "Started by an SCM change"`" ]; then 
      echo "Ignore this failure and wait for next build!"
   #===========其他情况，可能是环境导致的问题====================
   else
       Judge_LastRun_ISPASS
       echo "Wait for next build! Attention,please!"
       fail_reason="other_reason"
       report_url="http://******:8000/jenkins/job/$jobname/$save_job_num/console"
       python /data/webapps/common_autoLocation.mmz/send1.py $jobname $report_url $fail_reason
       exit 0
  fi





