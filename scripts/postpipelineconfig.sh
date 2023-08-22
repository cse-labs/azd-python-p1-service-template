#!/bin/bash
PWD=$(dirname "$0")

function sourceAzdEnvVars() {
while IFS='=' read -r key value; do
  value=$(echo "$value" | sed 's/^"//' | sed 's/"$//')
  export "$key=$value"
done <<EOF
$(azd env get-values)
EOF
}

GIT_CONTROLLER_URL=$(git remote get-url origin)

function pre_validation () {
  local git_url=$1

  [[ ! -z $git_url ]] && {
        echo "💥 Error! Git remote is missing. This script should run after azd pipeline config!"
        exit
  }

  for varName in AZURE_AKS_CLUSTER_NAME GITHUB_TOKEN; do
    varVal=$(eval echo "\${$varName}")
    [[ -z $varVal ]] && {
      echo "💥 Error! Required variable '$varName' is not set!"
      varUnset=true
    }
  done
}

sourceAzdEnvVars
pre_validation
GIT_CONTROLLER_REPO=$(echo $GIT_CONTROLLER_URL | sed 's|https://github.com/||')

gh secret set GH_TOKEN --body "${GITHUB_TOKEN}" --repo $GIT_CONTROLLER_REPO

for env in AZURE_AKS_CLUSTER_NAME; do
  echo "setting env variable: ${env} in repo: ${GIT_CONTROLLER_REPO}"
  envVal=$(eval echo "\${$env}")
  gh variable set $env --body "${envVal}" --repo $GIT_CONTROLLER_REPO
done
