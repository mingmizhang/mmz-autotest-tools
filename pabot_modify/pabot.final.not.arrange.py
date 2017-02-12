#!/usr/bin/env python

#  Copyright 2014->future! Mikko Korpela
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  partly based on work by Nokia Solutions and Networks Oyj
"""A parallel executor for Robot Framework test cases.
Version 0.31.

Supports all Robot Framework command line options and also following
options (these must be before normal RF options):

--verbose
  more output

--command [ACTUAL COMMANDS TO START ROBOT EXECUTOR] --end-command
  RF script for situations where pybot is not used directly

--processes [NUMBER OF PROCESSES]
  How many parallel executors to use (default max of 2 and cpu count)

--resourcefile [FILEPATH]
  Indicator for a file that can contain shared variables for
  distributing resources.

--pabotlib
  Start PabotLib remote server. This enables locking and resource
  distribution between parallel test executions.

--pabotlibhost [HOSTNAME]
  Host name of the PabotLib remote server (default is 127.0.0.1)

--pabotlibport [PORT]
  Port number of the PabotLib remote server (default is 8270)

--suitesfrom [FILEPATH TO OUTPUTXML]
  Optionally read suites from output.xml file. Failed suites will run
  first and longer running ones will be executed before shorter ones.

--argumentfile[INTEGER] [FILEPATH]
  Run same suite with multiple argumentfile options.
  For example "--argumentfile1 arg1.txt --argumentfile2 arg2.txt".

Copyright 2016 Mikko Korpela - Apache 2 License
"""

import os
import re
import sys
import time
import datetime
import multiprocessing
from glob import glob
from StringIO import StringIO
import shutil
import subprocess
import threading
from contextlib import contextmanager
from robot import run, rebot
from robot import __version__ as ROBOT_VERSION
from robot.api import ExecutionResult
from robot.errors import Information
from robot.result.visitor import ResultVisitor
from robot.libraries.Remote import Remote
from multiprocessing.pool import ThreadPool
from robot.run import USAGE
from robot.utils import ArgumentParser
import signal
import PabotLib
from result_merger import merge
import Queue
import threading
import traceback
import copy
import pydevd

CTRL_C_PRESSED = False
MESSAGE_QUEUE = Queue.Queue()
_PABOTLIBURI = '127.0.0.1:8270'
ARGSMATCHER = re.compile(r'--argumentfile(\d+)')

class Color:
    SUPPORTED_OSES = ['posix']

    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    YELLOW = '\033[93m'


def execute_and_wait_with(args):
    global CTRL_C_PRESSED
    if CTRL_C_PRESSED:
        # Keyboard interrupt has happened!
        return
    time.sleep(0)
    datasources, outs_dir, options, suite_name, command, verbose, (argfile_index, argfile) = args
    datasources = [d.encode('utf-8') if isinstance(d, unicode) else d
                   for d in datasources]
    outs_dir = os.path.join(outs_dir, argfile_index, suite_name)
    cmd = command + _options_for_custom_executor(options,
                                                 outs_dir,
                                                 suite_name,
                                                 argfile) + datasources
    cmd = [c if (' ' not in c) and (';' not in c) else '"%s"' % c for c in cmd]
    os.makedirs(outs_dir)
    with open(os.path.join(outs_dir, 'stdout.txt'), 'w') as stdout:
        with open(os.path.join(outs_dir, 'stderr.txt'), 'w') as stderr:
            process, rc = _run(cmd, stderr, stdout, suite_name, verbose)
    if rc != 0:
        _write(_execution_failed_message(suite_name, rc, verbose), Color.RED)
    else:
        _write('PASSED %s' % suite_name, Color.GREEN)


def _run(cmd, stderr, stdout, suite_name, verbose):
    process = subprocess.Popen(' '.join(cmd),
                               shell=True,
                               stderr=stderr,
                               stdout=stdout)
    if verbose:
        _write('[PID:%s] EXECUTING PARALLEL SUITE %s with command:\n%s' %
               (process.pid, suite_name, ' '.join(cmd)))
    else:
        _write('[PID:%s] EXECUTING %s' % (process.pid, suite_name))
    return process, _wait_for_return_code(process, suite_name)


def _wait_for_return_code(process, suite_name):
    rc = None
    elapsed = 0
    ping_time = ping_interval = 150
    while rc is None:
        rc = process.poll()
        time.sleep(0.3)
        elapsed += 1
        if elapsed == ping_time:
            ping_interval += 50
            ping_time += ping_interval
            _write('[PID:%s] still running %s after %s seconds '
                   '(next ping in %s seconds)'
                   % (process.pid, suite_name, elapsed / 10.0,
                      ping_interval / 10.0))
    return rc


