import os
import shutil
import subprocess
import tempfile

import yaml
from wrappers.azure import AzureClient
from wrappers.github import GitClient
from wrappers.renderer import RenderEngine

TEMPLATE_FILE = "azure.yaml"
CWD = os.path.abspath(os.path.join(os.getcwd(), os.pardir))


def set_env_from_azd():
    """
    Sets environment variables from the values returned by the 'azd env get-values' command.
    """
    env_string = subprocess.check_output(["azd", "env", "get-values", "--cwd", CWD], universal_newlines=True)

    for env_var in env_string.splitlines():
        env_var = env_var.replace("'", "").replace('"', "")
        key, value = env_var.split("=")
        os.environ[key] = value


def get_services_to_deploy(yaml_template) -> dict:
    """
    Parses the yaml file and returns a dictionary containing the services to deploy.
    """
    template_file = os.path.join(CWD, yaml_template)

    with open(template_file, encoding="utf-8") as stream:
        try:
            # Converts yaml document to python object
            yaml_dict = yaml.safe_load(stream)

            if "services" not in yaml_dict:
                raise ValueError(f"No services found in yaml file {template_file}.")

            return yaml_dict["services"]
        except yaml.YAMLError as ex:
            print("Error loading yaml file: ", ex)


def pre_req_assertions(deployment_template):
    """
    Asserts that the required environment variables and files exist.
    """
    azure_dir = os.path.join(CWD, ".azure")
    template_file = os.path.join(CWD, deployment_template)

    # verify that the .azure folder exists
    if not os.path.exists(azure_dir):
        raise ValueError(
            f"The .azure folder in {azure_dir} does not exist. Please run 'azd init' \
                         to setup your environment."
        )

    # verify that the yaml template file exists
    if not os.path.exists(template_file):
        raise ValueError("The template_dir folder does not exist. Please run 'azd init'")

    if os.environ.get("SERVICE_API_IMAGE_NAME") is None:
        raise ValueError(
            "No SERVICE_API_IMAGE_NAME environment variable found. Please set the \
        SERVICE_API_IMAGE_NAME environment variable."
        )

    os.environ["SERVICE_API_IMAGE_REPO"] = os.environ["SERVICE_API_IMAGE_NAME"].split(":")[0]
    os.environ["SERVICE_API_IMAGE_TAG"] = os.environ["SERVICE_API_IMAGE_NAME"].split(":")[1]


def set_gh_pat_token():
    """
    Gets the GitHub PAT token from the environment variables.
    """
    if os.environ.get("AZURE_AKS_ENVIRONMENT_NAME") is None:
        raise ValueError(
            "No AZURE_AKS_ENVIRONMENT_NAME environment variable found. Please set the \
                "
        )

    azure_client = AzureClient()
    bb_keyvault = azure_client.get_keyvault(
        os.environ.get("AZURE_AKS_ENVIRONMENT_NAME"),
        os.environ.get("AZURE_SUBSCRIPTION_ID"),
        os.environ.get("AZURE_RESOURCE_GROUP"),
    )

    if bb_keyvault is None:
        raise ValueError(
            "No key vaults found. Please create a key vault and set the \
        azd-keyvault-name tag."
        )

    pat_token = azure_client.get_keyvault_secret(bb_keyvault, "githubToken")
    if pat_token is not None:
        azure_client.set_azd_env_variable("GITHUB_TOKEN", pat_token, True)


def copy_manifest_dir_tree_to_repo(manifest_path, repo_path):
    """
    Recursively searches for files ending with a .tmpl extension under manifest_path
    and copies the directory tree to repo_path.
    """

    def ignore_func(_, files):
        return [f for f in files if f[-5:] != ".tmpl"]

    shutil.copytree(manifest_path, repo_path, ignore=ignore_func, dirs_exist_ok=True)


if __name__ == "__main__":
    print("Post-Deplouy hook running...")

    set_env_from_azd()
    pre_req_assertions(TEMPLATE_FILE)
    environment_name = os.environ.get("AZURE_AKS_ENVIRONMENT_NAME")
    print("Logging in to GitHub...")
    set_gh_pat_token()
    gh_pat = os.environ.get("GITHUB_TOKEN")
    git_client = GitClient(gh_pat)

    if os.environ.get("GITHUB_TOKEN") is None:
        raise ValueError(
            "No GitHub PAT token found. Please create a GitHub PAT and set the \
        GITHUB_TOKEN environment variable."
        )

    print("GitHub login successful.")
    git_repo = os.environ.get("GITOPS_REPO")
    release_branch = os.environ.get("GITOPS_REPO_RELEASE_BRANCH")

    with tempfile.TemporaryDirectory() as git_clone_dir:
        print("created temporary directory for git operations", git_clone_dir)
        print(f"Cloning {git_repo}...")
        git_client.clone_repo(git_repo, release_branch, git_clone_dir)
        print("Git clone successful.")

        services_to_deploy = get_services_to_deploy(TEMPLATE_FILE)

        for service in services_to_deploy:
            os.environ["SERVICE_NAME"] = service
            print(f"Deploying service: {service}")
            if "project" not in services_to_deploy[service]:
                raise ValueError(
                    f"Project directory path not found for service: {service}. \
                        Please add a project property to the service in the yaml file."
                )

            project_dir = services_to_deploy[service]["project"]
            manifest_dir = "manifests"

            if "k8s" in services_to_deploy[service] and "deploymentPath" in services_to_deploy[service]["k8s"]:
                manifest_dir = services_to_deploy[service]["k8s"]["deploymentPath"]

            manifest_path = os.path.join(CWD, project_dir, manifest_dir)
            gitops_environment_path = os.path.join(git_clone_dir, "environments", environment_name, "src", "manifests")
            service_render_path = os.path.join(gitops_environment_path, "services", service)
            copy_manifest_dir_tree_to_repo(manifest_path, service_render_path)
            render_client = RenderEngine(
                service_render_path, os.path.join(gitops_environment_path, "kustomization.yaml"), service
            )
            render_client.render()
            git_client.push_changes(git_clone_dir, f"Deployed service: {service}")
            print(f"Service {service} deployed successfully.")
