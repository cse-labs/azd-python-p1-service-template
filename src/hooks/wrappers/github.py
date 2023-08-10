import subprocess
import os

class GithubClient:
    def login(self):
        gh_pat = os.environ.get('GITHUB_TOKEN')

        if gh_pat is None:
            self.unset_gh_pat()
            self.run_gh_cli_command("auth", "login")

        self.run_gh_cli_command("auth", "setup-git")
        self.run_gh_cli_command("auth", "status")

    def run_gh_cli_command(self, command, args):
        try:
            standard_out = subprocess.check_output(["gh", command, args],\
                universal_newlines=True)
            print(standard_out)
        except subprocess.CalledProcessError as ex:
            print(f" Error: {ex.output}")

    def unset_gh_pat(self):
        del os.environ['GITHUB_TOKEN']
