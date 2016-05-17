#!/bin/bash 

# Put myna into capture mode 
export CAPTURE=1

# Remove the old myna database if it exists
rm -f processes.db

# Run the commands I need for testing:
myna kubectl get namespaces
myna kubectl get pods --all-namespaces
myna kubectl get svc --all-namespaces
myna kubectl get rc --all-namespaces

# Export the results
myna --export | python -m json.tool > tests/kubectl.json
rm -f processes.db
