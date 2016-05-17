
deps: 
	glide up

build: deps
	go build

install: deps
	go install

myna:
	./kubectl.myna.sh
