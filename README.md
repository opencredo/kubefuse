KubeFuse
========

Kubernetes as a Filesystem


## Why?

Because kubectl is great, but sometimes a bit slow to navigate.

Enter KubeFuse.

Alpha quality software for quick Kubernetes browsing. What's not to love.

## Features

* Browse Kubernetes resources in your file system
* List services, replication controllers, pods and namespaces
* Works with `ls` and `find`
* That's it, but more stuff is planned.

## Requirements

Kubefuse runs on both Linux and Mac, but does require additional libraries to be installed (eg. OSXFUSE).

Kubefuse also uses the kubectl binary under the hood so this needs to be on the path. 

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
