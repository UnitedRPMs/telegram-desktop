%global debug_package %{nil}
%global  _hardened_build     1
#define _legacy_common_support 1
%global _disable_ld_no_undefined %nil
%undefine __cmake_in_source_build

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop



Name: telegram-desktop
Version: 2.8.4
Release: 7%{?dist}

License: GPLv3+ and LGPLv2+ and LGPLv3
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app
Source0: https://github.com/telegramdesktop/tdesktop/releases/download/v%{version}/tdesktop-%{version}-full.tar.gz

Patch2:	fix-gcc11-assert.patch
ExclusiveArch: x86_64

BuildRequires: cmake(Microsoft.GSL)
BuildRequires: cmake(OpenAL)
BuildRequires: cmake(Qt5Core)
BuildRequires: cmake(Qt5DBus)
BuildRequires: cmake(Qt5Gui)
BuildRequires: cmake(Qt5Network)
BuildRequires: cmake(Qt5Widgets)
BuildRequires: cmake(Qt5XkbCommonSupport)
BuildRequires: cmake(dbusmenu-qt5)
BuildRequires: cmake(range-v3)
BuildRequires: cmake(tl-expected)

BuildRequires: pkgconfig(gio-2.0)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavresample)
BuildRequires: pkgconfig(libavutil)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libswscale)
BuildRequires: pkgconfig(libxxhash)
BuildRequires: pkgconfig(openssl)
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(gtk+-3.0)

BuildRequires: cmake
BuildRequires: desktop-file-utils
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: libappstream-glib
BuildRequires: libatomic
BuildRequires: libqrcodegencpp-devel
BuildRequires: libstdc++-devel
BuildRequires: minizip-compat-devel
BuildRequires: ninja-build
BuildRequires: python3
BuildRequires: qt5-qtbase-private-devel
BuildRequires: qt5-qtwayland-devel
BuildRequires: pkgconfig(Qt5Svg)
BuildRequires: qt5-qtbase-static
BuildRequires: libjpeg-turbo-devel 
BuildRequires: kf5-kwayland-devel
BuildRequires: tg_owt-devel
BuildRequires: xcb-util-keysyms-devel
BuildRequires: pipewire-devel
BuildRequires: rlottie-devel
BuildRequires: rnnoise-devel
BuildRequires: pkgconfig(alsa)
BuildRequires: ffmpeg-devel
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(protobuf)
BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xtst)
BuildRequires: pkgconfig(glibmm-2.4)
BuildRequires: pkgconfig(webkit2gtk-4.0)
BuildRequires: extra-cmake-modules

BuildRequires: yasm

Requires: hicolor-icon-theme
Requires: open-sans-fonts
Requires: qt5-qtimageformats%{?_isa}

# Short alias for the main package...
Provides: telegram = %{version}-%{release}

%description
Telegram is a messaging app with a focus on speed and security, it’s super
fast, simple and free. You can use Telegram on all your devices at the same
time — your messages sync seamlessly across any number of your phones,
tablets or computers.

With Telegram, you can send messages, photos, videos and files of any type
(doc, zip, mp3, etc), as well as create groups for up to 50,000 people or
channels for broadcasting to unlimited audiences. You can write to your
phone contacts and find people by their usernames. As a result, Telegram is
like SMS and email combined — and can take care of all your personal or
business messaging needs.

%prep
%setup -n tdesktop-%{version}-full 
%patch2 -p1 -d Telegram/lib_webview/

echo "target_link_libraries(external_webrtc INTERFACE jpeg)" | tee -a cmake/external/webrtc/CMakeLists.txt
echo "find_package(X11 REQUIRED COMPONENTS Xcomposite Xdamage Xext Xfixes Xrender Xrandr Xtst)" | tee -a cmake/external/webrtc/CMakeLists.txt
echo "target_link_libraries(external_webrtc INTERFACE Xcomposite Xdamage Xext Xfixes Xrandr Xrender Xtst)" | tee -a cmake/external/webrtc/CMakeLists.txt
sed -i 's/DESKTOP_APP_USE_PACKAGED/NO_ONE_WILL_EVER_SET_THIS/' cmake/external/rlottie/CMakeLists.txt


sed -i "s|set(webrtc_build_loc.*|set(webrtc_build_loc %_libdir)|" cmake/external/webrtc/CMakeLists.txt
# TODO: there are incorrec using and linking libyuv
#sed -i "s|\(desktop-app::external_rnnoise\)|\1 -lyuv|" Telegram/cmake/lib_tgcalls.cmake
    


# Turns out we're allowed to use the official API key that telegram uses for their snap builds:
    # https://github.com/telegramdesktop/tdesktop/blob/8fab9167beb2407c1153930ed03a4badd0c2b59f/snap/snapcraft.yaml#L87-L88
    # Thanks @primeos!
    
    mkdir -p build 
    cmake -B build  \
    	-G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr \
        -DCMAKE_AR=%{_bindir}/gcc-ar \
        -DCMAKE_RANLIB=%{_bindir}/gcc-ranlib \
        -DCMAKE_NM=%{_bindir}/gcc-nm \
        -DTDESKTOP_API_ID=611335 \
        -DTDESKTOP_API_HASH=d524b414d21f4d37f08684c1df41ac9c \
        -DTDESKTOP_LAUNCHER_BASENAME="telegramdesktop" \
        -DDESKTOP_APP_SPECIAL_TARGET="" \
        -Wno-dev \
	-Wno-unknown-warning-option 
	
	
#         -DCMAKE_DISABLE_FIND_PACKAGE_rlottie=ON \
#        -DCMAKE_DISABLE_FIND_PACKAGE_rnnoise=ON \	

    %ninja_build -C build   -j2

%install
    %ninja_install -C build  -j2

%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{launcher}.appdata.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/%{launcher}.desktop

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/%{name}
%{_datadir}/applications/%{launcher}.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
%{_metainfodir}/%{launcher}.appdata.xml

%changelog

* Fri Jul 09 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> - 2.8.4-7
- Updated to 2.8.4

* Fri May 07 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> - 2.7.4-7
- Updated to 2.7.4

* Sun Feb 28 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> - 2.6.1-7
- Inital build
