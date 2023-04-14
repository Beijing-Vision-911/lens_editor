{ stdenv
, lib
, mkShell
, python311Packages
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
# x11 deps
, xcb-util-cursor
, xcbutilwm
, xcbutilimage 
, xcbutilkeysyms
, xcbutilrenderutil
, libXrender
, libxcb
}:
let
  pypkgs = python311Packages;
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
	xcb-util-cursor
	xcbutilwm
	xcbutilimage 
	xcbutilkeysyms
	xcbutilrenderutil
	libXrender
	libxcb
      ];
    in
    ''
      export LD_LIBRARY_PATH="/run/opengl-driver/lib:${lib.makeLibraryPath libs}"
    '';

}
