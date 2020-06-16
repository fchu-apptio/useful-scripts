
# Prerequisites

pip3 install requests

# Provision router
Provision router instance
```
python3 ./provision_router.py --router us-dev --env main --customer column.com --bff-version 1.0.1-dev_wip-r12-BIIT-77586-1111 --biit-address column-reorder.dapt.to > logs/provision_column.log
```
```
python3 provision_router.py -r local --env demo.apptio.net_localhost-9050 --customer fchu.dev -v bff-27979 -b localhost:9180 -a BFF
```

# Query Router
Search for environments
```
python3 ./query_router.py -f search_environments --router us-dev --version "12" --name "col"
```

Search for bad environments and print to output file
```
python3 ./query_router.py -f search_environments -r us-prod -c bad -i "csbox-us-east-r12-internal.apptio.com" -o logs/bad_env_us-prod.json
```

Search for versions
```
python3 ./query_router.py -f search_versions -r us-dev --version "r12.9"
```

Search for bad versions and print to output file
```
python3 ./query_router.py -f search_versions -r au-prod -c bad -o logs/bad_ver_au-prod.json
```

# Add router version
```
python3 ./addRouterVersion.py -r local -b host.docker.internal:9080 -v bff-20000 -a BFF -p true
```

# Upgrade environments
```
python3 ./upgradeEnvironments.py -r local --old-version bff-16494 --new-version bff-20000 -a BFF
```
```
python3 ./upgradeEnvironments.py -r local --fqen "fchu.dev:demo.apptio.net_localhost-9050" --new-version bff-20000 -a BFF
```

# Delete items
```
python3 ./deleteItems.py -i ./logs/bad_env_local.json -l environment --router local
```

```
python3 ./deleteItems.py -i ./logs/bad_env_local.json -l envVersion environment customer version --router local
```