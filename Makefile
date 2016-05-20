myna:
	./kubectl.myna.sh

test:
	DATABASE_LOCATION="`pwd`/kubectl.db" myna --import tests/kubectl.json 
	DATABASE_LOCATION="`pwd`/kubectl.db" nosetests -s

release:
	python setup.py register
	python setup.py sdist upload
