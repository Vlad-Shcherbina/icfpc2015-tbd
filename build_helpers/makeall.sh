build_helpers/nix_install.sh              && \
  . ~/.nix-profile/etc/profile.d/nix.sh   && \
  nix-shell --run 'python3 -m production.test_all'
