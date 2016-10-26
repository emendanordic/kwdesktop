# **************************************************************************************************
#  Emenda Nordic AB.
#
# Disclaimer: Please note that this software or software component is released by Emenda Nordic AB
# on a non-proprietary basis for commercial or non-commercial use with no warranty. Emenda Nordic AB
# will not be liable for any damage or loss caused by the use of this software. Redistribution is
# only allowed with prior consent.
#
# **************************************************************************************************

from kwlpmetrics import KwLocalProjectMetrics

import os, shutil, sys, time
from subprocess import call, Popen, PIPE

class Kwcheck:

    def __init__(self, logger, path, build_spec, url, project_dir, settings_dir,
        license_host, license_port, run, silent,  issue_report,
        report_query, metrics_report, metrics_ref, clean, verbose):

        self.REPORT_FORMAT_TYPE = {'csv':'scriptable','txt':'short','xml':'xml',
            'html':'html'}
        # options for kwcheck commands
        self.kwcheck_create_options = []
        self.kwcheck_import_options = []
        self.kwcheck_run_options = []
        self.kwcheck_list_options = []

        self.logger = logger
        self.path = path
        self.build_spec = build_spec
        self.url = url
        self.project_dir = project_dir
        self.settings_dir = settings_dir
        self.license_host = license_host
        self.license_port = license_port
        self.run = run
        self.silent = silent
        self.issue_report = issue_report
        self.report_query = report_query
        self.metrics_report = metrics_report
        self.metrics_ref = metrics_ref
        self.clean = clean
        self.verbose = verbose

        if self.path:
            self.kwcheck_exe = os.path.join(self.path, 'kwcheck')
            self.kwgcheck_exe = os.path.join(self.path, 'kwgcheck')
        else:
            self.kwcheck_exe = 'kwcheck'
            self.kwgcheck_exe = 'kwgcheck'

        if self.project_dir != None:
            self.add_kwcheck_option('--project-dir', self.project_dir, kwcheck_create=True, kwcheck_import=True, kwcheck_run=True, kwcheck_list=True)
        if self.settings_dir != None:
            self.add_kwcheck_option('--settings-dir', self.settings_dir, kwcheck_create=True)
        if self.url != None:
            self.add_kwcheck_option('--url', self.url, kwcheck_create=True)
        if self.license_host != None:
            self.add_kwcheck_option('--license-host', self.license_host, kwcheck_create=True, kwcheck_run=True, kwcheck_list=True)
        if self.license_port != None:
            self.add_kwcheck_option('--license-port', self.license_port, kwcheck_create=True, kwcheck_run=True, kwcheck_list=True)
        if self.build_spec:
            self.add_kwcheck_option('--build-spec', self.build_spec, kwcheck_create=True, kwcheck_run=True)


    def add_kwcheck_option(self, flag, opt, kwcheck_create=False, kwcheck_import=False, kwcheck_run=False, kwcheck_list=False):
        if kwcheck_create:
            self.kwcheck_create_options.extend((flag, opt))
        if kwcheck_import:
            self.kwcheck_import_options.extend((flag, opt))
        if kwcheck_run:
            self.kwcheck_run_options.extend((flag, opt))
        if kwcheck_list:
            self.kwcheck_list_options.extend((flag, opt))

    def run_analysis(self):
        self.logger.info('Starting kwcheck analysis stage')
        ret_code = 0
        if self.run:
            self.logger.info('Running kwcheck analysis')
            # perform analysis
            ret_code = self.execute_cmd(self.create_kwcheck_run_cmd())
        else:
            self.logger.info('Skipping kwcheck analysis')
        return ret_code

    def generate_report(self):
        self.logger.info('Starting report generation stage')
        ret_code = 0
        if self.issue_report:
            filename, file_extension = os.path.splitext(self.issue_report)
            if not file_extension:
                sys.exit('No file extension recognised for --issue-report "{}"'.format(self.issue_report))
            report_format = self.REPORT_FORMAT_TYPE[file_extension[1:]]
            # check file extension without "." so take all chars after 1st
            if not report_format:
                sys.exit('File extension "{}" not recognised for --issue-report'.format(file_extension))
            # TODO
            if report_format == 'html':
                sys.exit('Sorry! Report format html not supported... yet...')
            self.kwcheck_list_options.extend(('--report', self.issue_report))
            self.kwcheck_list_options.extend(('-F', report_format))
            # add report query options to the list command used to retrieve a list of Klocwork issues
            if self.report_query:
                # TODO : dont just split in case user provides argument with quotes
                self.kwcheck_list_options.extend((self.report_query.strip().split()))
            # generate report
            ret_code = self.execute_cmd(self.create_kwcheck_list_cmd())

        if self.metrics_report:
            kwlpmetrics = KwLocalProjectMetrics(self.logger, self.project_dir,
                self.metrics_report, self.metrics_ref)
            try:
                kwlpmetrics.generate_report()
            except SystemExit as e:
                sys.exit(e)

        return ret_code

    def open_gui(self):
        ret_code = 0
        if not self.silent:
            # TODO 3.x now "input"
            open_kwgcheck = raw_input('Would you like to start Klocwork Desktop? [Y/N] ')
            if 'Y' == open_kwgcheck.strip().upper():
                self.logger.info('Opening Klocwork Desktop GUI (kwgcheck)')
                # TODO : if path to project is not default, CD there
                ret_code = Popen([self.kwgcheck_exe])
            else:
                self.logger.info('Skipping Klocwork Desktop GUI (kwgcheck)')
        else:
            self.logger.info('Silent mode enabled. Skipping Klocwork Desktop GUI prompt')
        return ret_code

    def create_kwcheck_create_cmd(self):
        return [self.kwcheck_exe, 'create'] + self.kwcheck_create_options

    def create_kwcheck_import_cmd(self):
        return [self.kwcheck_exe, 'import'] + self.kwcheck_import_options + [self.build_spec]

    def create_kwcheck_run_cmd(self):
        return [self.kwcheck_exe, 'run'] + self.kwcheck_run_options

    def create_kwcheck_list_cmd(self):
        return [self.kwcheck_exe, 'list'] + self.kwcheck_list_options

    def create_project(self):
        ret_code = 0
        if self.has_existing_project():
            # TODO: support to update settings, e.g. url, project etc
            # then import build spec
            ret_code = self.import_build_spec()
        else:
            # create project
            ret_code = self.create_local_project()
        # TODO handle exception or return code
        self.logger.info('kwcheck called - error code = {0}'.format(ret_code))
        # TODO check project created properly
        return ret_code

    def import_build_spec(self):
        return self.execute_cmd(self.create_kwcheck_import_cmd())

    def create_local_project(self):
        return self.execute_cmd(self.create_kwcheck_create_cmd())

    def validate(self):
        self.logger.info('Starting validation stage')
        self.logger.info('Validating kwcheck executable...')
        if not self.hasExecutable():
            sys.exit('Cannot find kwcheck executable "{0}"'.format(self.kwcheck_exe))
        self.logger.info('Validating build specficiation exists...')
        if not os.path.exists(self.build_spec):
            sys.exit('Build spec does not exist')
        self.logger.info('Validating build specficiation contents...')
        self.validate_build_spec()
        self.logger.info('Validating local Klocwork project...')
        self.validate_local_project()
        self.logger.info('Validation stage completed successfully')

    def validate_build_spec(self):
        # TODO: validate build_spec
        if False:
            sys.exit('Build spec is not valid')
        return 0

    def validate_local_project(self):
        self.logger.info('Checking local Klocwork project exists...')
        if not self.has_existing_project():
            self.logger.info('Existing local Klocwork project not found. Cleaning up old files if necessary.')
            self.cleanup_klocwork_project()
        elif self.clean:
            self.logger.info('Existing local Klocwork project found but "--clean" flag provided so cleaning anyway')
            self.cleanup_klocwork_project()
        else:
            self.logger.info('Local Klocwork project exists')

    def cleanup_klocwork_project(self):
        if os.path.exists(self.project_dir):
            self.logger.info('Cleaning up {0}'.format(self.project_dir))
            shutil.rmtree(self.project_dir)
        if os.path.exists(self.settings_dir):
            self.logger.info('Cleaning up {0}'.format(self.settings_dir))
            shutil.rmtree(self.settings_dir)

    def has_existing_project(self):
        if os.path.exists(self.project_dir) and os.path.exists(self.settings_dir):
            return True
        return False

    # check if executable kwcheck exists
    def hasExecutable(self):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(self.kwcheck_exe)
        if fpath:
            if is_exe(self.kwcheck_exe):
                return True
        else:
            for path in os.environ['PATH'].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, self.kwcheck_exe)
                if is_exe(exe_file):
                    return True
        return False

    def execute_cmd(self, cmd):
        self.logger.info('Executing command: \'{0}\''.format(' '.join(cmd)))
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)

        if self.verbose:
            self.logger.debug('Print output from command:')
            while True:
                output = proc.stdout.readline()
                if output == '' and proc.poll() is not None:
                    break
                if output:
                    print output.strip()
            self.logger.debug('Command finished')
        else:
            while proc.poll() == None:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
            print('')

        if proc.returncode != 0:
            self.logger.warning('Non-zero return code. Return code {}'.format(proc.returncode))
            print(proc.stderr.read())
            sys.exit('Exiting due to non-zero return code.')
        return proc.returncode
