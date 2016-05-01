KubeFuse
========

Kubernetes as a Filesystem


## Why?

Because kubectl is great, but sometimes a bit slow to navigate.

Enter KubeFuse.

Alpha quality software for quick Kubernetes browsing. What's not to love.

## Features

* Browse Kubernetes resources in your file system...
* ...with (some of) your favourite tools: `ls`, `find`, `cat`, ...
* List services, replication controllers, pods and namespaces
* Export resources to YAML and JSON
* Access resource descriptions as files (eg. `cat ~/kubernetes/default/pod/postgres-aazm1/describe`)
* And that's it, but more may be coming. 

## Requirements

KubeFuse runs on both Linux and Mac, but does require additional libraries to be installed (eg. OSXFUSE).

KubeFuse also uses the kubectl binary under the hood so this needs to be on the path. 

## Setup

```
pip install -r requirements.txt
```

## Usage

```
python kubefuse.py [MOUNTPOINT] 
```

Examples
========

Create the mount:

```
python kubefuse.py ~/kubernetes
```

List all pods in the default namespace:

```
ls ~/kubernetes/default/pod/
```

List all known objects in the default namespace:

```
find ~/kubernetes/default -type d -mindepth 2
```

Describe the `postgres` pod:

```
cat ~/kubernetes/default/pod/postgres-aazm1/describe
```

Get logs from a `graphite` pod:

```
cat ~/kubernetes/default/pod/graphite-i3bb2/logs
```

Export the `postgres` replication controller to YAML:

```
cat ~/kubernetes/default/rc/postgres/yaml
```

Export the `postgres` replication controller to JSON:

```
cat ~/kubernetes/default/rc/postgres/json
```

Export all service definitions in the default namespace:

```
find ~/kubernetes/default/svc -name yaml | while read line ; do cat $line ; echo "----" ; echo ; done
```

Bugs
====

Yes.
