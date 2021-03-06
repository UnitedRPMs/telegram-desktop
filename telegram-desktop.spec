%global debug_package %{nil}
%global  _hardened_build     1
#define _legacy_common_support 1
%global _disable_ld_no_undefined %nil
%undefine __cmake_in_source_build

# Telegram Desktop's constants...
%global appname tdesktop
%global launcher telegramdesktop

# tg_owt
%global commit0 a19877363082da634a3c851a4698376504d2eaee
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver git%{shortcommit0}

# libvpx
%global commit1 ebefb90b75f07ea5ab06d6b2a5ea5355c843d266
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

# libyuv
%global commit2 c41eabe3d4e1c30f8cb1c5f8660583bf168d426a
%global shortcommit2 %(c=%{commit2}; echo ${c:0:7})


Name: telegram-desktop
Version: 2.6.1
Release: 7%{?dist}

License: GPLv3+ and LGPLv2+ and LGPLv3
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app
Source0: https://github.com/telegramdesktop/tdesktop/releases/download/v%{version}/tdesktop-%{version}-full.tar.gz

Source1: https://github.com/desktop-app/tg_owt/archive/%{commit0}/%{name}-%{shortcommit0}.tar.gz
Source2: https://chromium.googlesource.com/webm/libvpx.git/+archive/%{commit1}.tar.gz#/libvpx-%{shortcommit1}.tar.gz
Source3: https://chromium.googlesource.com/libyuv/libyuv.git/+archive/%{commit2}.tar.gz#/libyuv-%{shortcommit2}.tar.gz

Patch: 0002-tg_owt-fix-name-confliction.patch
Patch1: 0001-use-bundled-ranged-exptected-gsl.patch

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
#BuildRequires: tg_owt-devel
BuildRequires: xcb-util-keysyms-devel

BuildRequires: pkgconfig(alsa)
BuildRequires: ffmpeg-devel
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(protobuf)
BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xtst)

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
%setup -n tdesktop-%{version}-full -a1
%patch1 -p2 

echo "target_link_libraries(external_webrtc INTERFACE jpeg)" | tee -a cmake/external/webrtc/CMakeLists.txt

mkdir -p %{_builddir}/Libraries
cp -rf tg_owt-%{commit0} %{_builddir}/Libraries/tg_owt

tar -xf %{S:2} -C %{_builddir}/Libraries/tg_owt/src/third_party/libvpx/source/libvpx
tar -xf %{S:3} -C %{_builddir}/Libraries/tg_owt/src/third_party/libyuv
%patch -p1 -d %{_builddir}/Libraries/tg_owt

%build

  # Static
  pushd %{_builddir}/Libraries/tg_owt
  mkdir -p out/Release
  cmake -B out/Release -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POSITION_INDEPENDENT_CODE=TRUE \
    -DCMAKE_INSTALL_PREFIX=/usr \
    -DCMAKE_AR=%{_bindir}/gcc-ar \
    -DCMAKE_RANLIB=%{_bindir}/gcc-ranlib \
    -DCMAKE_NM=%{_bindir}/gcc-nm \
    -DTG_OWT_SPECIAL_TARGET=linux \
    -DTG_OWT_LIBJPEG_INCLUDE_PATH=/usr/include \
    -DTG_OWT_OPENSSL_INCLUDE_PATH=/usr/include \
    -DTG_OWT_OPUS_INCLUDE_PATH=/usr/include/opus \
    -DTG_OWT_FFMPEG_INCLUDE_PATH=/usr/include/ffmpeg \
    -DTG_OWT_PACKAGED_BUILD=TRUE
 

  %ninja_build -C out/Release
popd

# Turns out we're allowed to use the official API key that telegram uses for their snap builds:
    # https://github.com/telegramdesktop/tdesktop/blob/8fab9167beb2407c1153930ed03a4badd0c2b59f/snap/snapcraft.yaml#L87-L88
    # Thanks @primeos!
    mkdir -p build 
    pushd build 
    cmake  \
        -DCMAKE_INSTALL_PREFIX=/usr \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_AR=%{_bindir}/gcc-ar \
        -DCMAKE_RANLIB=%{_bindir}/gcc-ranlib \
        -DCMAKE_NM=%{_bindir}/gcc-nm \
        -DCMAKE_POSITION_INDEPENDENT_CODE=TRUE \
        -DTDESKTOP_API_ID=611335 \
        -DTDESKTOP_API_HASH=d524b414d21f4d37f08684c1df41ac9c \
        -DTDESKTOP_LAUNCHER_BASENAME="telegramdesktop" \
        -DDESKTOP_APP_SPECIAL_TARGET="" \
        -DDESKTOP_APP_USE_GLIBC_WRAPS=OFF \
        -DDESKTOP_APP_QTWAYLANDCLIENT_PRIVATE_HEADERS=OFF \
        -DDESKTOP_APP_USE_PACKAGED=ON \
        -DDESKTOP_APP_USE_PACKAGED_FONTS=ON \
        -DDESKTOP_APP_DISABLE_CRASH_REPORTS=ON \
        -Wno-dev \
	-Wno-unknown-warning-option ..
	popd

    %make_build -C build  

%install
    %make_install -C build 

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
* Sun Feb 28 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> - 2.6.1-7
- Inital build
