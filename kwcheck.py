
import os, shutil, sys
from subprocess import call

class Kwcheck:

    def __init__(self, logger, path, build_spec, url, project_dir, license_host, license_port, run, report_file, report_format, report_query):
        self.kwcheck_options = []
        self.logger = logger
        self.path = path
        self.build_spec = build_spec
        self.url = url
        self.project_dir = project_dir
        self.license_host = license_host
        self.license_port = license_port
        self.run = run
        self.report_file = report_file
        self.report_format = report_format
        self.report_query = report_query

        if self.path:
            self.kwcheck_exe = os.path.join(self.path, "kwcheck")
            self.kwgcheck_exe = os.path.join(self.path, "kwgcheck")
        else:
            self.kwcheck_exe = "kwcheck"
            self.kwgcheck_exe = "kwgcheck"

        self.add_kwcheck_option("--build-spec", self.build_spec)
        if self.license_port != None:
            self.add_kwcheck_option("--license-host", self.license_host)
        if self.license_port != None:
            self.add_kwcheck_option("--license-port", self.license_port)
        if self.url != None:
            self.add_kwcheck_option("--url", self.url)


        self.kwlp = os.path.join(self.project_dir, ".kwlp")
        self.kwps = os.path.join(self.project_dir, ".kwps")

    def add_kwcheck_option(self, flag, opt):
        self.kwcheck_options.extend((flag, '"{0}"'.format(opt)))

    def run_analysis(self):
        self.logger.info("Starting kwcheck analysis stage")
        ret_code = 0
        if self.run:
            self.logger.info("Running kwcheck analysis")
            # perform analysis
            ret_code = self.execute_cmd(self.create_kwcheck_run_cmd())
        else:
            self.logger.info("Skipping kwcheck analysis")
        # TODO : LOGGING!!
        return ret_code

    def generate_report(self):
        self.logger.info("Starting report generation stage")
        ret_code = 0
        if self.report_file and False:
            # generate report
            # TODO validate all options...
            ret_code = self.execute_cmd(self.create_kwcheck_list_cmd())
        # TODO : LOGGING!!
        return ret_code

    def open_gui(self):
        ret_code = 0
        if not self.silent:
            open_kwgcheck = input("Would you like to start Klocwork Desktop? [Y/N] ")
            if "Y" == open_kwgcheck.strip().upper():
                # TODO : if path to project is not default, CD there
                ret_code = Popen([kwgcheck_exe])
        return ret_code

    def create_kwcheck_create_cmd(self):
        return [self.kwcheck_exe, "create"] + self.kwcheck_options

    def create_kwcheck_import_cmd(self):
        return [self.kwcheck_exe, "import"] + self.kwcheck_options

    def create_kwcheck_run_cmd(self):
        return [self.kwcheck_exe, "run"] + self.kwcheck_options

    def create_kwcheck_list_cmd(self):
        return [self.kwcheck_exe, "list"] + self.kwcheck_options

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
        print "kwcheck called - error code = {0}".format(ret_code)
        # TODO check project created properly
        return ret_code

    def import_build_spec(self):
        return self.execute_cmd(self.create_kwcheck_import_cmd())

    def create_local_project(self):
        return self.execute_cmd(self.create_kwcheck_create_cmd())

    def validate(self):
        self.logger.info("Starting validation stage")
        self.logger.info("Validating kwcheck executable...")
        # if not self.hasExecutable():
            # sys.exit("Cannot find kwcheck executable in Klocwork installation.")
        self.logger.info("Validating build specficiation exists...")
        if not os.path.exists(self.build_spec):
            sys.exit("Build spec does not exist")
        self.logger.info("Validating build specficiation contents...")
        self.validate_build_spec()
        self.logger.info("Validating local Klocwork project...")
        self.validate_local_project()
        self.logger.info("Validation stage completed successfully")

    def validate_build_spec(self):
        # TODO: validate build_spec
        if False:
            sys.exit("Build spec is not valid")
        return 0

    def validate_local_project(self):
        self.logger.info("Checking local Klocwork project exists...")
        if not self.has_existing_project():
            self.logger.info("Existing local Klocwork project not found. Cleaning up old files if necessary.")
            if os.path.exists(self.kwlp):
                self.logger.info("Cleaning up {0}".format(self.kwlp))
                shutil.rmtree(self.kwlp)
            if os.path.exists(self.kwps):
                self.logger.info("Cleaning up {0}".format(self.kwps))
                shutil.rmtree(self.kwps)
        else:
            self.self.logger.info("Local Klocwork project exists")

    def has_existing_project(self):
        if os.path.exists(self.kwlp) and os.path.exists(self.kwps):
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
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, self.kwcheck_exe)
                if is_exe(exe_file):
                    return True
        return False

    def execute_cmd(self, cmd):
        print('Executing command: \'{0}\''.format(' '.join(cmd)))
        return call(cmd)
