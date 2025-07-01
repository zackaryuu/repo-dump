from functools import lru_cache
import os
import shutil
import yaml
import re
import subprocess

def is_program_installed(program):
    """
    Check if a program is installed by trying to call it.
    """

    # Use a null device to suppress the output of the program
    null_device = open(os.devnull, 'w')

    try:
        # Try to execute the program and get its version
        subprocess.run([program, '--version'], stdout=null_device, stderr=null_device)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False
    finally:
        null_device.close()


package_path = os.path.dirname(os.path.realpath(__file__))
cache_path = os.path.join(package_path, "cache")
presets_path = os.path.join(package_path, "presets")
shared_path = os.path.join(package_path, "shared")

def dump_yaml(path : str, data : dict):
    yaml_data = yaml.dump(data)
    with open(path, "w") as f:
        f.write("---\n")
        f.write(yaml_data)
        f.write("---\n")

@lru_cache()
def check_match(
    filename : str,
    pattern : str
):
    if re.match(pattern, filename):
        return True
    return False

def check_matches(
    filename : str,
    patterns : list
):
    if len(patterns) == 0:
        return True

    if filename in patterns:
        return True
    for pattern in patterns:
        if check_match(pattern, filename):
            return True
    return False

def extract_inbetween_p(
    string : str
):
    """
    extract all keys in between two %
    example:
    hello %a:1% %b% %c%
    will return {"a": 1, "b": None, "c": None}
    """
    pattern = r'%(\w+)%'
    matches = re.findall(pattern, string)
    # get all keys
    matches = list(set(matches))
    result= {}
    for match in matches:
        if ':' in match:
            key, value = match.split(':', 1)
            result[key] = value
        else:
            result[match] = None
    return result

def copy_file_wc(
    src : str,
    dst : str
):
    if os.path.exists(dst):
        raise Exception(f"{dst} already exists")

    shutil.copyfile(
        src,
        dst
    )