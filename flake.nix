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
        shellHook =''
        '';
      };
    };
  
  };

}
