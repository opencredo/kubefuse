#!/bin/bash 

# Put myna into capture mode 
export CAPTURE=1

# Remove the old myna database if it exists
rm -f processes.db

# Run the commands I need for testing:
myna kubectl get namespaces
myna kubectl get ns -o yaml
myna kubectl get pods --all-namespaces
myna kubectl get pod -o yaml --namespace default
myna kubectl get svc --all-namespaces
myna kubectl get svc -o yaml --namespace default
myna kubectl get rc --all-namespaces
myna kubectl get rc -o yaml --namespace default

# I don't want to hardcode pod names, so I'm getting the first one 
# and using that. The python unit tests do the same thing.

FIRST_POD=$(kubectl get pod -o yaml | grep "name: " | head -1 | awk '{print $2}')
myna kubectl get pod $FIRST_POD -o yaml --namespace default
myna kubectl get pod $FIRST_POD -o json --namespace default
myna kubectl describe pod $FIRST_POD --namespace default
myna kubectl logs $FIRST_POD --namespace default

# Export the results
myna --export | python -m json.tool > tests/kubectl.json
rm -f processes.db