def _execution_failed_message(suite_name, rc, verbose):
    if not verbose:
        return 'FAILED %s' % suite_name
    return 'Execution failed in %s with %d failing test(s)' % (suite_name, rc)


def _options_for_custom_executor(*args):
    return _options_to_cli_arguments(_options_for_executor(*args))


def _options_for_executor(options, outs_dir, suite_name, argfile):
    options = options.copy()
    options['log'] = 'NONE'
    options['report'] = 'NONE'
    options['xunit'] = 'NONE'
    options['suite'] = suite_name
    options['outputdir'] = outs_dir
    options['variable'] = options.get('variable')
    pabotLibURIVar = 'PABOTLIBURI:%s' % _PABOTLIBURI
    # Prevent multiple appending of PABOTLIBURI variable setting
    if pabotLibURIVar not in options['variable']:
        options['variable'].append(pabotLibURIVar)
    if argfile:
        options['argumentfile'] = argfile
    return _set_terminal_coloring_options(options)


def _set_terminal_coloring_options(options):
    if ROBOT_VERSION >= '2.9':
        options['consolecolors'] = 'off'
        options['consolemarkers'] = 'off'
    else:
        options['monitorcolors'] = 'off'
    if ROBOT_VERSION >= '2.8' and ROBOT_VERSION < '2.9':
        options['monitormarkers'] = 'off'
    return options


def _options_to_cli_arguments(opts):
    res = []
    for k, v in opts.items():
        if isinstance(v, str):
            res += ['--' + str(k), str(v)]
        elif isinstance(v, unicode):
            res += ['--' + str(k), v.encode('utf-8')]
        elif isinstance(v, bool) and (v is True):
            res += ['--' + str(k)]
        elif isinstance(v, list):
            for value in v:
                if isinstance(value, unicode):
                    res += ['--' + str(k), value.encode('utf-8')]
                else:
                    res += ['--' + str(k), str(value)]
    return res


class GatherSuiteNames(ResultVisitor):

    def __init__(self):
        self.result = []

    def end_suite(self, suite):
        if len(suite.tests):
            self.result.append(suite.longname)


def get_suite_names(output_file):
    if not os.path.isfile(output_file):
        print "get_suite_names: output_file='%s' does not exist" % output_file
        return []
    try:
        e = ExecutionResult(output_file)
        gatherer = GatherSuiteNames()
        e.visit(gatherer)
        return gatherer.result
    except BaseException, be:
        print "Exception in get_suite_names!",be
        return []


def _parse_args(args):
    pabot_args = {'command': ['pybot'],
                  'verbose': False,
                  'pabotlib': False,
                  'pabotlibhost': '127.0.0.1',
                  'pabotlibport': 8270,
                  'processes': max(multiprocessing.cpu_count(), 2),
                  'argumentfiles': []}
    while args and args[0] in ['--'+param for param in ['command',
                                                        'processes',
                                                        'verbose',
                                                        'resourcefile',
                                                        'pabotlib',
                                                        'pabotlibhost',
                                                        'pabotlibport',
                                                        'suitesfrom']] or \
            ARGSMATCHER.match(args[0]):
        if args[0] == '--command':
            end_index = args.index('--end-command')
            pabot_args['command'] = args[1:end_index]
            args = args[end_index+1:]
        if args[0] == '--processes':
            pabot_args['processes'] = int(args[1])
            args = args[2:]
        if args[0] == '--verbose':
            pabot_args['verbose'] = True
            args = args[1:]
        if args[0] == '--resourcefile':
            pabot_args['resourcefile'] = args[1]
            args = args[2:]
        if args[0] == '--pabotlib':
            pabot_args['pabotlib'] = True
            args = args[1:]
        if args[0] == '--pabotlibhost':
            pabot_args['pabotlibhost'] = args[1]
            args = args[2:]
        if args[0] == '--pabotlibport':
            pabot_args['pabotlibport'] = int(args[1])
            args = args[2:]
        if args[0] == '--suitesfrom':
            pabot_args['suitesfrom'] = args[1]
            args = args[2:]
        match = ARGSMATCHER.match(args[0])
        if ARGSMATCHER.match(args[0]):
            pabot_args['argumentfiles'] += [(match.group(1), args[1])]
            args = args[2:]
    options, datasources = ArgumentParser(USAGE,
                                          auto_pythonpath=False,
                                          auto_argumentfile=False).\
        parse_args(args)
    if len(datasources) > 1 and options['name'] is None:
        options['name'] = 'Suites'
    keys = set()
    for k in options:
        if options[k] is None:
            keys.add(k)
    for k in keys:
        del options[k]
    return options, datasources, pabot_args


