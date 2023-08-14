import subprocess
import os
import tempfile
import git

class GithubClient:
    def login(self):
        gh_pat = os.environ.get("GITHUB_TOKEN")

        if gh_pat is None:
            self.__run_gh_cli_command("auth", ["login"])
        else:
            self.__unset_gh_pat()
            self.__run_gh_cli_command("auth", ["logout"])
            self.__login_with_pat(gh_pat)

        self.__run_gh_cli_command("auth", ["setup-git"])
        self.__run_gh_cli_command("auth", ["status"])
        os.environ["GITHUB_TOKEN"] = gh_pat

    def __login_with_pat(self, gh_pat):
        with tempfile.TemporaryDirectory() as td_hndl:
            token_file = os.path.join(td_hndl, 'token')
            with open(token_file, 'w', encoding="utf-8") as file_hndl:
                file_hndl.write(gh_pat)
                file_hndl.close()
                self.__run_gh_cli_command("auth", ["login", f"--with-token < {token_file}"])

    def clone_repo(self, repo_name, target_branch, directory):
        if repo_name is None:
            raise ValueError("repo_name cannot be None")

        git_url = f"https://github.com/{repo_name}"

        try:
            git.Repo.clone_from(git_url, directory, branch=target_branch)
        except git.exc.GitCommandError as ex:
            print(f"Error cloning repo {repo_name}: Exception: {ex}")

    def push_changes(self, repo_dir, commit_message):
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
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, \
                                             universal_newlines=True, shell=True)
            return output.strip()
        except subprocess.CalledProcessError as ex:
            print(f"Error: {ex.output}")
            return None
            
    def __run_gh_cli_command(self, command, args):
        return self.__run_command(["gh", command] + args)

    def __unset_gh_pat(self):
        del os.environ["GITHUB_TOKEN"]