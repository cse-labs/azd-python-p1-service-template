
@description('The name of the key vault to grant access to')
param keyVaultName string

@description('Specifies the object ID of the federated app dev principal identity.')
param principalId string

param policyName string = 'add'

@description('Specifies the permissions to secrets in the vault. Valid values are: all, get, list, set, delete, backup, restore, recover, and purge.')
param secretsPermissions array = [
  'get'
]

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' existing = {
  name: keyVaultName
}

resource keyVaultAccessPolicies 'Microsoft.KeyVault/vaults/accessPolicies@2022-07-01' = {
  parent: keyVault
  name: policyName
  properties: {
    accessPolicies: [ 
      {
        objectId: principalId
        tenantId: subscription().tenantId
        permissions: { secrets: secretsPermissions }
      }
    ]
  }
}
