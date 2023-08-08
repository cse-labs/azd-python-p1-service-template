from infra.hooks.wrappers.azure import AzureClient

client = AzureClient()

def test_get_active_subscription_id():
    subscription_id = client.get_active_subscription_id()
    assert subscription_id is not None

def test_get_aks_clusters():
    # Replace with your own test values
    subscription_id = client.get_active_subscription_id()
        
    # Call the get_aks_clusters function
    clusters = client.get_aks_clusters(subscription_id)
        
    # Assert that the clusters list is not empty
    self.assertTrue(len(clusters) > 0)