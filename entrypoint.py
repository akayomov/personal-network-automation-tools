import os
import subprocess
from argparse import ArgumentParser


class EntryPoint:
    def __init__(self):
        unit = str(subprocess.run(['uname', '-n'], stdout=subprocess.PIPE).stdout, 'utf-8').rstrip()
        print("Running on node: " + unit)

        self.path = os.path.dirname(__file__)

        self.argp = ArgumentParser(description="Automation entry point")
        self.argp.add_argument('-p', '--pid', help="PID file path")
        self.argv = self.argp.parse_args()

        selector = {
            'nibiru': self.keenetic_router,
            'oakaiomov-devtool': self.keenetic_router,
        }

        selector.get(unit, self.unknown)()

    def keenetic_router(self):
        runner = self.path+"/routers/keenetic/runner.py"
        process = subprocess.Popen(['python3', runner], cwd=self.path, stdout=subprocess.PIPE)
        print("KeeneticRunner: service started with pid '"+str(process.pid)+"'")
        if self.argv.pid:
            open(self.argv.pid, 'w').write(str(process.pid))

    @staticmethod
    def unknown():
        print("Started on unknown node")


if __name__ == "__main__":
    EntryPoint()
