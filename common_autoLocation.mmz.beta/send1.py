#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import commands
import re
import os
import urllib
import smtplib
import string
from email.mime.text import MIMEText
from email.header import Header

def sendMail(emailto, subject, content):
    sender = "mingmi.zhang"
    msg = MIMEText(content,_subtype='html',_charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender
    msg['To'] = emailto
    emailto = string.splitfields(emailto, ",")
    #msg['To'] = emailto
    server=smtplib.SMTP('mail.163.com')
    server.sendmail(sender, emailto, msg.as_string())
    server.quit()


if __name__ == '__main__':
    print len(sys.argv)
    #print sys.argv[8]
    if len(sys.argv) == 7:
        print 111
        passed=int(sys.argv[1])
        failed=int(sys.argv[2])
        total=passed+failed
        Bizname=sys.argv[3]
        mail_list=sys.argv[4]
        print mail_list
        commiter=mail_list.split('@',1)[0]
        print commiter
        report_url=sys.argv[5]
        fail_reason=sys.argv[6]
    elif len(sys.argv) == 6:
        print 222
        Bizname=sys.argv[1]
        mail_list=sys.argv[2]
        print mail_list
        commiter=mail_list.split('@',1)[0]
        report_url=sys.argv[3]
        fail_reason=sys.argv[4]
        comment=sys.argv[5]
	failed=1
    elif len(sys.argv) == 8:
        print 333
        passed=int(sys.argv[1])
        print passed
        failed=int(sys.argv[2])
        total=passed+failed
        Bizname=sys.argv[3]
        mail_list=sys.argv[4]
        print mail_list
        commiter=mail_list.split('@',1)[0]
        print commiter
        report_url=sys.argv[5]
        fail_reason=sys.argv[6]
        print fail_reason
        comment=sys.argv[7]
        print comment
    elif len(sys.argv) == 4:
        print 444
        Bizname=sys.argv[1]
        report_url=sys.argv[2]
        fail_reason=sys.argv[3]
        failed=1
    elif len(sys.argv) == 5:
        print 555
        Bizname=sys.argv[1]
        comment=sys.argv[2]
        #fail_reason=sys.argv[3]
        mail_list=sys.argv[3]
        commiter=mail_list.split('@',1)[0]
        fail_reason='developer_down'
        TestRunIP=sys.argv[4]
        failed=1

#    content = '<style type="text/css">#robot-summary-table {text-align: center;border-collapse: collapse;}  #robot-summary-table th {font-weight: normal;    padding: 3px; }  #robot-summary-table td {      font-weight: bold;      border-left: 1px solid #888;      margin: 0px;      padding: 3px;}  #robot-summary-table .table-upper-row {  	  border-bottom: 1px solid #888; }  #robot-summary-table .fail {      color: #f00;}  #robot-summary-table .pass { color: #0f0; } </style><table class="table" id="robot-summary-table" /><tbody /><tr /><th /></th /><th />Total</th /><th />Failed</th /><th />Passed</th /></tr><tr /><th />All tests</th /><td class="table-upper-row" style="border-left:0px;" />%d</td/><td class="table-upper-row"/><span class="pass"/>%d</span/></td/><td class="table-upper-row" />%d</td /></tr /></tbody /></table /><p /><a href="%s">&gt; Browse results</a></p />' % (total, failed, passed, report_url)
#    content = '<p style="color: black">Hello,mingmi.zhang<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;你提交的search-it-automation的修改，导致自动化case失败<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;case失败情况如下：</p><table border=6 width=200 hspace=100 cellpadding=10><tr><th>ALL</th><th>PASS</th><th>FAIL</th></tr><tr><th>%s</th><th>%s</th><th bgcolor="#FF0000">%s</th></tr></table><p><a href="http://baidu.com">&gt;Browse results</a></p>' % (total, passed, failed)

    if fail_reason == 'qa':
    	content = ' <p style="color: black">Hello,<font color="red" size="3.5"><b>&nbsp;&nbsp;%s&nbsp;&nbsp;:</b></font><br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;定位到你提交的search-it-automation项目代码的修改，导致beta自动化<font color="#00dd00" size="3.5"><b>%s</b></font>的job中的case失败，请分析解决！<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;case失败情况如下：</p> <table border="6" width="200" hspace="100" cellpadding="10" style="margin-left:24px;"><tr><th>ALL</th><th>PASS</th><th>FAIL</th></tr><tr><td align=center>%s</th><td align=center>%s</th><td bgcolor="#FF0000" align=center>%s</th></tr></table><br><p><a href="%s" style="margin-left:26px;">&gt;点击此处查看详情</a></p>' % (commiter, Bizname, total, passed, failed, report_url)
    elif fail_reason == 'developer_package':
        content = ' <p style="color: black">Hello,<font color="red" size="3.5"><b>&nbsp;&nbsp;%s&nbsp;&nbsp;:</b></font><br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;定位到你提交的comment为%s的项目代码的修改，导致beta自动化<font color="#00dd00" size="3.5"><b>%s</b></font>的job失败。<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s的job失败主要原因是<font color="red" size="3.5">项目代码打包失败</font>，请分析解决下！！！</p><br><p><a href="%s" style="margin-left:26px;">&gt;点击此处查看打包失败的日志详情</a></p>' % (commiter, comment, Bizname, Bizname, report_url)
    elif fail_reason == 'developer_case':
        print comment
     	content = ' <p style="color: black">Hello,<font color="red" size="3.5"><b>&nbsp;&nbsp;%s&nbsp;&nbsp;:</b></font><br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;定位到你提交的comment为%s的项目代码的修改，导致beta自动化<font color="#00dd00" size="3.5"><b>%s</b></font>的job中的case失败，请分析解决！<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;case失败情况如下：</p> <table border="6" width="200" hspace="100" cellpadding="10" style="margin-left:24px;"><tr><th>ALL</th><th>PASS</th><th>FAIL</th></tr><tr><td align=center>%s</th><td align=center>%s</th><td bgcolor="#FF0000" align=center>%s</th></tr></table><br><p><a href="%s" style="margin-left:26px;">&gt;<b>点击此处查看详情</b></a></p>' % (commiter, comment, Bizname, total, passed, failed, report_url)
	#print fail_reason
        #content = ' <p style="color: black">Hello,<font color="red" size="3.5"><b>&nbsp;&nbsp;%s&nbsp;&nbsp;:</b></font><br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;定位到你提交的comment为%s的项目代码的修改，导致beta自动化<font color="#00dd00" size="3.5"><b>%s</b></font>的job失败。<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s的job失败主要原因是<font color="red" size="3.5">项目代码打包失败</font>，请分析解决下！！！</p><p><a href="%s" style="margin-left:26px;">&gt;点击此处查看打包失败的日志详情</a></p>' % (commiter, comment, Bizname, Bizname, report_url)
    elif fail_reason == 'developer_down':
        content = ' <p style="color: black">Hello,<font color="red" size="3.5"><b>&nbsp;&nbsp;%s&nbsp;&nbsp;:</b></font><br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;定位到你提交的comment为%s代码的修改，导致beta自动化<font color="#00dd00" size="3.5"><b>%s</b></font>的job失败。<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s的job失败主要原因是<font color="red" size="3.5">服务未正常启动</font>，请和对应的QA确认，登录到<font color="red" size="3.5"><b>%s</b></font>机器查看该服务失败的详细日志！！！' % (commiter, comment, Bizname, Bizname, TestRunIP)
    elif fail_reason == 'other_reason':
        content = ' <p style="color: black">Hello,<font color="red" size="3.5"><b>&nbsp;&nbsp;mingmi.zhang&nbsp;&nbsp;:</b></font><br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;定位到<font color="#00dd00" size="3.5"><b>%s</b></font>的beta自动化job失败，请解决自动化环境问题或联系对应的开发解决!<p><a href="%s" style="margin-left:26px;">&gt;点击此处查看对应job失败的详情</a></p>' % (Bizname, report_url)
    else :
	    print 'hah'	
	    pass
    content = content[0:2000]
    subject = "[Failed] %s Automation Test On beta"%(Bizname)
    if fail_reason == 'other_reason':
        mail='mingmi.zhang'
    else :
        print "tttt"
        plat=',mingmi.zhang'
	mail=mail_list+plat
    	print mail
    sendMail(mail,subject,content)
    sys.exit(0)
