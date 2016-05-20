from setuptools import setup, find_packages

setup(
    name = "kubefuse",
    version = "0.4.0",
    packages = find_packages(),
    author = "Bart Spaans",
    author_email = "bart.spaans@gmail.com",
    url = "https://github.com/bspaans/kubefuse",
    description = "A FUSE file system for Kubernetes",
    classifiers = [
	    'Programming Language :: Python',
    ],
    entry_points = {
	    'console_scripts': [
		    'kubefuse = kubefuse.kubefuse:main'
	    ]
    }
 )