def solve_suite_names(outs_dir, datasources, options, pabot_args):
    if 'suitesfrom' in pabot_args:
        return _suites_from_outputxml(pabot_args['suitesfrom'])
    opts = _options_for_dryrun(options, outs_dir)
    with _with_modified_robot():
        run(*datasources, **opts)
    output = os.path.join(outs_dir, opts['output'])
    suite_names = get_suite_names(output)
    return sorted(set(suite_names))



def sort_suite_names_include_init(suite_names):
    print len(suite_names)
    suite_names_with_init=[]
    suite_names_with_end=[]
    suite_names_without_init=[]
    for suite in suite_names:
        if("Init" in suite):
            suite_names_with_init.append(suite)
        elif("Destory" in suite):
            suite_names_with_end.append(suite)
        else:
            suite_names_without_init.append(suite)
    for suite_test in suite_names_with_init:
        dir_name=suite_test.rpartition(".")[0]
        i=0
        dir_depth = len(dir_name) - 1
        for suite in suite_names_without_init:
            if (suite.startswith(dir_name)):
                suite_names_without_init.insert(i,suite_test)
                break
            else:
                i=i+1
    for suite_test in suite_names_with_end:
        dir_name=suite_test.rpartition(".")[0]
        i=0
        dir_depth = len(dir_name) - 1
        for i in range(0,len(suite_names_without_init)):
            suite=suite_names_without_init[i]
            if(suite.startswith(dir_name)):
                i=i+1
                suite = suite_names_without_init[i]
                while (suite.startswith(dir_name) and i<len(suite_names_without_init)):
                    i = i + 1
                    if(i<len(suite_names_without_init)):
                        suite=suite_names_without_init[i]
                    else:
                        break
                suite_names_without_init.insert(i,suite_test)
                break
    del suite_names_with_init
    del suite_names_with_end
    return suite_names_without_init

@contextmanager
def _with_modified_robot():
    TsvReader = None
    old_read = None
    try:
        from robot.parsing.tsvreader import TsvReader, Utf8Reader

        def new_read(self, tsvfile, populator):
            process = False
            first = True
            for row in Utf8Reader(tsvfile).readlines():
                row = self._process_row(row)
                cells = [self._process_cell(cell)
                         for cell in self.split_row(row)]
                if cells and cells[0].strip().startswith('*') and \
                        populator.start_table([c.replace('*', '')
                                               for c in cells]):
                    process = True
                elif process:
                    if cells[0].strip() != '' or \
                            (len(cells) > 1 and
                                 ('[' in cells[1] or (first and '...' in cells[1]))):
                        populator.add(cells)
                        first = True
                    elif first:
                        populator.add(['', 'No Operation'])
                        first = False
            populator.eof()

        old_read = TsvReader.read
        TsvReader.read = new_read
    except:
        pass

    try:
        yield
    finally:
        if TsvReader:
            TsvReader.read = old_read


class SuiteNotPassingsAndTimes(ResultVisitor):

    def __init__(self):
        self.suites = []

    def start_suite(self, suite):
        if len(suite.tests) > 0:
            self.suites.append((not suite.passed,
                                suite.elapsedtime,
                                suite.longname))


def _suites_from_outputxml(outputxml):
    res = ExecutionResult(outputxml)
    suite_times = SuiteNotPassingsAndTimes()
    res.visit(suite_times)
    return [suite for (_, _, suite) in reversed(sorted(suite_times.suites))]


def _options_for_dryrun(options, outs_dir):
    options = options.copy()
    options['log'] = 'NONE'
    options['report'] = 'NONE'
    options['xunit'] = 'NONE'
    if ROBOT_VERSION >= '2.8':
        options['dryrun'] = True
    else:
        options['runmode'] = 'DryRun'
    options['output'] = 'suite_names.xml'
    # --timestampoutputs is not compatible with hard-coded suite_names.xml
    options['timestampoutputs'] = False
    options['outputdir'] = outs_dir
    options['stdout'] = StringIO()
    options['stderr'] = StringIO()
    options['listener'] = []
    return _set_terminal_coloring_options(options)


def _options_for_rebot(options, start_time_string, end_time_string):
    rebot_options = options.copy()
    rebot_options['starttime'] = start_time_string
    rebot_options['endtime'] = end_time_string
    rebot_options['monitorcolors'] = 'off'
    if ROBOT_VERSION >= '2.8':
        options['monitormarkers'] = 'off'
    return rebot_options


def _now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def _print_elapsed(start, end):
    elapsed = end - start
    millis = int((elapsed * 1000) % 1000)
    seconds = int(elapsed) % 60
    elapsed_minutes = (int(elapsed)-seconds)/60
    minutes = elapsed_minutes % 60
    elapsed_hours = (elapsed_minutes-minutes)/60
    elapsed_string = ''
    if elapsed_hours > 0:
        elapsed_string += '%d hours ' % elapsed_hours
    elapsed_string += '%d minutes %d.%d seconds' % (minutes, seconds, millis)
    print 'Elapsed time: '+elapsed_string


