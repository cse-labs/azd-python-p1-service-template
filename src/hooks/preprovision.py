import os
import subprocess
from pick import pick
from wrappers.azure import AzureClient, AZD_ENVIRONMENT_NAME_RESOURCE_TAG
from wrappers.github import GithubClient

def prompt_user_for_target_clusters(clusters):
    """
    Prompts the user to select a cluster from a list of clusters.

    Args:
        clusters (List[ManagedCluster]): A list of AKS clusters.

    Returns:
        ManagedCluster: The selected cluster.
    """
    title = "Select a Big Bang cluster for your deployment environment"

    options = [f"Environment: {cluster.tags[AZD_ENVIRONMENT_NAME_RESOURCE_TAG]} \
        Cluster: {cluster.name}" for cluster in clusters]

    _, index = pick(options, title)

    return clusters[index - 1]

def set_azd_env_variable(name, value, export=False):
    """
    Sets an Azure Developer CLI environment variable with the given name and value.

    Args:
        name (str): The name of the environment variable to set.
        value (str): The value to set for the environment variable.

    Returns:
        None
    """
    print(f"Setting {name} environment variable...")
    try:
        standard_out = subprocess.check_output(["azd", "env", "set", name, value],\
            universal_newlines=True)
        print(standard_out)

        if export:
            os.environ[name] = value

    except subprocess.CalledProcessError as ex:
        print(f" Error: {ex.output}")

if __name__ == "__main__":
    print("Pre-provisioning hook running...")

    # verify that the .azure folder exists
    azure_dir = os.path.join(os.getcwd(), ".azure")
    if not os.path.exists(azure_dir):
        raise ValueError("The .azure folder does not exist. Please run 'azd init' \
                         to setup your environment.")

    print("Getting active subscription ID...")
    client = AzureClient()
    subscription_id = client.get_active_subscription_id()

    if subscription_id is None:
        raise ValueError\
            ("No active subscription found. Please run 'az login' to log in to Azure.")

    print(f"Active subscription ID: {subscription_id}")
    print("Getting AKS clusters...")
    clusters = client.get_aks_clusters(subscription_id)

    # Check if any clusters were found
    if len(clusters) == 0:
        raise ValueError(f"No AKS clusters found. Please create an AKS cluster and set the \
        {AZD_ENVIRONMENT_NAME_RESOURCE_TAG} tag.")

    target_cluster = prompt_user_for_target_clusters(clusters)
    resource_group_name = target_cluster.id.split("/")[4]
    github_pat_token = client.get_gitops_repo_pat_token(\
        target_cluster.tags[AZD_ENVIRONMENT_NAME_RESOURCE_TAG], \
        subscription_id, resource_group_name)

    registry = client.get_container_registry(subscription_id, resource_group_name)

    if registry is None:
        raise ValueError("No container registry found. Please create a container registry \
        and set the azd-container-registry-name tag.")

    if github_pat_token is not None:
        set_azd_env_variable("GITHUB_TOKEN", github_pat_token, True)

    set_azd_env_variable("AZURE_AKS_CLUSTER_NAME", target_cluster.name)
    set_azd_env_variable("AZURE_RESOURCE_GROUP", resource_group_name)
    set_azd_env_variable("AZURE_CONTAINER_REGISTRY_ENDPOINT", registry.login_server)
    set_azd_env_variable("GITOPS_REPO_RELEASE_BRANCH", \
        target_cluster.tags["gitops-release-branch"], True)
    set_azd_env_variable("GITOPS_REPO", target_cluster.tags["gitops-repo"], True)

    print("Pre-provisioning hook complete.")
