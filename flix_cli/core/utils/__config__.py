import getpass
import os
import platform as plt


def get_temp() -> str:
    username = getpass.getuser()
    temp_dir = ""
    if plt.system() == "Windows":
        temp_dir = os.path.join("C:\\", "Users", username, "AppData", "Local", "Temp", "flix-cli")
    else:
        temp_dir = os.path.join("/tmp", "flix-cli")

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    return temp_dir


def get_config() -> tuple[str, str]:
    CONFIG_DIR = (
        os.path.join(os.path.expanduser("~"), ".config", "flix-cli")
        if plt.system() != "Windows"
        else os.path.join(os.getenv("APPDATA"), "flix-cli")
    )

    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    CONFIG_FILE = f"{CONFIG_DIR}/flix-cli.conf"

    config = {}
    player = ""
    downloads_dir = ""

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip().strip('"')

        player = config.get("player")
        downloads_dir = config.get("dl_dir")

    else:
        player = "mpv"
        downloads_dir = (
            f"C:/Users/{getpass.getuser()}/Downloads"
            if plt.system() == "Windows"
            else f"{os.path.expanduser('~')}/Downloads"
        )

    return player, downloads_dir
