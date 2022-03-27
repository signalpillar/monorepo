{ nixpkgs ? import <nixpkgs> {} }:

with nixpkgs;

let
  basePyPackages = ps: with ps; [
  ];

in

mkShell {
    name = "health-calculator";

    # The packages in the `buildInputs` list will be added to the PATH in our shell
    # Python-specific guide:
    # https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md
    buildInputs = [
      poetry
      docker-compose
    ];
    shellHook = ''
        export SOURCE_DATE_EPOCH=$(date +%s)
    '';
}
