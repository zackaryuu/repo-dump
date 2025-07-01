import logging
import os

from zuu.etc import preserve_cwd

class GitRepo:
    def __init__(self, path : str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Repository not found at {path}")
        
        if not os.path.isdir(path):
            raise NotADirectoryError(f"{path} is not a directory")
        
        if not os.path.exists(os.path.join(path, ".git")):
            raise NotADirectoryError(f"{path} is not a git repository")
        
        self.path = path

    def __str__(self):
        return f"GitRepo({self.path})"

    @preserve_cwd
    def createEmptyBranch(self, branch_name : str, switchBack : bool = False):
        """
        Create a new empty Git branch and push it to the remote repository.

        Args:
            branch_name (str): The name of the new branch to create.
            switchBack (bool, optional): If True, switch back to the previous branch after creating the new branch. Defaults to False.

        Raises:
            subprocess.CalledProcessError: If any of the Git commands fail.
        """
        os.chdir(self.path)
        os.system(f"git checkout --orphan {branch_name}")
        os.system("git rm -rf .")
        os.system('git commit --allow-empty -m "Initial commit for empty branch"')
        os.system(f"git push origin {branch_name}")
        if switchBack:
            os.system("git checkout -")

    @preserve_cwd
    def pull(self):
        os.chdir(self.path)
        os.system("git pull")

    @classmethod
    @preserve_cwd
    def create(cls, path : str, remote : str = None):
        try:
            return cls(path)
        except Exception as e:
            logging.warning(f"Failed to create git repository at {path}: {e}")
            os.makedirs(path)
            os.chdir(path)
            if remote:
                os.system(f"git clone {remote} .")
            else:
                os.system("git init")
            return cls(path)

    @classmethod
    def toLatest(cls, path : str, remote : str):
        repo = cls.create(path, remote)
        repo.pull()
        return repo
    
    