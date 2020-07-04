import subprocess

unit = str(subprocess.run(['uname', '-n'], stdout=subprocess.PIPE).stdout, 'utf-8').rstrip()

print("Running on node: "+unit)
