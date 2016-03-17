import ConfigParser
import os
import sys


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

    # Getters

    def get_xml_file(self):
        return (self._config_by_section("paths"))['xmlfile']

    def get_version(self):
        return (self._config_by_section("general"))['version']


class Logger:

    def __init__ (self, config):
        return " "
