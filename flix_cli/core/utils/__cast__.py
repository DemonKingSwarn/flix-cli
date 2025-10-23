import subprocess

CATT_EXECUTABLE = "catt"

def cast(file, subs):

    url = file

    subprocess.call(f"{CATT_EXECUTABLE} -s \"{subs}\" \"{url}\"", shell=True)