def keyboard_interrupt(*args):
    global CTRL_C_PRESSED
    CTRL_C_PRESSED = True


def _parallel_execute_modify(datasources, options, outs_dir, pabot_args, suite_names):
    original_signal_handler = signal.signal(signal.SIGINT, keyboard_interrupt)
    #pool = ThreadPool(pabot_args['processes'])
    suite_length=len(suite_names)
    suiteGroupNum=[]
    i=0
    print "suite names"
    print suite_names
    for suite in suite_names:
        if("Init" in suite):
            suiteGroupNum.append(i)
        elif("Destory" in suite):
            suiteGroupNum.append(i)
        i=i+1
    print suiteGroupNum
    suiteGroup=[]
    if(len(suiteGroupNum)==0):
        suiteGroup=suite_names
    else:
        for j in range(0,len(suiteGroupNum)):
            print j
            list_start=suite_names[suiteGroupNum[j]]
            suiteGroup.append(list_start)
            list_middle=[]
            print len(suite_names),len(suiteGroupNum),suiteGroupNum[j]
            if(j==(len(suiteGroupNum)-1) and suiteGroupNum[j]==(len(suite_names)-1)):
                break
            elif(j==(len(suiteGroupNum)-1) and suiteGroupNum[j]<(len(suite_names)-1)):
                suiteGroupNum.append(len(suite_names))
                print suiteGroupNum
            if(suiteGroupNum[j]+1<suiteGroupNum[j+1]):
                for m in range(suiteGroupNum[j]+1,suiteGroupNum[j+1]):
                    list_middle.append(suite_names[m])
                suiteGroup.append(list_middle)
    print "***suiteGroup"
    print suiteGroup
    print "***suiteGroup"
    for i in range(0,len(suiteGroup)):
        suite_names=suiteGroup[i]
        print suite_names
        print type(suite_names)
        if(isinstance(suite_names,str)):
            print "Init or End tests"
            pool = ThreadPool(1)
            suite=suite_names
            for argfile in pabot_args['argumentfiles'] or [("", None)]:
        	    pollArgsList=[(datasources, outs_dir, options, suite,pabot_args['command'], pabot_args['verbose'], argfile)]
		    print pollArgsList
       	            result=pool.map_async(execute_and_wait_with,pollArgsList)
            pool.close()
            pool.join()
        else:
            print "Middle tests"
            print suite_names
            pool = ThreadPool(pabot_args['processes'])
            result = pool.map_async(execute_and_wait_with,
                                    ((datasources, outs_dir, options, suite,
                                      pabot_args['command'], pabot_args['verbose'], argfile)
                                     for suite in suite_names
                                     for argfile in pabot_args['argumentfiles'] or [("", None)]))
            pool.close()
            pool.join()
    while not result.ready():
        #keyboard interrupt is executed in main thread
        #and needs this loop to get time to get executed
        try:
            time.sleep(0.3)
        except IOError:
            keyboard_interrupt()
    signal.signal(signal.SIGINT, original_signal_handler)

def _parallel_execute_arrange(datasources, options, outs_dir, pabot_args, suite_names, para_mode):
    if (para_mode=="single"):
        original_signal_handler = signal.signal(signal.SIGINT, keyboard_interrupt)
    suite_length=len(suite_names)
    suiteGroupNum=[]
    i=0
    for suite in suite_names:
        if("Init" in suite):
            suiteGroupNum.append(i)
        elif("Destory" in suite):
            suiteGroupNum.append(i)
        i=i+1
    suiteGroup=[]
    if(len(suiteGroupNum)==0):
        suiteGroup=suite_names
    else:
        for j in range(0,len(suiteGroupNum)):
            list_start=suite_names[suiteGroupNum[j]]
            suiteGroup.append(list_start)
            list_middle=[]
            if(j==(len(suiteGroupNum)-1) and suiteGroupNum[j]==(len(suite_names)-1)):
                break
            elif(j==(len(suiteGroupNum)-1) and suiteGroupNum[j]<(len(suite_names)-1)):
                suiteGroupNum.append(len(suite_names))
            if(suiteGroupNum[j]+1<suiteGroupNum[j+1]):
                for m in range(suiteGroupNum[j]+1,suiteGroupNum[j+1]):
                    list_middle.append(suite_names[m])
                suiteGroup.append(list_middle)
    for i in range(0,len(suiteGroup)):
        suite_names=suiteGroup[i]
        if(isinstance(suite_names,str)):
            print "Running Init or End tests"
            pool = ThreadPool(1)
            suite=suite_names
            for argfile in pabot_args['argumentfiles'] or [("", None)]:
        	    pollArgsList=[(datasources, outs_dir, options, suite,pabot_args['command'], pabot_args['verbose'], argfile)]
       	            result=pool.map_async(execute_and_wait_with,pollArgsList)
            pool.close()
            pool.join()
        else:
            print "Running Middle tests"
            pool = ThreadPool(pabot_args['processes'])
            result = pool.map_async(execute_and_wait_with,
                                    ((datasources, outs_dir, options, suite,
                                      pabot_args['command'], pabot_args['verbose'], argfile)
                                     for suite in suite_names
                                     for argfile in pabot_args['argumentfiles'] or [("", None)]))
            pool.close()
            pool.join()
    while not result.ready():
        #keyboard interrupt is executed in main thread
        #and needs this loop to get time to get executed
        try:
            time.sleep(0.3)
        except IOError:
            keyboard_interrupt()
    if (para_mode == "single"):
        signal.signal(signal.SIGINT, original_signal_handler)

