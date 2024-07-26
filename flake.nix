{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs, }:
  let
    system =  "x86_64-linux";
    pkgs = import nixpkgs{inherit system;};
  in {
  
    devShells.${system} = {
      default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          python312Packages.pip
          
        ];
        shellHook = ''
          export PIP_PREFIX=$(pwd)/_build/pip_packages #Dir where built packages are stored
          export PYTHONPATH="$PIP_PREFIX/${pkgs.python3.sitePackages}:$PYTHONPATH"
          export PATH="$PIP_PREFIX/bin:$PATH"
          unset SOURCE_DATE_EPOCH
        '';
      };
    };
  
  };

}
