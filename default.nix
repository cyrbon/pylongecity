with import <nixpkgs> {};
(let 
  pylongecity = python35Packages.buildPythonPackage rec {
      pname = "pylongecity";
      name = pname + "-" + version;
      version = "0.1.1";
      src = pkgs.fetchFromGitHub {
        owner = "cyrbon";
        repo = pname;
        rev = version;
        sha256 = "1dgg810x9vyfdn932h0im866m4az70hqjk5xpn3v1qn9l798bbxq";
      };
      doCheck = false;
      propagatedBuildInputs = with pkgs.python35Packages; [ requests2 pyquery joblib]; 
      meta = {
        homepage = "http://github.com/cyrbon/pylongecity/";
        description = "Simple script to search longecity threads for relevant information";
        license = pkgs.lib.licenses.asl20; 
      };
};
in pkgs.python35.buildEnv.override rec {
  extraLibs = with pkgs.python35Packages; 

  ######## Add packages you want in the environment here #########
  # It can be python packages or non-python packages.
  # If not a python package, then use pkgs prefix `pkgs.packageName` like `pkgs.openssl` 
  # Otherwise just use the name of the python package like `pandas` or `numpy`
  # By default, it includes extra `ipykernel`, which is ipython kernel.

  [ pylongecity ipykernel];

}
).env 
