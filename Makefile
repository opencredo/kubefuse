myna:
	./kubectl.myna.sh

import_myna:
	DATABASE_LOCATION="`pwd`/kubectl.db" myna --import tests/kubectl.json 

test: import_myna
	DATABASE_LOCATION="`pwd`/kubectl.db" nosetests -s

test3: import_myna
	DATABASE_LOCATION="`pwd`/kubectl.db" python3 -m nose -s

release:
	python setup.py register
	python setup.py sdist upload
