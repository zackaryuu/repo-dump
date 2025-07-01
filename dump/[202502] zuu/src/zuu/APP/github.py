import datetime
import os
import typing
import requests
import io
import re

DEFAULT_GITHUB_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}


def download_raw_content(
    url: str, save_path: str = None, headers: dict = None
) -> bytes:
    """
    Downloads the raw content from the given GitHub URL.

    Args:
        url (str): The URL of the content to be downloaded.
        save_path (str, optional): Path to save the content locally. Defaults to None.
        headers (dict, optional): Custom headers for the request. Defaults to None.

    Returns:
        bytes: The raw content downloaded from the specified URL.

    Raises:
        RuntimeError: If the file is not found on GitHub.
        requests.exceptions.RequestException: For any network-related errors.
    """
    headers = headers or DEFAULT_GITHUB_HEADERS
    full_url = f"https://raw.githubusercontent.com/{url}"

    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error downloading content: {e}")

    if save_path:
        with open(save_path, "wb") as file:
            file.write(response.content)
        return

    return response.content


def last_commit(
    repository_id: str, file_path: str, headers: dict = None
) -> typing.Optional[typing.Dict]:
    """
    Retrieves the last commit information for a specified repository and file.

    Args:
        repository_id (str): The repository identifier (e.g., 'user/repo').
        file_path (str): The file path in the repository.
        headers (dict, optional): Custom headers for the request. Defaults to None.

    Returns:
        dict: JSON data of the last commit, or None if an error occurs.

    Raises:
        requests.exceptions.RequestException: For any network-related errors.
    """
    headers = headers or DEFAULT_GITHUB_HEADERS
    api_url = f"https://api.github.com/repos/{repository_id}/commits?path={file_path}&per_page=1"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        commits = response.json()
        return commits[0] if commits else None
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving last commit: {e}")
        return None


def extract_commit(
    commit_data: dict, extract_type: str = "sha"
) -> typing.Optional[str]:
    """
    Extracts specific information (date or SHA) from commit JSON data.

    Args:
        commit_data (dict): JSON data of the commit.
        extract_type (str): Type of information to extract, either "date" or "sha".

    Returns:
        Optional[str]: A datetime string for the commit date or the commit SHA.
    """
    try:
        if extract_type == "date":
            date_str = commit_data["commit"]["committer"]["date"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            return date_obj
        elif extract_type == "sha":
            return commit_data["sha"]
    except (KeyError, TypeError) as e:
        print(f"Error extracting commit data: {e}")
        return None


def get_releases(
    repo: str, limit: int = 10, headers: dict = None
) -> typing.List[typing.Dict]:
    """
    Retrieves a list of releases for a given repository.

    Args:
        repo (str): The repository name (e.g., 'user/repo').
        limit (int, optional): Maximum number of releases to retrieve. Defaults to 10.
        headers (dict, optional): Custom headers for the request. Defaults to None.

    Returns:
        List[Dict]: A list of release metadata dictionaries.

    Raises:
        requests.exceptions.RequestException: For any network-related errors.
    """
    headers = headers or DEFAULT_GITHUB_HEADERS
    api_url = f"https://api.github.com/repos/{repo}/releases?per_page={limit}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving releases: {e}")
        return []


def release_meta(
    repo: str,
    name: str = None,
    match_type: str = "exact",
    match_release_tag: bool = False,
    headers: dict = None,
) -> typing.Optional[typing.Dict]:
    """
    Retrieves metadata about a GitHub release based on matching criteria.

    Args:
        repo (str): The GitHub repository name.
        name (str, optional): The name of the release tag. Defaults to None.
        match_type (str, optional): Matching criteria ("exact", "startswith", "contains", "endswith", "glob").
        match_release_tag (bool, optional): Whether to match the release tag. Defaults to False.
        headers (dict, optional): Custom headers for the request. Defaults to None.

    Returns:
        Optional[Dict]: The metadata of the matching GitHub release.

    Raises:
        ValueError: If no release matches the criteria.
        requests.exceptions.RequestException: For any network-related errors.
    """
    headers = headers or DEFAULT_GITHUB_HEADERS
    releases = get_releases(repo, headers=headers)

    if name and match_type == "exact":
        url = f"https://api.github.com/repos/{repo}/releases/tags/{name}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Release with tag '{name}' not found: {e}")

    try:
        for release in releases:
            match_var = release["tag_name"] if match_release_tag else release["name"]

            if (
                (match_type == "startswith" and match_var.startswith(name))
                or (match_type == "contains" and name in match_var)
                or (match_type == "endswith" and match_var.endswith(name))
                or (match_type == "glob" and re.match(name, match_var) is not None)
            ):
                return release

        raise ValueError(f"Could not find release with tag {name}")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving release metadata: {e}")
        return None

