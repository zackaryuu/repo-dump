from dataclasses import dataclass
from functools import cache, cached_property
import subprocess
import json
import os


class Scoop:

    @staticmethod
    def pkgIsInstalled(pkg: str):
        return any(pkg == pkg_info.name for pkg_info in Scoop.list())

    @staticmethod
    def pkgInstall(pkg: str, version: str = None):
        cmd = f"scoop install {pkg}"
        if version:
            cmd += f"@{version}"
        subprocess.run(cmd, shell=True, check=True)

    @staticmethod
    def list():
        result = subprocess.run(
            ["scoop", "list"], capture_output=True, text=True, check=True, shell=True
        )
        has_started = False 
        for line in result.stdout.splitlines():
            if "----" in line:
                has_started = True
                continue
            elif not has_started:
                continue
            if not line:
                continue
            name, version, bucket, date, time, *args = line.split()
            yield ScoopPkg(
                name=name,
                version=version,
                bucket=bucket,
                date=date,
                time=time,
                is_global=len(args) > 0,
            )

    @staticmethod
    def bucketList():
        result = subprocess.run(
            ["scoop", "bucket", "list"],
            capture_output=True,
            text=True,
            check=True,
            shell=True,
        )
        return result.stdout.splitlines()

    @staticmethod
    def bucketAdd(bucket: str, url: str = None):
        subprocess.run("scoop update", shell=True, check=True)
        subprocess.run("scoop install git", shell=True, check=True)
        if url:
            subprocess.run(f"scoop bucket add {bucket} {url}", shell=True, check=True)
        else:
            subprocess.run(f"scoop bucket add {bucket}", shell=True, check=True)


class ScoopSelf:
    @staticmethod
    def isInstalled():
        try:
            result = subprocess.run(
                ["scoop", "which", "scoop"],
                capture_output=True,
                text=True,
                check=True,
                shell=True,
            )
            return "scoop" in result.stdout
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    @cache
    def path():
        result = subprocess.run(
            ["scoop", "which", "scoop"],
            capture_output=True,
            text=True,
            check=True,
            shell=True,
        )
        raw = result.stdout.strip()
        return os.path.expanduser(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(raw))))
        )


Scoop.self = ScoopSelf


@dataclass
class ScoopPkg:
    name: str
    version: str
    bucket: str
    date: str
    time: str
    is_global: bool

    def reinstall(self):
        """Reinstall the Scoop package"""
        cmd = ["scoop", "reinstall", self.name]
        if self.is_global:
            cmd.append("--global")
        subprocess.run(cmd, shell=True, check=True)

    def update(self):
        """Update the Scoop package"""
        cmd = ["scoop", "update", self.name]
        if self.is_global:
            cmd.append("--global")
        subprocess.run(cmd, shell=True, check=True)

    def uninstall(self):
        """Uninstall the Scoop package"""
        cmd = ["scoop", "uninstall", self.name]
        if self.is_global:
            cmd.append("--global")
        subprocess.run(cmd, shell=True, check=True)

    def cat(self):
        result = subprocess.run(
            ["scoop", "cat", self.name],
            capture_output=True,
            text=True,
            check=True,
            shell=True,
        )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None

    @cached_property
    def manifestData(self):
        return self.cat()

    @property
    def manifestPath(self):
        return os.path.join(
            ScoopSelf.path(), "buckets", self.bucket, "bucket", f"{self.name}.json"
        )

    @cached_property
    def path(self):
        path = os.path.join(ScoopSelf.path(), self.name, "current")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Application path not found: {path}")
        return path

    def _clearCache(self):
        self.__dict__.pop("manifestData", None)
        self.__dict__.pop("path", None)

