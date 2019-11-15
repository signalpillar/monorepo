{ pkgs ? import <nixpkgs> {} }:

  pkgs.mkShell {
    buildInputs = [
      pkgs.git
      pkgs.python36Packages.cython
      pkgs.just
    ];
  }
