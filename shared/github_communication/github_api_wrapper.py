import requests
from github import Auth, Github


class GithubAPIWrapper:
    def __init__(self, api_token: str, repository_name: str) -> None:
        # personal access token
        self.api_token = api_token
        # format: "user_name/repository_name"
        self.repo_name = repository_name
        self.repository = self.initialize_repository()

    def initialize_repository(self):
        """
        Initialize Github repository.

        Returns:
            Github repository.
        """
        auth = Auth.Token(self.api_token)
        return Github(auth=auth).get_repo(self.repo_name)

    def get_file_paths(self, branch_name: str) -> list[str]:
        """
        Get all file names and contents from repository.
        The path to the file is relative to the repository root.

        Args:
            branch_name: Name of the branch.

        Returns:
            List of file paths.
        """

        files = []
        contents = self.repository.get_contents("", ref=branch_name)

        for file_content in contents:
            # if file is a directory, get the contents of this directory and add them to the list
            if file_content.type == "dir":
                contents.extend(
                    self.repository.get_contents(file_content.path, ref=branch_name)
                )
            else:
                files += [file_content.path]
        return files

    def get_file_content(self, file_path: str, branch_name: str) -> str:
        """
        Get file content from repository.

        Args:
            file_path: Path to file.
            branch_name: Name of the branch.

        Returns:
            File content.
        """

        if file_path not in self.get_file_paths(branch_name):
            raise FileNotFoundError(
                f"File {file_path} not found in repository. Please check the file path."
            )
        file = self.repository.get_contents(file_path, ref=branch_name)
        content = file.decoded_content.decode("utf-8")
        return content

    def create_file(
        self, file_path: str, file_content: str, commit_message: str, branch_name: str
    ) -> requests.Response:
        """
        Create file in repository.

        Args:
            file_path: Path to file.
            file_content: Content of file.
            commit_message: Commit message.
            branch_name: Name of the branch.
        """

        response = self.repository.create_file(
            file_path, commit_message, file_content, branch=branch_name
        )
        return response

    def update_file(
        self, file_path: str, file_content: str, commit_message: str, branch_name: str
    ) -> requests.Response:
        """
        Update file in repository.

        Args:
            file_path: Path to file.
            file_content: Content of file.
            commit_message: Commit message.
            branch_name: Name of the branch.
        """

        if file_path not in self.get_file_paths(branch_name):
            raise FileNotFoundError(
                f"File {file_path} not found in repository. Please check the file path."
            )

        file = self.repository.get_contents(file_path, ref=branch_name)
        response = self.repository.update_file(
            file_path, commit_message, file_content, file.sha, branch=branch_name
        )
        return response

    def delete_file(
        self, file_path: str, commit_message: str, branch_name: str
    ) -> requests.Response:
        """
        Delete file in repository.

        Args:
            file_path: Path to file.
            commit_message: Commit message.
            branch_name: Name of the branch.
        """

        if file_path not in self.get_file_paths(branch_name):
            raise FileNotFoundError(
                f"File {file_path} not found in repository. Please check the file path."
            )

        file = self.repository.get_contents(file_path, ref=branch_name)
        response = self.repository.delete_file(
            file_path, commit_message, file.sha, branch=branch_name
        )
        return response

    def get_branches(self) -> list[str]:
        """
        Get all branches from repository.

        Returns:
            List of branches.
        """

        branches = self.repository.get_branches()
        branches = [branch.name for branch in branches]
        return branches

    def create_branch(
        self, branch_name: str, from_branch: str = "main"
    ) -> requests.Response:
        """
        Create branch in repository.

        Args:
            branch_name: Name of branch.
            from_branch: Name of branch to branch from. Default is "main".
        """

        brances = self.get_branches()
        for branch in brances:
            if branch.name == branch_name:
                raise ValueError(
                    f"Branch {branch_name} already exists. Please choose another branch name."
                )

        response = self.repository.create_git_ref(
            ref=f"refs/heads/{branch_name}",
            sha=self.repository.get_branch(from_branch).commit.sha,
        )
        return response

    def delete_branch(self, branch_name: str) -> requests.Response:
        """
        Delete branch in repository.

        Args:
            branch_name: Name of branch.
        """

        if branch_name not in [branch.name for branch in self.get_branches()]:
            raise ValueError(
                f"Branch {branch_name} does not exist. Please choose another branch name."
            )

        response = self.repository.get_git_ref(f"heads/{branch_name}").delete()
        return response

    def get_pull_requests(self, state: str = "open") -> list[requests.Response]:
        """
        Get all pull requests from repository.

        Args:
            state: State of pull requests. Default is "open".

        Returns:
            List of numbers of pull requests.
        """
        pull_requests = self.repository.get_pulls(state=state)
        pull_requests_numbers = [pull_request.number for pull_request in pull_requests]
        return pull_requests_numbers

    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False,
    ) -> requests.Response:
        """
        Create pull request in repository.

        Args:
            title: Title of pull request.
            body: Body of pull request.
            head: Name of branch to merge from.
            base: Name of branch to merge to. Default is "main".
            draft: Whether pull request is a draft. Default is False.
        """

        if head not in [branch.name for branch in self.get_branches()]:
            raise ValueError(
                f"Branch {head} does not exist. Please choose another branch name."
            )

        response = self.repository.create_pull(
            title=title, body=body, head=head, base=base, draft=draft
        )
        return response

    def get_pull_request(self, pull_request_number: int) -> requests.Response:
        """
        Get pull request from repository.

        Args:
            pull_request_number: Number of pull request.

        Returns:
            Pull request.
        """

        pull_request = self.repository.get_pull(pull_request_number)
        return pull_request

    def update_pull_request(
        self, pull_request_number: int, title: str, body: str
    ) -> requests.Response:
        """
        Update pull request in repository.

        Args:
            pull_request_number: Number of pull request.
            title: Title of pull request.
            body: Body of pull request.
        """

        pull_request = self.get_pull_request(pull_request_number)
        response = pull_request.edit(title=title, body=body)
        return response

    def merge_pull_request(self, pull_request_number: int) -> requests.Response:
        """
        Merge pull request in repository.

        Args:
            pull_request_number: Number of pull request.
        """

        pull_request = self.get_pull_request(pull_request_number)

        # check if pull request can be merged
        if pull_request.mergeable_state != "clean":
            raise ValueError(
                f"Pull request {pull_request_number} cannot be merged. Please check the pull request."
            )

        response = pull_request.merge()
        return response

    def comment_on_pull_request(self, pull_request_number: int, comment: str) -> None:
        """
        Comment on pull request in repository.

        Args:
            pull_request_number: Number of pull request.
            comment: Comment.
        """

        pull_request = self.get_pull_request(pull_request_number)
        response = pull_request.create_issue_comment(comment)

        return response

    def close_pull_request(self, pull_request_number: int) -> requests.Response:
        """
        Close pull request in repository.

        Args:
            pull_request_number: Number of pull request.
        """

        pull_request = self.get_pull_request(pull_request_number)
        response = pull_request.edit(state="closed")
        return response

    def get_issues(self, state: str = "open") -> list[requests.Response]:
        """
        Get all issues from repository.

        Args:
            state: State of issues. Default is "open".

        Returns:
            List of issues.
        """

        issues = self.repository.get_issues(state=state)
        issues_numbers = [issue.number for issue in issues]
        return issues_numbers

    def create_issue(
        self,
        title: str,
        body: str,
    ) -> requests.Response:
        """
        Create issue in repository.

        Args:
            title: Title of issue.
            body: Body of issue.
            assignee: Name of assignee. Default is None.
            milestone: Number of milestone. Default is None.
            labels: List of labels. Default is None.
        """

        response = self.repository.create_issue(
            title=title,
            body=body,
        )
        return response

    def get_issue(self, issue_number: int) -> requests.Response:
        """
        Get issue from repository.

        Args:
            issue_number: Number of issue.

        Returns:
            Issue.
        """

        issue = self.repository.get_issue(issue_number)
        return issue

    def update_issue(self, issue_number: int, title: str, body: str) -> None:
        """
        Update issue in repository.

        Args:
            issue_number: Number of issue.
            title: Title of issue.
            body: Body of issue.
        """

        issue = self.get_issue(issue_number)
        issue.edit(title=title, body=body)

    def close_issue(self, issue_number: int) -> None:
        """
        Close issue in repository.

        Args:
            issue_number: Number of issue.
        """

        issue = self.get_issue(issue_number)
        issue.edit(state="closed")

    def comment_on_issue(self, issue_number: int, comment: str) -> requests.Response:
        """
        Comment on issue in repository.

        Args:
            issue_number: Number of issue.
            comment: Comment.
        """

        issue = self.get_issue(issue_number)
        response = issue.create_comment(comment)
        return response
