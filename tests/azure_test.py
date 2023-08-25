from unittest.mock import MagicMock
import pytest
from src.hooks.wrappers.azure import AzureClient

@pytest.fixture
def azure_client():
    return AzureClient()

def test_get_container_service_client(azure_client):
    # Mock the ContainerServiceClient object
    container_service_client_mock = MagicMock()
    azure_client.get_container_service_client = MagicMock(\
        return_value=container_service_client_mock)

    # Test that the method returns the mocked object
    assert azure_client.get_container_service_client("subscription_id") == \
        container_service_client_mock


def test_get_aks_clusters(azure_client):
    # Mock the ContainerServiceClient object and its managed_clusters.list() method
    container_service_client_mock = MagicMock()
    container_service_client_mock.managed_clusters.list.return_value = [
        MagicMock(tags={"azd-env-name": "test_env"}),
        MagicMock(tags={}),
        MagicMock(tags={"azd-env-name": "another_env"}),
    ]
    azure_client.get_container_service_client = MagicMock(return_value=\
                                                          container_service_client_mock)

    # Test that the method returns only the AKS clusters with the "azd-env-name" tag
    assert len(azure_client.get_aks_clusters("subscription_id")) == 2

@pytest.mark.integtest
def test_get_gitops_repo_pat_token(azure_client):
    subscription_id = azure_client.get_active_subscription_id()
    clusters = azure_client.get_aks_clusters(subscription_id)

    assert len(clusters) > 0

    target_cluster = clusters[0]
    azd_env_name_tag_name = "azd-env-name"
    resource_group_name = target_cluster.id.split("/")[4]
    azd_env_name = target_cluster.tags.get(azd_env_name_tag_name)
    kv = azure_client.get_keyvault(
        azd_env_name, subscription_id, resource_group_name
    )
    client_secret = azure_client.get_keyvault_secret(kv, "githubToken")

    assert client_secret is not None
