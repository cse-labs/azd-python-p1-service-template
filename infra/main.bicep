targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the resource group.')
param rgName string

@minLength(1)
@description('Primary location for all resources')
param location string

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: rgName
}

output AZURE_LOCATION string = location
