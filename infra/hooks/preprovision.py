from azure.identity import DefaultAzureCredential, SubscriptionClient
from azure.mgmt.containerservice import ContainerServiceClient


def get_subscription_id(credential: AzureCliCredential): 
    # Create a SubscriptionClient object using the credential
    subscription_client = SubscriptionClient(credential)

    # Get the current subscription ID
    subscription = next(subscription_client.subscriptions.list())

    return subscription.subscription_id


def login_to_azure():
    try:
        # Create an instance of the Azure CLI credential
        credential = AzureCliCredential()

        # Get the subscription ID
        subscription_id = get_subscription_id(credential)

        # Create a ResourceManagementClient object using the credential and subscription ID
        resource_client = ResourceManagementClient(credential, subscription_id)

        return resource_client
    except Exception as e:
        print(f"Error occurred while logging in to Azure: {e}")
        return None

if __name__ == "__main__":
    client = login_to_azure()

    if client is not None:
        print("client is valid")
    try:
        client = login_to_azure()
        


        if client is not None:
            print("client is valid")
        else:
            print("client is not valid")
    except AuthenticationFailedError as e:
        print(f"Error occurred while logging in to Azure: {e}")

        try:
            client = login_to_azure()
            def get_aks_resources(client):
                # Get all resource groups
                resource_groups = client.resource_groups.list()

                # Loop through each resource group
                for resource_group in resource_groups:
                    # Create a ContainerServiceClient object using the credential and subscription ID
                    container_service_client = ContainerServiceClient(client.credentials, resource_group.location)

                    # Get all AKS clusters in the resource group
                    aks_clusters = container_service_client.managed_clusters.list_by_resource_group(resource_group.name)

                    # Loop through each AKS cluster
                    for aks_cluster in aks_clusters:
                        # Check if the AKS cluster has a label named "azd-env-name"
                        if aks_cluster.tags is not None and "azd-env-name" in aks_cluster.tags:
                            # Do something with the AKS cluster
                            print(f"AKS cluster name: {aks_cluster.name}, Resource group: {resource_group.name}")

            if __name__ == "__main__":
                client = login_to_azure()

                if client is not None:
                    get_aks_resources(client)
            # END: 5f7d7c8fj9d3
            if client is not None:
                print("client is valid")
            else:
                print("client is not valid")
        except ClientAuthenticationError as e:
            print(f"Error occurred while logging in to Azure: {e}")

        try:
            client = login_to_azure()

            if client is not None:
                print("client is valid")
            else:
                print("client is not valid")
        except ClientAuthenticationError as e:
            print(f"Error occurred while logging in to Azure: {e}")
