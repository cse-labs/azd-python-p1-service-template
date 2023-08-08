from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.subscription import SubscriptionClient
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError

# These APIs are simple wrappers over the Azure SDk for Python.
# They are used to simplify the code in the preprovision.py hook.

class AzureClient:
    def __init__(self):
        self._credential = DefaultAzureCredential()

    # Return the current subscription ID from credentials
    def get_active_subscription_id(self):
        try:
            sub_client = SubscriptionClient(self._credential) 
            subscription = next(sub_client.subscriptions.list())
            return subscription.subscription_id
        except (HttpResponseError, ClientAuthenticationError) as exc:
            print(f"Error occurred while getting subscription ID: {exc}")
            return None

    # Create a ContainerServiceClient object using the credential and subscription ID
    def get_container_service_client(self, subscription_id):
        try:
            return ContainerServiceClient(self._credential, subscription_id)
        except (HttpResponseError, ClientAuthenticationError) as exc:
            print(f"Error occurred while creating ContainerServiceClient: {exc}")
            return None

    # Get all AKS clusters in the subscription and filter out any that 
    # are missing the label "azd-env-name"
    # Return a list of AKS clusters
    def get_aks_clusters(self, subscription_id):
        try:
            container_service_client = self.get_container_service_client(subscription_id)
            aks_clusters = container_service_client.managed_clusters.list()
            return [cluster for cluster in aks_clusters if cluster.tags.get("azd-env-name")]
        except (HttpResponseError, ClientAuthenticationError) as exc:
            print(f"Error occurred while getting AKS clusters: {exc}")
            return None