def _parallel_execute_merge(datasources, options, outs_dir, pabot_args, suite_names):
    #original_signal_handler = signal.signal(signal.SIGINT, keyboard_interrupt)
    #pool = ThreadPool(pabot_args['processes'])
    suite_length=len(suite_names)
    suiteGroupNum=[]
    i=0
    print "suite names"
    print suite_names
    for suite in suite_names:
        if("Init" in suite):
            suiteGroupNum.append(i)
        elif("Destory" in suite):
            suiteGroupNum.append(i)
        i=i+1
    print suiteGroupNum
    suiteGroup=[]
    if(len(suiteGroupNum)==0):
        suiteGroup=suite_names
    else:
        for j in range(0,len(suiteGroupNum)):
            print j
            list_start=suite_names[suiteGroupNum[j]]
            suiteGroup.append(list_start)
            list_middle=[]
            print len(suite_names),len(suiteGroupNum),suiteGroupNum[j]
            if(j==(len(suiteGroupNum)-1) and suiteGroupNum[j]==(len(suite_names)-1)):
                break
            elif(j==(len(suiteGroupNum)-1) and suiteGroupNum[j]<(len(suite_names)-1)):
                suiteGroupNum.append(len(suite_names))
                print suiteGroupNum
            if(suiteGroupNum[j]+1<suiteGroupNum[j+1]):
                for m in range(suiteGroupNum[j]+1,suiteGroupNum[j+1]):
                    list_middle.append(suite_names[m])
                suiteGroup.append(list_middle)
    print "***suiteGroup"
    print suiteGroup
    print "***suiteGroup"
    for i in range(0,len(suiteGroup)):
        suite_names=suiteGroup[i]
        print suite_names
        print type(suite_names)
        if(isinstance(suite_names,str)):
            print "Init or End tests"
            pool = ThreadPool(1)
            suite=suite_names
            for argfile in pabot_args['argumentfiles'] or [("", None)]:
        	    pollArgsList=[(datasources, outs_dir, options, suite,pabot_args['command'], pabot_args['verbose'], argfile)]
		    print pollArgsList
       	            result=pool.map_async(execute_and_wait_with,pollArgsList)
            pool.close()
            pool.join()
        else:
            print "Middle tests"
            print suite_names
            pool = ThreadPool(pabot_args['processes'])
            result = pool.map_async(execute_and_wait_with,
                                    ((datasources, outs_dir, options, suite,
                                      pabot_args['command'], pabot_args['verbose'], argfile)
                                     for suite in suite_names
                                     for argfile in pabot_args['argumentfiles'] or [("", None)]))
            pool.close()
            pool.join()
    while not result.ready():
        #keyboard interrupt is executed in main thread
        #and needs this loop to get time to get executed
        try:
            time.sleep(0.3)
        except IOError:
            keyboard_interrupt()
    #signal.signal(signal.SIGINT, original_signal_handler)

def _output_dir(options, cleanup=True):
    outputdir = options.get('outputdir', '.')
    outpath = os.path.join(outputdir, 'pabot_results')
    if cleanup and os.path.isdir(outpath):
        shutil.rmtree(outpath)
    return outpath


def _copy_screenshots(options):
    pabot_outputdir = _output_dir(options, cleanup=False)
    outputdir = options.get('outputdir', '.')
    for location, dir_names, file_names in os.walk(pabot_outputdir):
        for file_name in file_names:
            # We want ALL screenshots copied, not just selenium ones!
            if file_name.endswith(".png"):
                prefix = os.path.relpath(location, pabot_outputdir)
                # But not .png files in any sub-folders of "location"
                if os.sep in prefix:
                    continue
                dst_file_name = '-'.join([prefix, file_name])
                shutil.copyfile(os.path.join(location, file_name),
                                os.path.join(outputdir, dst_file_name))


