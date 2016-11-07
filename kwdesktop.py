# MIT License
#
# Copyright (c) 2016 Emenda Nordic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from kwcheck import Kwcheck

import argparse, csv, logging, os, shutil, sys
from subprocess import call, PIPE, Popen

parser = argparse.ArgumentParser(description='Klocwork Desktop Analysis Script.')
parser.add_argument('--path', required=False,
    help='Path to Klocwork desktop installation, e.g. C:\\Klocwork\\Desktop\\X.Y\\bin')
parser.add_argument('--build-spec', required=False, default='kwinject.out')
parser.add_argument('--url', required=False,
    help='URL to the Klocwork server and project, e.g. http://klocworkserver:8080/myproject')
parser.add_argument('--project-dir', required=False, default='.kwlp',
    help='Location of the .kwlp directory. Default is in the current directory, i.e. \'.kwlp\'')
parser.add_argument('--settings-dir', required=False, default='.kwps',
    help='Location of the .kwps directory. Default is in the current directory, i.e. \'.kwps\'')
parser.add_argument('--license-host', required=False,
    help='Host name for the FlexLM license server')
parser.add_argument('--license-port', required=False,
    help='Port for the FlexLM license server')
parser.add_argument('--silent', required=False, dest='silent', action='store_true',
    help='Do not prompt user about opening Klocwork GUI (kwgcheck)')
parser.add_argument('--run', required=False, dest='run', action='store_true',
    help='Also trigger the Klocwork analysis')
parser.add_argument('--issue-report', required=False,
    help='Specify a report file for detected Klocwork issues. The format is \
    automatically detected from the extension. E.g. "--issue-report REPORT.html" \
    will generate an HTML report')
parser.add_argument('--report-query', required=False,
    help='Provide extra arguments to be passed to kwcheck when generating a \
    report using \'kwcheck list\'. E.g. --report-query \'--system --status \
    Analyze,Ignore\' will also show system issues with statuses Analyze and Ignore')
parser.add_argument('--metrics-report', required=False,
    help='Specify a report file for software metrics detected by Klocwork. \
    Requires a list of Klocwork metrics which can be provided using the \
    --metrics-ref argument')
parser.add_argument('--metrics-ref', required=False,
    help='Specify a list of metrics to report')
parser.add_argument('--clean', required=False, dest='clean', action='store_true',
    help='Clean the existing Klocwork project (if it exists)')
parser.add_argument('--verbose', required=False, dest='verbose',
    action='store_true', help='Provide verbose output')

def print_title(text):
    print os.linesep
    print('-------------------------------------------------------------------------------')
    print('--- {0}'.format(text))
    print('-------------------------------------------------------------------------------')
    print os.linesep

def print_stage(text):
    print ('')
    print ('--- {0}'.format(text))
    print ('')

def main():
    print_title('Klocwork Desktop Utility')
    args = parser.parse_args()
    logLevel = logging.INFO
    if args.verbose:
        logLevel = logging.DEBUG
    logging.basicConfig(level=logLevel,
        format='%(levelname)s:%(asctime)s %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S')
    logger = logging.getLogger('kwdesktop')

    # create kwcheck object to handle for local Klocwork project
    kwcheck = Kwcheck(logger, args.path, args.build_spec, args.url,
        args.project_dir, args.settings_dir,
        args.license_host, args.license_port, args.run, args.silent,
        args.issue_report, args.report_query,
        args.metrics_report, args.metrics_ref,
        args.clean, args.verbose)

    try:
        print_stage('Validation Stage')
        kwcheck.validate()
        print_stage('Create Local Project')
        kwcheck.create_project()
        print_stage('Run Analysis')
        kwcheck.run_analysis()
        print_stage('Report Generation')
        kwcheck.generate_report()
        print_stage('Open Klocwork Desktop GUI')
        kwcheck.open_gui()
    except SystemExit as e:
        logger.error(e)
        sys.exit(1)
    except OSError as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
