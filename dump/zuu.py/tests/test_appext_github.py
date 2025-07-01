import pytest
import os
from zuu.appext_github import GithubRepo, GithubGist, GithubRepoFileContext
from datetime import datetime
import time


class TestGitHubIntegration:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        # Setup test values
        self.test_repo_url = "https://github.com/octocat/Hello-World/blob/master/README"
        self.test_raw_url = "https://raw.githubusercontent.com/octocat/Hello-World/master/README"
        self.test_branch_url = "https://github.com/octocat/Hello-World/blob/test/CONTRIBUTING.md"
        self.test_gist_id = "a28f59969e978f82f37cb3e8eba479a4"
        self.eagle_repo = "zw-eagle-plugins/eagle-link"
        
        # Teardown cleanup
        yield
        for f in ["test_download.md", "downloaded_asset"]:
            if os.path.exists(f):
                if os.path.isdir(f):
                    for root, dirs, files in os.walk(f, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(f)
                else:
                    os.remove(f)

    def test_download_raw_content(self):
        # Test with URL string
        content = GithubRepo.downloadRaw(self.test_repo_url)
        assert content.startswith(b"Hello World!")
        
        # Test with context object
        ctx = GithubRepoFileContext.fromGithubBlobUrl(self.test_repo_url)
        content = GithubRepo.downloadRaw(ctx)
        assert content.startswith(b"Hello World!")

    def test_download_raw_non_primary_branch(self):
        content = GithubRepo.downloadRaw(self.test_branch_url)
        assert b"Contributing" in content

    def test_last_commit_info(self):
        commit = GithubRepo.lastCommit(self.test_repo_url)
        assert isinstance(commit, dict)
        assert "sha" in commit
        assert "commit" in commit
        
        # Verify commit structure
        assert isinstance(commit["commit"]["committer"]["date"], str)
        assert datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

    def test_release_download(self):
        
        releases = GithubRepo.releases(self.eagle_repo, tag="v1.3.0")
        assert len(releases) == 1, "Should get exactly one release with specific tag"

        start_time = time.time()
        GithubRepo.releases(self.eagle_repo, tag="v1.3.0")
        assert time.time() - start_time < 0.1, "Should return cached response instantly"
        
        # Test download with tag specification
        result = GithubRepo.downloadRelease(
            self.eagle_repo,
            asset_names=["Linker-*.eagleplugin"],
            save_path="downloaded_asset",
            tag="v1.3.0"
        )
        assert result is None, "Should return None when saving to path"
        assert os.path.exists("downloaded_asset/Linker-1.3.0.eagleplugin"), "Specific asset should be downloaded"

        # Test latest release
        latest_release = GithubRepo.releases(self.eagle_repo)
        assert len(latest_release) > 0, "Should get at least one release"
        
        # Test latest download without tag
        result = GithubRepo.downloadRelease(
            self.eagle_repo,
            asset_names=["Linker-*.eagleplugin"],
            save_path="downloaded_asset"
        )
        assert os.path.exists("downloaded_asset/Linker-1.3.0.eagleplugin"), "Latest asset should be downloaded"

    def test_gist_download(self):
        # Test gist download with save path
        list(GithubGist.file(
            self.test_gist_id,
            files=["teams-fix.ps1"],
            save_path="test-downloaded-asset"
        ))
        assert os.path.exists("test-downloaded-asset/teams-fix.ps1")
        assert b"$Host.UI.RawUI.WindowTitle" in open("test-downloaded-asset/teams-fix.ps1", "rb").read()

        # Test in-memory gist download
        gen = GithubGist.file(self.test_gist_id, files=["*.ps1"])
        filename, content = next(gen)
        assert filename == "teams-fix.ps1"

    def test_invalid_url_handling(self):
        # Test invalid URL with none_on_error
        ctx = GithubRepoFileContext.auto("https://invalid.url", none_on_error=True)
        assert ctx is None
        
        # Test invalid URL without none_on_error
        with pytest.raises(ValueError):
            GithubRepoFileContext.auto("https://invalid.url") 