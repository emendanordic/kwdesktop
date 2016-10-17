
# This script sets up a local Klocwork project using the command line tools.
# To use, make sure you have captured your build command with Klocwork's kwinject command
# to generate a valid build specification. The build specification is required to use this
# script

from kwcheck import Kwcheck

import argparse, csv, logging, os, shutil
from subprocess import call, PIPE, Popen

parser = argparse.ArgumentParser(description='Klocwork Desktop Analysis Script.')
parser.add_argument('--path', required=False, help='Path to Klocwork desktop installation, e.g. C:\\Klocwork\\Desktop\\X.Y\\bin')
parser.add_argument('--build-spec', required=False, default='kwinject.out')
parser.add_argument('--url', required=False, help='URL to the Klocwork server and project, e.g. http://klocworkserver:8080/myproject')
parser.add_argument('--project-dir', required=False, default='.', help='Location of the local Klocwork project. Default is the current directory, i.e. \'.\'')
parser.add_argument('--license-host', required=False)
parser.add_argument('--license-port', required=False)
parser.add_argument('--silent', dest='silent', action='store_true', help='Do not prompt user about opening Klocwork GUI (kwgcheck)')
parser.add_argument('--run', dest='run', action='store_true', help='Also trigger the Klocwork analysis')
parser.add_argument('--report-file', required=False, help='Specify a report file. Requires --report-format')
parser.add_argument('--report-format', required=False, help='Specify a report format. Requires --report-file')
parser.add_argument('--report-query', required=False, help='Provide extra arguments to be passed to kwcheck when generating a report using \'kwcheck list\'. E.g. --report-query \'--system --status Analyze,Ignore\' will also show system issues with statuses Analyze and Ignore')

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
    # TODO check logger settings
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('kwdesktop')

    args = parser.parse_args()

    # create kwcheck object to handle for local Klocwork project
    kwcheck = Kwcheck(logger, args.path, args.build_spec, args.url, args.project_dir,
        args.license_host, args.license_port, args.run, args.report_file,
        args.report_format, args.report_query)

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
    except OSError as e:
        logger.error(e)


if __name__ == "__main__":
    main()
