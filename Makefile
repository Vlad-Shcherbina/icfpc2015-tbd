.PHONY: all install test

all:
	nix-shell --run 'python3 -m production.test_all'
