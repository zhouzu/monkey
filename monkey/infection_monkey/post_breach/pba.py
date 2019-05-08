import logging
import subprocess
import socket
from infection_monkey.control import ControlClient
from infection_monkey.utils import is_windows_os
from infection_monkey.config import WormConfiguration


LOG = logging.getLogger(__name__)

__author__ = 'VakarisZ'


class PBA(object):
    """
    Post breach action object. Can be extended to support more than command execution on target machine.
    """
    def __init__(self, name="unknown", command=""):
        """
        :param name: Name of post breach action.
        :param command: Command that will be executed on breached machine
        """
        self.command = command
        self.name = name

    @staticmethod
    def get_pba():
        """
        Should be overridden by all child classes.
        This method returns a PBA object based on worm's configuration.
        :return: An array of PBA objects.
        """
        raise NotImplementedError()

    @staticmethod
    def default_get_pba(name, pba_class, linux_cmd="", windows_cmd=""):
        if pba_class.__name__ in WormConfiguration.post_breach_actions:
            command = PBA.choose_command(linux_cmd, windows_cmd)
            if command:
                return PBA(name, command)

    def run(self):
        """
        Runs post breach action command
        """
        exec_funct = self._execute_default
        hostname = socket.gethostname()
        ControlClient.send_telemetry('post_breach', {'command': self.command,
                                                     'result': exec_funct(),
                                                     'name': self.name,
                                                     'hostname': hostname,
                                                     'ip': socket.gethostbyname(hostname)
                                                     })

    def _execute_default(self):
        """
        Default post breach command execution routine
        :param command: What command to execute
        :return: Tuple of command's output string and boolean, indicating if it succeeded
        """
        try:
            return subprocess.check_output(self.command, stderr=subprocess.STDOUT, shell=True), True
        except subprocess.CalledProcessError as e:
            # Return error output of the command
            return e.output, False

    @staticmethod
    def choose_command(linux_cmd, windows_cmd):
        return windows_cmd if is_windows_os() else linux_cmd
