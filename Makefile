.PHONY: all install test

all:
	./build_helpers/nix_install.sh
	nix-shell --run 'python3 -m production.test_all'
