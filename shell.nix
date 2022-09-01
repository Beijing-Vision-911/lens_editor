{ stdenv
, lib
, mkShell
, python38Packages
, taglib
, openssl
, git
, libxml2
, libxslt
, libzip
, zlib
  # qt deps  
, libGL
, libxkbcommon
, fontconfig
, libX11
, glib
, freetype
, dbus
, wayland
  # pyright
, nodejs
}:
let
  pypkgs = python38Packages;
in
mkShell rec {
  name = "pythonVenv";
  venvDir = "./.venv";
  buildInputs = [
    pypkgs.python
    pypkgs.venvShellHook

    taglib
    openssl
    git
    libxml2
    libxslt
    libzip
    zlib
    nodejs
  ];
  postShellHook =
    let
      libs = [
        stdenv.cc.cc
        libGL
        libxkbcommon
        fontconfig
        libX11
        glib
        freetype
        dbus
        wayland
        zlib
        taglib
        openssl
        git
        libxml2
        libxslt
        libzip
      ];
    in
    ''
      export LD_LIBRARY_PATH="/run/opengl-driver/lib:${lib.makeLibraryPath libs}"
    '';

}
