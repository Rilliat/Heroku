"""Entry point. Checks for user and starts main script"""

# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# 🌐 https://github.com/hikariatama/Hikka
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🔑 https://www.gnu.org/licenses/agpl-3.0.html

import getpass
import os
import subprocess
import sys

from ._internal import restart

if (
    getpass.getuser() == "root"
    and "--root" not in " ".join(sys.argv)
    and all(trigger not in os.environ for trigger in {"DOCKER", "GOORM", "NO_SUDO"})
):
    print("🚫" * 15)
    print("You attempted to run Heroku on behalf of root user")
    print("Please, create a new user and restart script")
    print("If this action was intentional, pass --root argument instead")
    print("🚫" * 15)
    print()
    print("Type force_insecure to ignore this warning")
    print("Type no_sudo if your system has no sudo (Debian vibes)")
    inp = input('> ').lower()
    if inp != "force_insecure":
        sys.exit(1)
    elif inp == "no_sudo":
        os.environ["NO_SUDO"] = "1"
        print("Added NO_SUDO in your environment variables")
        restart()

if "--test-backend" in " ".join(sys.argv):
    print("⚠️" * 15)
    print("Your Heroku is running on TEST BACKEND")
    print("Do not report any bugs, as this mode is very unstable.")
    print("Thank you")
    print("⚠️" * 15)

def deps():
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "-q",
            "--disable-pip-version-check",
            "--no-warn-script-location",
            "-r",
            "requirements.txt",
        ],
        check=True,
    )


if sys.version_info < (3, 8, 0):
    print("🚫 Error: you must use at least Python version 3.8.0")
elif __package__ != "hikka":  # In case they did python __main__.py
    print("🚫 Error: you cannot run this as a script; you must execute as a package")
else:
    try:
        import herokutl
    except Exception:
        pass
    else:
        try:
            import herokutl  # noqa: F811

            if tuple(map(int, herokutl.__version__.split("."))) < (2, 0, 8):
                raise ImportError
        except ImportError:
            print("🔄 Installing dependencies...")
            deps()
            restart()

    try:
        from . import log

        log.init()

        from . import main
    except ImportError as e:
        print(f"{str(e)}\n🔄 Attempting dependencies installation... Just wait ⏱")
        deps()
        restart()

    if "HIKKA_DO_NOT_RESTART" in os.environ:
        del os.environ["HIKKA_DO_NOT_RESTART"]

    if "HIKKA_DO_NOT_RESTART2" in os.environ:
        del os.environ["HIKKA_DO_NOT_RESTART2"]

    main.hikka.main()  # Execute main function
