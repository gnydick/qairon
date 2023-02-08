from qairon.qcli import CLIController


def _main_():
    qcli = CLIController()
    qcli.list('deployment')


if __name__ == '__main__':
    _main_()