def _report_results(outs_dir, pabot_args, options, start_time_string, tests_root_name):
    if pabot_args['argumentfiles']:
        outputs = []
        for index, _ in pabot_args['argumentfiles']:
            outputs += [_merge_one_run(os.path.join(outs_dir, index), options, tests_root_name,
                                       outputfile=os.path.join('pabot_results', 'output%s.xml' % index))]
            _copy_screenshots(options)
        options['output'] = 'output.xml'
        return rebot(*outputs, **_options_for_rebot(options,
                                                    start_time_string, _now()))
    else:
        return _report_results_for_one_run(outs_dir, options, start_time_string, tests_root_name)


def _report_results_for_one_run(outs_dir, options, start_time_string, tests_root_name):
    output_path = _merge_one_run(outs_dir, options, tests_root_name)
    _copy_screenshots(options)
    print 'Output:  %s' % output_path
    options['output'] = None  # Do not write output again with rebot
    return rebot(output_path, **_options_for_rebot(options,
                                                   start_time_string, _now()))


def _merge_one_run(outs_dir, options, tests_root_name, outputfile='output.xml'):
    output_path = os.path.abspath(os.path.join(
        options.get('outputdir', '.'),
        options.get('output', outputfile)))
    merge(sorted(glob(os.path.join(outs_dir, '**/*.xml'))),
          options, tests_root_name).save(output_path)
    return output_path


def _writer():
    while True:
        message = MESSAGE_QUEUE.get()
        print message
        sys.stdout.flush()


def _write(message, color=None):
    MESSAGE_QUEUE.put(_wrap_with(color, message))


def _wrap_with(color, message):
    if _is_output_coloring_supported() and color:
        return "%s%s%s" % (color, message, Color.ENDC)
    return message


def _is_output_coloring_supported():
    return sys.stdout.isatty() and os.name in Color.SUPPORTED_OSES


def _start_message_writer():
    t = threading.Thread(target=_writer)
    t.setDaemon(True)
    t.start()


def _start_remote_library(pabot_args):
    global _PABOTLIBURI
    _PABOTLIBURI = '%s:%s' % (pabot_args['pabotlibhost'],
                              pabot_args['pabotlibport'])
    if not pabot_args['pabotlib']:
        return None
    if pabot_args.get('resourcefile') and not os.path.exists(
            pabot_args['resourcefile']):
        _write('Warning: specified resource file doesn\'t exist.'
               ' Some tests may fail or continue forever.', Color.YELLOW)
        pabot_args['resourcefile'] = None
    return subprocess.Popen('python %s %s %s %s' %
                            (os.path.abspath(PabotLib.__file__),
                             pabot_args.get('resourcefile'),
                             pabot_args['pabotlibhost'],
                             pabot_args['pabotlibport']),
                            shell=True)


def _stop_remote_library(process):
    _write('Stopping PabotLib process')
    Remote(_PABOTLIBURI).run_keyword('stop_remote_server', [], {})
    i = 50
    while i > 0 and process.poll() is None:
        time.sleep(0.3)
        i -= 1
    if i == 0:
        _write('Could not stop PabotLib Process in 5 seconds ' \
              '- calling terminate', Color.YELLOW)
        process.terminate()
    else:
        _write('PabotLib process stopped')


def _get_suite_root_name(suite_names):
    top_names = [x.split('.')[0] for x in suite_names]
    if top_names.count(top_names[0]) == len(top_names):
        return top_names[0]
    return ''


def main_original(args):
    start_time = time.time()
    start_time_string = _now()
    lib_process = None
    # NOTE: timeout option
    try:
        _start_message_writer()
        options, datasources, pabot_args = _parse_args(args)
        print options
        print datasources
        print pabot_args
        lib_process = _start_remote_library(pabot_args)
        outs_dir = _output_dir(options)
        suite_names = solve_suite_names(outs_dir, datasources, options,
                                        pabot_args)
        print suite_names
        suite_names = sort_suite_names_include_init(suite_names)
        print suite_names
        if suite_names:
            _parallel_execute_modify(datasources, options, outs_dir, pabot_args,
                              suite_names)
            sys.exit(_report_results(outs_dir, pabot_args, options, start_time_string,
                                     _get_suite_root_name(suite_names)))
        else:
            print 'No tests to execute'
    except Information, i:
        print __doc__
        print i.message
    finally:
        if lib_process:
            _stop_remote_library(lib_process)
        _print_elapsed(start_time, time.time())

def main_report_merge(datasources, options, outs_dir, pabot_args,suite_names,lib_process):
    start_time = time.time()
    start_time_string = _now()
    # NOTE: timeout option
    try:
        if suite_names:
            _parallel_execute_merge(datasources, options, outs_dir, pabot_args,
                              suite_names)
            sys.exit(_report_results(outs_dir, pabot_args, options, start_time_string,
                                     _get_suite_root_name(suite_names)))
        else:
            print 'No tests to execute'
    except Information, i:
        print __doc__
        print i.message
    finally:
        if lib_process:
            _stop_remote_library(lib_process)
        _print_elapsed(start_time, time.time())

