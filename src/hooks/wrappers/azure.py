import os
import subprocess

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.subscription import SubscriptionClient

AZD_ENVIRONMENT_NAME_RESOURCE_TAG = "azd-env-name"


class AzureClient:
    """
    A client for interacting with Azure services.

    This class provides methods for retrieving information about Azure resources, such as AKS
    clusters and GitHub PATs.
    """

    def __init__(self):
        self._credential = DefaultAzureCredential()

    def set_azd_env_variable(self, name, value, export=False):
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
            standard_out = subprocess.check_output(["azd", "env", "set", name, value], universal_newlines=True)
            print(standard_out)

            if export:
                os.environ[name] = value

        except subprocess.CalledProcessError as ex:
            print(f" Error: {ex.output}")

    def get_active_subscription_id(self):
        """
        Returns the subscription ID of the active subscription.

        :return: The subscription ID of the active subscription, or None if an error occurred.
        """
        try:
            sub_client = SubscriptionClient(self._credential)
            subscription = next(sub_client.subscriptions.list())
            return subscription.subscription_id
        except (HttpResponseError, ClientAuthenticationError) as exc:
            print(f"Error occurred while getting subscription ID: {exc}")
            return None

    def _parse_resource_group_from_id(self, resource_id):
        """
        Returns the resource group name from the specified resource ID.

        Args:
            resource_id (str): The ID of the Azure resource.

        Returns:
            str: The name of the resource group that contains the resource.
        """
        return resource_id.split("/")[4]

    def get_container_service_client(self, subscription_id):
        """
        Returns a ContainerServiceClient object for the specified subscription ID.

        Args:
            subscription_id (str): The ID of the Azure subscription.

        Returns:
            ContainerServiceClient: A client object for managing Azure Kubernetes
            Service (AKS) clusters. Returns None if an error occurs while
            creating the client object.
        """
        try:
            return ContainerServiceClient(self._credential, subscription_id)
        except (HttpResponseError, ClientAuthenticationError) as exc:
            print(f"Error occurred while creating ContainerServiceClient: {exc}")
            return None

    def get_container_registry(self, subscription_id, resource_group_name):
        """
        Returns a list of container registries in the specified resource group.

        Args:
            subscription_id (str): The ID of the Azure subscription.
            resource_group_name (str): The name of the resource group.

        Returns:
            List of ContainerRegistry objects, or None if an error occurred.
        """
        try:
            container_registry_client = ContainerRegistryManagementClient(self._credential, subscription_id)
            registries = container_registry_client.registries.list_by_resource_group(resource_group_name)

            reduced_registries = [
                registry
                for registry in registries
                if AZD_ENVIRONMENT_NAME_RESOURCE_TAG in registry.tags
                and registry.tags.get(AZD_ENVIRONMENT_NAME_RESOURCE_TAG)
            ]

            if len(reduced_registries) == 0:
                return None

            return reduced_registries[0]
        except (HttpResponseError, ClientAuthenticationError) as exc:
            print(f"Error occurred while getting container registries: {exc}")
            return None

    def get_aks_clusters(self, subscription_id):
        """
        Returns a list of AKS clusters that have the 'azd-env-name' tag set.

        Args:
            subscription_id (str): The ID of the Azure subscription to use.

        Returns:
            List of AKS clusters that have the 'azd-env-name' tag set, or None if an error occurred.
        """
        try:
            container_service_client = self.get_container_service_client(subscription_id)
            aks_clusters = container_service_client.managed_clusters.list()
            return [
                cluster
                for cluster in aks_clusters
                if AZD_ENVIRONMENT_NAME_RESOURCE_TAG in cluster.tags
                and cluster.tags.get(AZD_ENVIRONMENT_NAME_RESOURCE_TAG)
            ]
        except (HttpResponseError, ClientAuthenticationError) as exc:
            print(f"Error occurred while getting AKS clusters: {exc}")
            return None

    def get_keyvault(self, azd_env_name, subscription_id, resource_group_name):
        """
        Returns the Software Factory KeyVault within the specified resource group.

        Args:
            azd_env_name (str): The name of the AZD environment.
            subscription_id (str): The ID of the Azure subscription.
            resource_group_name (str): The name of the resource group.

        Returns:
            A KeyVault object, or None if an error occurred.
        """
        try:
            kv_client = KeyVaultManagementClient(self._credential, subscription_id)
            reduced_keyvaults = [
                keyvault
                for keyvault in kv_client.vaults.list()
                if self._parse_resource_group_from_id(keyvault.id) == resource_group_name
                and AZD_ENVIRONMENT_NAME_RESOURCE_TAG in keyvault.tags
                and keyvault.tags.get(AZD_ENVIRONMENT_NAME_RESOURCE_TAG) == azd_env_name
            ]

            if len(reduced_keyvaults) == 0:
                raise ValueError(f"No KeyVaults found for environment: {azd_env_name}")

            return kv_client.vaults.get(resource_group_name, reduced_keyvaults[0].name)
        except (HttpResponseError, ClientAuthenticationError, ValueError) as exc:
            print(f"Error occurred while getting KeyVaults: {exc}")
            return None

    def get_keyvault_secret(self, keyvault, secret_name):
        """
        Retrieves the specified secret from the specified Azure Key Vault.

        Args:
            keyvault (KeyVault): The KeyVault object representing the Azure Key
            Vault to retrieve the secret from.
            secret_name (str): The name of the secret to retrieve.

        Returns:
            str: The value of the specified secret, or None if an error occurred.
        """
        try:
            if keyvault is None:
                raise ValueError("KeyVault is None")

            # Get the secret from the keyvault
            secret_client = SecretClient(vault_url=keyvault.properties.vault_uri, credential=self._credential)
            if secret_client is None:
                raise ValueError("SecretClient is None")

            # Get the secret value
            secret = secret_client.get_secret(secret_name)

            # Return the secret value
            return secret.value
        except (HttpResponseError, ClientAuthenticationError, ValueError, ResourceNotFoundError) as exc:
            print(f"Error occurred while getting the KeyVault secret {secret_name}: {exc}")
            return None
