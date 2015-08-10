if [ -z "$(nix-env 2>&1 | grep -o 'help')" ]; then
	curl https://nixos.org/nix/install | sh
	. ~/.nix-profile/etc/profile.d/nix.sh
fi
