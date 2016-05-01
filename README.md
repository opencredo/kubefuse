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

List all known objects:

```
find ~/kubernetes/all/ -type d
```

Export the `kubernetes` replication controller to YAML:

```
cat ~/kubernetes/default/rc/postgres/yaml
```

Export the `kubernetes` replication controller to JSON:

```
cat ~/kubernetes/default/rc/postgres/json
```
