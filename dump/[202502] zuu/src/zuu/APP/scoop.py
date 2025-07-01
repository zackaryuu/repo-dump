from functools import cache
import subprocess
import json
import os


def is_installed():
    """
    Checks if the Scoop package manager is installed on the system.

    Returns:
        bool: True if Scoop is installed, False otherwise.
    """
    try:
        # Attempt to run 'scoop' with the 'which' command to check its path
        result = subprocess.run(
            ["scoop", "which", "scoop"],
            capture_output=True,
            text=True,
            check=True,
            shell=True,
        )

        # Check if the result contains the path to the scoop executable
        if "scoop" in result.stdout:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        # If there's an error (scoop not found), return False
        return False


def list():
    """
    Retrieves a list of installed Scoop packages on the system.

    Returns:
        Generator[dict]: A generator that yields a dictionary for each installed Scoop package, containing the following keys:
            - "name": The name of the Scoop package.
            - "version": The version of the Scoop package.
            - "bucket": The Scoop bucket the package is from.
            - "date": The date the package was installed.
            - "time": The time the package was installed.
            - "is_global": A boolean indicating whether the package is installed globally or not.
    """
    raw = subprocess.run(
        ["scoop", "list"], capture_output=True, text=True, check=True, shell=True
    ).stdout.splitlines()
    has_started = False
    for line in raw:
        if "----" in line:
            has_started = True
            continue
        elif not has_started:
            continue
        if not line:
            continue
        name, version, bucket, date, time, *args = line.split()
        yield {
            "name": name,
            "version": version,
            "bucket": bucket,
            "date": date,
            "time": time,
            "is_global": len(args) > 0,
        }


def get_installed_manifest(name: str) -> dict | None:
    raw = subprocess.run(
        ["scoop", "cat", name], capture_output=True, text=True, check=True, shell=True
    )
    try:
        res = json.loads(raw.stdout)
        assert isinstance(res, dict)
        return res
    except json.JSONDecodeError:
        return None


@cache
def get_path() -> str:
    result = subprocess.run(
        ["scoop", "which", "scoop"],
        capture_output=True,
        text=True,
        check=True,
        shell=True,
    )
    raw = result.stdout
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(raw))))
    return os.path.expanduser(path)


@cache
def get_app_path(name: str):
    manifest = get_installed_manifest(name)
    assert manifest

    path = os.path.join(get_path(), name, "current")

    assert os.path.exists(path)

    return path


def add_bucket(name: str):
    os.system("scoop update")
    os.system("scoop install git")
    if not name.startswith("https://"):
        os.system(f"scoop bucket add {name}")
    else:
        url = name
        # the last path bit
        name = name.split("/")[-1]
        os.system(f"scoop bucket add {name} {url}")
