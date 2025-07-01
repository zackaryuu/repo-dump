from dataclasses import dataclass
from functools import cache
import typing
import os
from urllib.parse import urlparse
import requests

from zuu.util_file import path_match


class Github:
    HEADERS = {"Accept": "application/vnd.github.v3+json"}


class GithubGist:
    @staticmethod
    @cache
    def apiGet(gist_id: str) -> dict:
        url = f"https://api.github.com/gists/{gist_id}"
        response = requests.get(url, headers=Github.HEADERS)
        return response.json()

    @staticmethod
    def file(
        gist_id: str, files: typing.List[str], save_path: str = None
    ) -> typing.Generator[typing.Tuple[str, bytes], None, None]:
        gist = GithubGist.apiGet(gist_id)
        filenames = list(gist.get("files", {}).keys())
        matches = path_match(filenames, files, depth=0)

        for match in matches:
            file_info = gist["files"][match]
            download_url = file_info["raw_url"]

            try:
                response = requests.get(download_url)
                response.raise_for_status()
                content = response.content

                if save_path is not None:
                    os.makedirs(save_path, exist_ok=True)
                    with open(os.path.join(save_path, match), "wb") as f:
                        f.write(content)

                yield match, content
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {match}: {e}")
                continue


@dataclass(frozen=True)
class GithubRepoFileContext:
    org: str
    repo: str
    path: str
    branch: str = None

    def __hash__(self):
        return hash((self.org, self.repo, self.path, self.branch))

    @classmethod
    @cache
    def fromGithubBlobUrl(cls, url: str) -> "GithubRepoFileContext":
        parsed = urlparse(url)
        if parsed.netloc != "github.com":
            raise ValueError("URL must be from github.com domain")

        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 4 or path_parts[2] != "blob":
            raise ValueError(
                "Invalid GitHub URL format. Expected: https://github.com/<org>/<repo>/blob/<branch>/<path>"
            )

        return cls(
            org=path_parts[0],
            repo=path_parts[1],
            branch=path_parts[3],
            path="/".join(path_parts[4:]),
        )

    @classmethod
    @cache
    def fromGithubRawUrl(cls, url: str) -> "GithubRepoFileContext":
        parsed = urlparse(url)
        if parsed.netloc != "raw.githubusercontent.com":
            raise ValueError("URL must be from raw.githubusercontent.com domain")

        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 3:
            raise ValueError(
                "Invalid GitHub raw URL format. Expected: https://raw.githubusercontent.com/<org>/<repo>/<branch>/<path>"
            )

        return cls(
            org=path_parts[0],
            repo=path_parts[1],
            branch=path_parts[2],
            path="/".join(path_parts[3:]) if len(path_parts) > 3 else "",
        )

    @classmethod
    def auto(
        cls, url: str, none_on_error: bool = False
    ) -> typing.Union["GithubRepoFileContext", None]:
        if url.startswith("https://github.com/"):
            return cls.fromGithubBlobUrl(url)
        elif url.startswith("https://raw.githubusercontent.com/"):
            return cls.fromGithubRawUrl(url)
        else:
            if none_on_error:
                return None
            raise ValueError("Invalid GitHub URL format.")


@dataclass
class GithubRepoContext:
    org: str
    repo: str
    branch: str = None


class GithubRepo:

    @cache
    @staticmethod
    def rawUrl(query: typing.Union[GithubRepoFileContext, str]) -> str:
        if isinstance(query, str):
            obj = GithubRepoFileContext.auto(query, none_on_error=True)
            if obj is None:
                return query

            url = f"https://raw.githubusercontent.com/{obj.org}/{obj.repo}"

            if obj.branch:
                url += f"/{obj.branch}"
            if obj.path:
                url += f"/{obj.path}"
            return url
        else:  # Handle GithubRepoFileContext case
            url = f"https://raw.githubusercontent.com/{query.org}/{query.repo}"
            if query.branch:
                url += f"/{query.branch}"
            if query.path:
                url += f"/{query.path}"
            return url

    @staticmethod
    def downloadRaw(
        query: typing.Union[GithubRepoFileContext, str], path: str = None
    ) -> str:
        url = GithubRepo.rawUrl(query)
        response = requests.get(url, headers=Github.HEADERS)
        if path is not None:
            with open(path, "wb") as f:
                f.write(response.content)
        return response.content

    @staticmethod
    @cache
    def lastCommit(
        query: typing.Union[GithubRepoFileContext, str],
    ) -> typing.Optional[typing.Dict]:
        if isinstance(query, str):
            query = GithubRepoFileContext.auto(query)

        api_url = f"https://api.github.com/repos/{query.org}/{query.repo}/commits"
        params = {"path": query.path, "per_page": 1}
        if query.branch:
            params["sha"] = query.branch

        try:
            response = requests.get(api_url, headers=Github.HEADERS, params=params)
            response.raise_for_status()
            commits = response.json()
            return commits[0] if commits else None
        except requests.exceptions.RequestException:
            return None

    @staticmethod
    @cache
    def releases(
        query: typing.Union[GithubRepoContext, str],
        tag: str = None,
        page_num: int = None,
    ) -> list[dict]:
        if isinstance(query, str):
            if "/" in query:
                org, repo = query.split("/", 1)
            else:
                raise ValueError("Invalid repository format, should be 'org/repo'")
        else:
            org, repo = query.org, query.repo

        api_url = f"https://api.github.com/repos/{org}/{repo}/releases"
        if tag:
            api_url += f"/tags/{tag}"
        else:
            if page_num is None:
                page_num = 1
            api_url += f"?page={page_num}"

        try:
            response = requests.get(api_url, headers=Github.HEADERS)
            response.raise_for_status()
            result = [response.json()] if tag else response.json()

            return result

        except requests.exceptions.RequestException:
            return []

    @staticmethod
    def downloadRelease(
        query: typing.Union[GithubRepoContext, str, dict],
        asset_names: typing.List[str],
        save_path: typing.Optional[str] = None,
        tag: str | None = None,
    ) -> typing.Optional[typing.List[bytes]]:
        if isinstance(query, dict):
            release = query
        else:
            if tag is None:
                tag = "latest"
            releases = GithubRepo.releases(query, tag=tag)
            if not releases:
                return None
            release = releases[0]

        downloaded = []
        assets = release.get("assets", [])
        filenames = [asset["name"] for asset in assets]
        matches = path_match(filenames, asset_names, depth=0)

        for match in matches:
            asset = next(a for a in assets if a["name"] == match)
            try:
                response = requests.get(
                    asset["browser_download_url"], headers=Github.HEADERS
                )
                response.raise_for_status()
                content = response.content

                if save_path:
                    os.makedirs(save_path, exist_ok=True)
                    with open(os.path.join(save_path, asset["name"]), "wb") as f:
                        f.write(content)
                else:
                    downloaded.append((asset["name"], content))
            except requests.exceptions.RequestException:
                continue

        return downloaded or None
