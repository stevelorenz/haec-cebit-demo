#
# Makefile
#
# vim:ft=make
#

FABFILE = fabfile.py
NETEMSRC = $(shell find ./ -name '*.py')
PYSRC = $(FABFILE) $(NETEMSRC)
PYCFILE = $(shell find ./ -name '*.pyc')

all: codecheck

codecheck: $(PYSRC)
	-echo "Running code check"
	python2 -m pyflakes $(PYSRC)
	python2 -m pylint $(PYSRC)
	python2 -m pep8 $(PYSRC)

errcheck: $(PYSRC)
	-echo "Running check for errors only"
	python2 -m pyflakes $(PYSRC)
	python2 -m pylint $(PYSRC)

build-iperf-demo-pc: ./iperf-server-client-demo.go
	@echo "Build the Iperf-server-client-demo for pc."
	go build ./iperf-server-client-demo.go

build-iperf-demo-odroid: ./iperf-server-client-demo.go
	@echo "Build the Iperf-server-client-demo for odroid."
	GOOS=linux GOARCH=arm GOARM=7 go build -v ./iperf-server-client-demo.go

clean:
	@echo "Clean tmp file."
	@echo $(PYCFILE)
	rm -rf $(PYCFILE)
