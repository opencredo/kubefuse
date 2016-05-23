from setuptools import setup, find_packages

setup(
    name = "kubefuse",
    version = "0.5.0",
    packages = find_packages(),
    author = "Bart Spaans",
    author_email = "bart.spaans@gmail.com",
    url = "https://github.com/bspaans/kubefuse",
    description = "A FUSE file system for Kubernetes",
    classifiers = [
	    'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System',
        'Topic :: System :: Clustering',
        'Topic :: System :: Filesystems',
    ],
    license="Apache License v2",
    entry_points = {
	    'console_scripts': [
		    'kubefuse = kubefuse.kubefuse:main'
	    ]
    }
 )