def generate_suite_xml(args):
    start_time = time.time()
    start_time_string = _now()
    lib_process = None
    # NOTE: timeout option
    _start_message_writer()
    options, datasources, pabot_args = _parse_args(args)
    lib_process = _start_remote_library(pabot_args)
    outs_dir = _output_dir(options)
    suite_names = solve_suite_names(outs_dir, datasources, options,
                                    pabot_args)
    suite_names = sort_suite_names_include_init(suite_names)
    print suite_names
    return datasources, options, outs_dir, pabot_args,suite_names,lib_process

def pabot_cmd_parse(args):
    pabot_cmd_list=[]
    pabot_cmd_list.append(0)
    for i in range(0,len(args)):
        if("pabot" in args[i]):
            pabot_cmd_list.append(i)
            i=i+1
        else:
            i=i+1
    return pabot_cmd_list


class Consumer(threading.Thread):
    def run(self):
        global merge_queue
        while merge_queue.qsize() > 0:
            cmd = merge_queue.get()
            main_report_merge(cmd[0],cmd[1],cmd[2],cmd[3],cmd[4],cmd[5])




merge_queue = Queue.Queue(maxsize=10)
# options_list = []
# datasources_list = []
# pabot_args_list = []
# outs_dir_list = []
# suite_names_list=[]
def main(args):
    pydevd.settrace('172.24.96.112',port=57007, stdoutToServer=True, stderrToServer=True)
    pabot_cmd_list = pabot_cmd_parse(sys.argv[1:])
    if (len(pabot_cmd_list) == 1):
        main_original(sys.argv[1:])
    else:
        # could use multiplythread
        i = 1
        pabot_index = 0
        options_list_mm = []
        datasources_list = []
        pabot_args_list = []
        outs_dir_list = []
        suite_names_list = []
        while (i <= len(pabot_cmd_list)):
            if (i < len(pabot_cmd_list)):
                datasources, options, outs_dir, pabot_args, suite_names, lib_process = generate_suite_xml(
                    sys.argv[pabot_index + 1:pabot_cmd_list[i] + 1])
                print outs_dir
                merge_queue.put([datasources, options, outs_dir, pabot_args, suite_names, lib_process])
            else:
                datasources, options, outs_dir, pabot_args, suite_names, lib_process = generate_suite_xml(
                    sys.argv[pabot_index + 1:])
                merge_queue.put([datasources, options, outs_dir, pabot_args, suite_names, lib_process])
            # tmp = copy.deepcopy(options)
            options_list_mm.append(copy.deepcopy(options))
            # options_list_mm.append(options)
            datasources_list.append(copy.deepcopy("".join(datasources[0])))
            #pabot_args_list.append(pabot_args)
            pabot_args_list.append(copy.deepcopy(pabot_args))
            #outs_dir_list.append(outs_dir)
            outs_dir_list.append(copy.deepcopy(outs_dir))
            suite_names_list.append(copy.deepcopy(suite_names))
            if (i < len(pabot_cmd_list)):
                pabot_index = pabot_cmd_list[i] + 1
            i = i + 1
        size = merge_queue.qsize()
        print outs_dir_list
        out_dir_common,suite_names_entire=generate_pabot_suiteXml(outs_dir_list,options_list_mm,datasources_list,pabot_args_list)
        print out_dir_common
        threads=[]
        for i in range(size):
            c = Consumer()
            c.setDaemon(True)
            c.start()
            threads.append(c)
        #in order to kill the process by ctrl+c
        for t in threads:
            while 1:
                if t.isAlive():
                    time.sleep(1)
                else:
                    break
        root_name=merge_pabot_report(out_dir_common,outs_dir_list,options_list_mm,datasources_list,pabot_args_list,_now())
        #_get_suite_root_name(convert_multi_list(suite_names_list))
        option_list_common=options_list_mm[0]
        option_list_common['outputdir']=out_dir_common
        sys.exit(_report_results(out_dir_common, pabot_args_list[0], option_list_common, _now(),_get_suite_root_name(suite_names_entire)))

def convert_multi_list(list):
    list_one=[]
    for i in range(0,len(list)):
        for j in range(0,len(list[i])):
            list_one.append(list[i][j])
    return list_one

def generate_pabot_suiteXml(outs_dir_list,options_list,datasources_list,pabot_args_list):
    outs_dir_common=get_common_out_dir(outs_dir_list,len(outs_dir_list))
    ##implement tempory
    options_common=options_list[0]
    pabot_args_common=pabot_args_list[0]
    datasources_test=[get_common_dir(datasources_list,len(datasources_list))]
    suite_names = solve_suite_names(outs_dir_common, datasources_test, options_common,pabot_args_common)
    return outs_dir_common,suite_names

