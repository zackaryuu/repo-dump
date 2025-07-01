from zuu.UTILS import preserve_cwd
import os


@preserve_cwd
def create_empty_branch(path: str, name: str, switch_back: bool = False):
    """
    Create a new empty Git branch and push it to the remote repository.

    Args:
        path (str): The local path to the Git repository.
        name (str): The name of the new branch to create.
        switch_back (bool, optional): If True, switch back to the previous branch after creating the new branch. Defaults to False.

    Raises:
        subprocess.CalledProcessError: If any of the Git commands fail.
    """
    os.chdir(path)
    os.system(f"git checkout --orphan {name}")
    os.system("git rm -rf .")
    os.system('git commit --allow-empty -m "Initial commit for empty branch"')
    os.system(f"git push origin {name}")
    if switch_back:
        os.system("git checkout -")


@preserve_cwd
def update_repo(path: str, url: str = None, branch: str = None):
    """
    Update a Git repository by either cloning it from a URL or pulling the latest changes.

    Args:
        path (str): The local path to the Git repository.
        url (str, optional): The URL of the Git repository to clone. Required if the repository does not already exist at the specified path.
        branch (str, optional): The name of the branch to checkout after cloning or pulling.

    Raises:
        subprocess.CalledProcessError: If any of the Git commands fail.
    """
    os.makedirs(path, exist_ok=True)
    os.chdir(path)
    if not os.path.exists(os.path.join(path, ".git")):
        assert url
        os.system(f"git clone {url} .")
        if branch:
            os.system(f"git checkout {branch}")
    else:
        os.system("git pull")
        if branch:
            os.system(f"git checkout {branch}")
