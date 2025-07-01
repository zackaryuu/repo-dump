import pytest
import os
from zuu.APP.github import (
    download_raw_content,
    last_commit,
    extract_commit,
    download_gist,
)
pytest.skip(reason="GitHub API rate limit exceeded", allow_module_level=True)

class TestGitHubFunctions:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        # Setup
        self.test_repo = "octocat/Hello-World"
        self.test_file = "README"
        self.test_non_primary_branch = "test"
        self.test_non_primary_file = "CONTRIBUTING.md"  
        self.test_gist_id = "a28f59969e978f82f37cb3e8eba479a4"  # Example gist

        # Teardown
        yield
        if os.path.exists("test_download.md"):
            os.remove("test_download.md")

    
    def test_download_github_raw_content(self):
        content = download_raw_content(
            f"{self.test_repo}/master/{self.test_file}"
        )
        assert content.startswith(b"Hello World!")
    
    def test_download_github_raw_content_non_primary_branch(self):
        content = download_raw_content(
            f"{self.test_repo}/{self.test_non_primary_branch}/{self.test_non_primary_file}"
        )
        assert content.startswith(b"## Contributing")

    def test_last_commit(self):
        commit = last_commit(self.test_repo, self.test_file)
        assert commit is not None
        assert "sha" in commit

    def test_extract_commit(self):
        commit = last_commit(self.test_repo, self.test_file)
        sha = extract_commit(commit, "sha")
        assert sha is not None and len(sha) == 40  # SHA-1 is 40 characters long

    def test_download_gist(self):
        content = download_gist(
            self.test_gist_id, file_name="teams-fix.ps1"
        )
        assert content is not None
        assert b"$Host.UI.RawUI.WindowTitle" in content.getvalue()
