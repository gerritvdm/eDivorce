#! /bin/bash
_includeFile=$(type -p overrides.inc)
if [ ! -z ${_includeFile} ]; then
  . ${_includeFile}
else
  _red='\033[0;31m'; _yellow='\033[1;33m'; _nc='\033[0m'; echo -e \\n"${_red}overrides.inc could not be found on the path.${_nc}\n${_yellow}Please ensure the openshift-developer-tools are installed on and registered on your path.${_nc}\n${_yellow}https://github.com/BCDevOps/openshift-developer-tools${_nc}"; exit 1;
fi

if createOperation; then
  # Randomly generate a set of credentials without asking ...
  printStatusMsg "Creating a set of random user credentials ..."
  writeParameter "BASICAUTH_USERNAME" $(generateUsername) "false"
  writeParameter "BASICAUTH_PASSWORD" $(generatePassword) "false"

  # Ask for sensitive information ...
  readParameter "EDIVORCE_KEYCLOAK_SECRET - Please provide the KeyCloak client secret for the eDivorce aplication. The default is a blank string." EDIVORCE_KEYCLOAK_SECRET "" "false"
  readParameter "EFILING_HUB_KEYCLOAK_SECRET - Please provide the KeyCloak client secret for the eFiling Hub aplication. The default is a blank string." EFILING_HUB_KEYCLOAK_SECRET "" "false"
else
  # Secrets are removed from the configurations during update operations ...
  printStatusMsg "Update operation detected ...\nSkipping the generation of random user credentials ...\n"
  writeParameter "BASICAUTH_USERNAME" "generation_skipped" "false"
  writeParameter "BASICAUTH_PASSWORD" "generation_skipped" "false"

  printStatusMsg "Update operation detected ...\nSkipping prompts for secrets ...\n"
  writeParameter "EDIVORCE_KEYCLOAK_SECRET" "prompt_skipped" "false"
  writeParameter "EFILING_HUB_KEYCLOAK_SECRET" "prompt_skipped" "false"
fi

SPECIALDEPLOYPARMS="--param-file=${_overrideParamFile}"
echo ${SPECIALDEPLOYPARMS}




