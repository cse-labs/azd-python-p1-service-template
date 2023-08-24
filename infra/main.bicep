targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the resource group.')
param rgName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('ID of the principal')
param principalId string = ''

@description('The name of the key vault to grant access to')
param keyVaultName string

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: rgName
}

module kv_policies './kv-access-policies.bicep' = {
  scope: resourceGroup
  name: 'keyvaultPolicy'
  params: {
    keyVaultName: keyVaultName
    principalId: principalId  
  }
}

output AZURE_LOCATION string = location
