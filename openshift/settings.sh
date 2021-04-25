export PROJECT_NAMESPACE=${PROJECT_NAMESPACE:-ed44ad}
export GIT_URI=${GIT_URI:-"https://github.com/bcgov/eDivorce.git"}
export GIT_REF=${GIT_REF:-"master"}

# The templates that should not have their GIT referances(uri and ref) over-ridden
# Templates NOT in this list will have they GIT referances over-ridden
# with the values of GIT_URI and GIT_REF
export -a skip_git_overrides="schema-spy-build.yaml s2i-nginx-build.yaml backup-build.yaml clamav-build.yaml"