import subprocess
import os
import git

class GitClient:
    def __init__(self, gh_pat):
        """
        Logs in to GitHub using either the GITHUB_TOKEN environment variable or the gh CLI.
        """
        # Clone private repository using GITHUB_TOKEN

        if gh_pat is None:
            raise ValueError("No GitHub PAT token found. Please create a GitHub PAT and set the \
                             GITHUB_TOKEN environment variable.")

        self.pat_token = gh_pat

    def push_changes(self, repo_dir, commit_message):
        """
        Pushes changes to a GitHub repository.
        """
        if repo_dir is None:
            raise ValueError("repo_dir cannot be None")

        if commit_message is None:
            raise ValueError("commit_message cannot be None")

        try:
            repo = git.Repo(repo_dir)
            repo.git.add(".")
            repo.index.commit(commit_message)
            repo.git.push()
        except git.exc.GitCommandError as ex:
            print(f"Error pushing changes: Exception: {ex}")

    def __run_command(self, command):
        """
        Runs a command in the shell and returns its output.
        """
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, \
                                             universal_newlines=True, shell=True)
            return output.strip()
        except subprocess.CalledProcessError as ex:
            print(f"Error: {ex.output}")
            return None

    def __run_gh_cli_command(self, command, args):
        """
        Runs a command in the gh CLI and returns its output.
        """
        return self.__run_command(["gh", command] + args)

    def clone_repo(self, repo_name, target_branch, directory):
        """
        Clones a GitHub repository to a local directory.
        """
        if repo_name is None:
            raise ValueError("repo_name cannot be None")

        git_url = f"https://{self.pat_token}@github.com/{repo_name}"
        self.__run_gh_cli_command("auth", ["setup-git"])

        try:
            git.Repo.clone_from(git_url, directory, branch=target_branch, \
                                env={"GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN")})
        except git.exc.GitCommandError as ex:
            print(f"Error cloning repo {repo_name}: Exception: {ex}")
