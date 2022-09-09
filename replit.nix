{ pkgs }: {
	deps = [
		pkgs.python39Packages.pip
		pkgs.nodejs
		pkgs.vim
		pkgs.python39Full
		pkgs.clang_12
		pkgs.ccls
		pkgs.gdb
		pkgs.gnumake
    pkgs.wget
    pkgs.adoptopenjdk-bin
	];
}