def get_common_out_dir(dir_list,dir_length):
    min_outdir_length=len(dir_list[0].strip('/').split('/'))
    min_out_dir_index=0
    paths_dir_name=[[]]*dir_length
    for i in range(0,dir_length):
        paths_dir_name[i]=dir_list[i].strip('/').split('/')
        if(min_outdir_length>len(dir_list[i].strip('/').split('/'))):
            min_outdir_length=len(dir_list[i].strip('/').split('/'))
            min_out_dir_index=i
    pathnames=dir_list[min_out_dir_index].strip('/').split('/')
    common_out_dir="/"
    flag=True
    for j in range(0,len(pathnames)):
        for i in range(0,dir_length):
            if(pathnames[j]!="".join(paths_dir_name[i][j])):
                flag=False
                break
        if(flag==True):
            common_out_dir=common_out_dir+pathnames[j]+"/"
    common_out_dir=common_out_dir+"suitename"
    if(os.path.exists(common_out_dir+"suitename")):
        os.mkdir(common_out_dir)
    return common_out_dir

def get_common_dir(dir_list,dir_length):
    min_outdir_length=len(dir_list[0].strip('/').split('/'))
    min_out_dir_index=0
    paths_dir_name=[[]]*dir_length
    for i in range(0,dir_length):
        paths_dir_name[i]=dir_list[i].strip('/').split('/')
        if(min_outdir_length>len(dir_list[i].strip('/').split('/'))):
            min_outdir_length=len(dir_list[i].strip('/').split('/'))
            min_out_dir_index=i
    pathnames=dir_list[min_out_dir_index].strip('/').split('/')
    common_out_dir="/"
    flag=True
    for j in range(0,len(pathnames)):
        for i in range(0,dir_length):
            if(pathnames[j]!="".join(paths_dir_name[i][j])):
                flag=False
                break
        if(flag==True):
            common_out_dir=common_out_dir+pathnames[j]+"/"
    return common_out_dir


def merge_pabot_report(out_dir_common,outs_dir_list,options_list,datasources_list,pabot_args_list,start_time_string):
    pabot_path_entire=out_dir_common+'/pabot_results'
    if (os.path.exists(pabot_path_entire)):
        shutil.rmtree(pabot_path_entire)
    os.mkdir(pabot_path_entire)
    for i in range(0,len(outs_dir_list)):
        cmd="cp -r "+outs_dir_list[i]+"/*   "+pabot_path_entire
        os.system(cmd)
    cmd="mv "+out_dir_common+"/*.xml   "+pabot_path_entire
    os.system(cmd)
    return pabot_path_entire


# def _exitCheckfunc(threadName):
#     try:
#         while 1:
#             alive=False
#             if threadName.isAlive():
#                 alive=True
#             if not alive:
#                 break
#             time.sleep(1)
#     # KeyboardInterrupt :ctrl-c
#     except KeyboardInterrupt, e:
#         traceback.print_exc()



if __name__ == '__main__':
    main(sys.argv[1:])
    # pabot_cmd_list=pabot_cmd_parse(sys.argv[1:])
    # if(len(pabot_cmd_list)==1):
    #     main_original(sys.argv[1:])
    # else:
    #     #pabot multiplythread
    #     i=1
    #     pabot_index=0
    #     while(i<=len(pabot_cmd_list)):
    #         if(i<len(pabot_cmd_list)):
    #             datasources, options, outs_dir, pabot_args, suite_names, lib_process=generate_suite_xml(sys.argv[pabot_index+1:pabot_cmd_list[i]+1])
    #             merge_queue.put([datasources, options, outs_dir, pabot_args, suite_names, lib_process])
    #         else:
    #             datasources, options, outs_dir, pabot_args, suite_names, lib_process=generate_suite_xml(sys.argv[pabot_index+1:])
    #             merge_queue.put([datasources, options, outs_dir, pabot_args, suite_names, lib_process])
    #         if(i<len(pabot_cmd_list)):
    #             pabot_index=pabot_cmd_list[i]+1
    #         i = i + 1
    #     size = merge_queue.qsize()
    #     threads = []
    #     original_signal_handler = signal.signal(signal.SIGINT, keyboard_interrupt)
    #     for i in range(size):
    #         # time.sleep(1)
    #         c = Consumer()
    #         #c.setDaemon(True)
    #         c.start()
    #     # threads.append(c)
    #     # for t in threads:
    #     #     t._shutdown = _exitCheckfunc(t)
    #     signal.signal(signal.SIGINT, original_signal_handler)



