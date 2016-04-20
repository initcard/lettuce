import ConfigParser
import os
import sys
import time
import getpass

# Configuration File Setup


class Configuration:

    def __init__(self):
        self.Config = ConfigParser.ConfigParser()
        self.operatingSystem = ""

        # calls the config file that is located in the same directory as the module

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.Config.read(os.path.join(__location__, 'lettuceConfig.ini'))

        # OS Switch

        if sys.platform == "linux" or sys.platform == "linux2":
            # linux
            self.operatingSystem = "linux"

        elif sys.platform == "darwin":
            # OS X
            self.operatingSystem = "osx"

        elif sys.platform == "win32":
            # Windows...
            self.operatingSystem = "windows"

        else:
            raise OSError('Unsupported Operating System')

        self.server = self._server_connect()
        self.project = self._project_set()

    # From the python wiki: https://wiki.python.org/moin/ConfigParserExamples
    # returns a dict representing the sections given

    def _config_by_section(self, section):
        config_dict = {}
        options = self.Config.options(section)
        for option in options:
            try:
                config_dict[option] = self.Config.get(section, option)
                if config_dict[option] == -1:
                    print("skip: {}".format(option))
            except KeyError:
                print("exception on {}!".format(option))
                config_dict[option] = None
        return config_dict

    def _server_connect(self):
        if self.operatingSystem == "windows":
            if self._config_by_section(self.operatingSystem)['unc'] == "1":
                server = self._config_by_section(self.operatingSystem)['server']
            else:
                server = self._config_by_section(self.operatingSystem)['server']
        else:
            server = self._config_by_section(self.operatingSystem)['server']

        return os.path.normpath(server)

    def _project_set(self):
        # sets the project

        # Local Disk based project
        if self._config_by_section("paths")['local'] == "1":
            project = self._config_by_section("paths")['project']

        # Server Based Project
        else:
            unresolved_project = sanitize_path_list((self._config_by_section("paths")['project']).split('/'))

            project = self.server

            for l in unresolved_project:
                project = os.path.join(project, l)

        return os.path.normpath(project)

    # ---------------------------------------------------
    #                       Getters
    # ---------------------------------------------------

    def get_project(self):
        return self.project

    def get_server(self):
        return self.server

    def get_xml_file(self):
        xml_file_list = (self._config_by_section("paths"))['xmlfile'].split('/')

        xml_file_path = self.project

        for l in xml_file_list:
            xml_file_path = os.path.join(xml_file_path, l)
        return xml_file_path

    def get_version(self):
        return (self._config_by_section("general"))['version']

    def get_log_file(self):
        log_folder_list = ((self._config_by_section("paths"))['log']).split('/')
        log_name = "lettuce_{0}-{1}-{2}.log".format(self.get_version(),
                                                    getpass.getuser(),
                                                    time.strftime("%y%m%d-%H.%M.%S")
                                                    )

        log_folder_path = self.project

        for l in log_folder_list:
            log_folder_path = os.path.join(log_folder_path, l)

        return os.path.join(log_folder_path, log_name)



    def get_log_level(self):
        return "logging.{}".format(self._config_by_section("logging_root")["level"])


def sanitize_path_list(path_list):
    new_path_list = []
    for l in path_list:
        if l:
            new_path_list.append(l)
    return new_path_list
