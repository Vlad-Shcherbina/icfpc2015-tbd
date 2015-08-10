let
  pkgs = import <nixpkgs> {};
  hypothesisLatest = pkgs.python34Packages.buildPythonPackage rec {
    name = "hypothesis-1.10.1";
    doCheck = false;
    src = pkgs.fetchurl {
      url = "https://pypi.python.org/packages/source/h/hypothesis/hypothesis-1.10.1.tar.gz";
      md5 = "e8086239a853e1e873cc8074dfccfa74";
    };
    meta = with pkgs.stdenv.lib; {
      description = "A Python library for property based testing";
      homepage = https://github.com/DRMacIver/hypothesis;
      license = licenses.mpl20;
    };
  };
  tbdPyEnv = pkgs.python.buildEnv.override {
    extraLibs = [
      hypothesisLatest
      pkgs.python34Packages.nose
      pkgs.python34Packages.coverage
      pkgs.python34Packages.tornado
      pkgs.python34Packages.requests2
      pkgs.python34Packages.psutil
    ];
    ignoreCollisions = true;
  };

in

{
  icfpc2015TbdEnv = pkgs.buildEnv {
    name = "icfpc2015-tbd-env";
    paths = [
      tbdPyEnv
      pkgs.stdenv
      pkgs.sqlite
      pkgs.swig3
    ];
  };
}

