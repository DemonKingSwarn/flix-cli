import subprocess

CATT_EXECUTABLE = "catt"


def cast(file, subs):
    url = file

    device = input("enter the IPv4 of your TV: ")

    args = [CATT_EXECUTABLE, "-d", device, "cast", "-s", subs[0], url]

    catt_process = subprocess.Popen(args)
    catt_process.wait()

    # subprocess.call(f"{CATT_EXECUTABLE} cast -s \"{subs[0]}\" \"{url}\"", shell=True)
