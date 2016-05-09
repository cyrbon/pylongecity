{ mkDerivation, pkgs }:

mkDerivation {
  pname = "pylongecity";
  version = "0.1";
  src = builtins.filterSource (path: type: baseNameOf path != ".git") ./.;
  buildDepends = [
    pyquery
    joblib
  ];
  license = null;
}