def download_release(
    release_data: dict,
    asset_names: typing.List[str] = None,  # Accept a list of asset names
    match_type: str = "exact",
    save_path: typing.Optional[str] = None,  # Path to save the downloaded assets
) -> typing.Optional[typing.List[io.BytesIO]]:
    """
    Downloads release assets from a GitHub release based on matching criteria.

    Args:
        release_data (dict): The JSON representation of the GitHub release.
        asset_names (List[str], optional): The names of the release assets to download. Defaults to None.
        match_type (str, optional): The matching criteria for the release asset ("exact", "startswith", "contains", "endswith", "glob").
        save_path (str, optional): The path to save the downloaded assets. If a folder is provided, assets will be saved there.

    Returns:
        Optional[List[io.BytesIO]]: If `save_path` is provided, returns None. Otherwise, returns a list of downloaded assets as BytesIO objects.

    Raises:
        requests.exceptions.HTTPError: If there is an error in the HTTP response.
    """
    downloaded_assets = []  # List to hold downloaded assets
    try:
        for asset in release_data.get("assets", []):
            for asset_name in asset_names or [None]:  # Iterate over asset names
                name_match = (
                    (match_type == "exact" and asset["name"] == asset_name)
                    or (match_type == "startswith" and asset["name"].startswith(asset_name))
                    or (match_type == "contains" and asset_name in asset["name"])
                    or (match_type == "endswith" and asset["name"].endswith(asset_name))
                    or (
                        match_type == "glob"
                        and re.match(asset_name, asset["name"]) is not None
                    )
                )

                if name_match:
                    download_url = asset["browser_download_url"]
                    response = requests.get(download_url, stream=True)
                    response.raise_for_status()

                    if save_path:
                        # Save the asset to the specified folder
                        file_path = os.path.join(save_path, asset["name"])
                        with open(file_path, "wb") as file:
                            for block in response.iter_content(1024):
                                file.write(block)
                        continue  # Skip adding to downloaded_assets if saved to disk

                    content = io.BytesIO()
                    for block in response.iter_content(1024):
                        content.write(block)

                    downloaded_assets.append(content)  # Add to the list of downloaded assets

        return downloaded_assets  # Return the list of downloaded assets
    except requests.exceptions.RequestException as e:
        print(f"Error downloading release asset: {e}")
        return None


def download_gist(
    gist_id: str,
    file_name: str = None,
    match_type: str = "exact",
    save_path: typing.Optional[str] = None,
    headers: dict = None,
) -> typing.Optional[typing.Union[io.BytesIO, None]]:
    """
    Download a file from a GitHub Gist.

    Args:
        gist_id (str): The ID of the GitHub Gist.
        file_name (str, optional): The name of the file to download from the Gist. Defaults to None.
        match_type (str, optional): The matching criteria for the file name ("exact", "startswith", "contains", "endswith", "glob").
        save_path (str, optional): The path to save the downloaded file. Defaults to None.
        headers (dict, optional): Additional headers to include in the request. Defaults to None.

    Returns:
        Optional[Union[io.BytesIO, None]]: If `save_path` is provided, returns None. Otherwise, returns the downloaded file as a BytesIO object.

    Raises:
        requests.exceptions.HTTPError: If there is an error in the HTTP response.
    """
    try:
        gist_url = f"https://api.github.com/gists/{gist_id}"
        response = requests.get(gist_url, headers=headers)
        response.raise_for_status()
        gist_data = response.json()

        for gist_file in gist_data["files"].values():
            name_match = (
                (match_type == "exact" and gist_file["filename"] == file_name)
                or (
                    match_type == "startswith"
                    and gist_file["filename"].startswith(file_name)
                )
                or (match_type == "contains" and file_name in gist_file["filename"])
                or (
                    match_type == "endswith"
                    and gist_file["filename"].endswith(file_name)
                )
                or (
                    match_type == "glob"
                    and re.match(file_name, gist_file["filename"]) is not None
                )
            )

            if name_match:
                download_url = gist_file["raw_url"]
                response = requests.get(download_url, headers=headers)
                response.raise_for_status()

                content = io.BytesIO(response.content)

                if save_path:
                    with open(save_path, "wb") as file:
                        file.write(content.getvalue())
                    return None

                return content

        print(f"No matching file found in the Gist with ID: {gist_id}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error downloading GitHub Gist: {e}")
        return None
