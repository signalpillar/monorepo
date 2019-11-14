{ pkgs ? import <nixpkgs> {} }:

  let cockroachdb = import ./db.nix {pkgs = pkgs;};
  in pkgs.mkShell {
    buildInputs = [
      pkgs.just
      cockroachdb
    ];
  }
