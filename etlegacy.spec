%define __cmake_in_source_build 1

#
%global gittag v%{version}
#%%global gitcommit 886f0ef0d6a48b527a25409dbd6eb350e6610e48
%if 0%{?gitcommit:1}
%global snapdate 20211102
%global snapinfo %{snapdate}git%(echo %{gitcommit}| cut -c 1-8)
%global gitver %{gitcommit}
%else
%global gitver %{version}
%endif

%global __provides_exclude_from ^%{_libdir}/%{name}/.*\\.so$

Name:           etlegacy
Version:        2.81.1
Release:        2%{?snapinfo:.%{snapinfo}}%{?dist}
Summary:        Fully compatible client and server for the game Wolfenstein: Enemy Territory

License:        GPLv3
URL:            https://www.etlegacy.com/
Source0:        https://github.com/etlegacy/etlegacy/archive/%{gittag}/%{name}-%{gitver}.tar.gz
Source1:        etlegacy-data.html
# Launcher finds data or directs how to fetch them
Source2:        https://raw.githubusercontent.com/pemensik/etlegacy-tools/installer/linux/etl-launcher
Source3:        https://raw.githubusercontent.com/pemensik/etlegacy-tools/installer/linux/etl-installer
Source4:        com.etlegacy.ETLegacy.installer.desktop

# https://github.com/etlegacy/etlegacy/pull/2289
Patch2:         etlegacy-2.81-cjson-devel.patch

BuildRequires:  gcc gcc-c++
BuildRequires:  cmake
BuildRequires:  libpng-devel freetype-devel SDL2-devel curl-devel openssl-devel sqlite-devel
BuildRequires:  libtheora-devel libogg-devel libvorbis-devel libjpeg-turbo-devel
BuildRequires:  glew-devel
BuildRequires:  lua-devel
BuildRequires:  openal-soft-devel
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  systemd-rpm-macros
BuildRequires:  sed
BuildRequires:  cjson-devel
%if 0%{fedora} > 37
BuildRequires:  minizip-ng-devel
%else
BuildRequires:  minizip-devel
%endif

Requires:       shared-mime-info
# Can be produced by game-data-packager enemy-territory
Suggests:       enemy-territory-data
Suggests:       game-data-packager
Suggests:       %{name}-installer

%description
Welcome to ET: Legacy, an open source project that aims to create
a fully compatible client and server for the popular online FPS game
Wolfenstein: Enemy Territory - whose game-play is still considered
unmatched by many, despite its great age.

%package installer
Summary:        Data installation from Wolfenstein: Enemy Territory package
BuildArch:      noarch
Recommends:     dialog
Requires:       %{name} = %{version}-%{release}
Requires:       curl tar bash

%description installer
Welcome to ET: Legacy, an open source project that aims to create
a fully compatible client and server for the popular online FPS game
Wolfenstein: Enemy Territory - whose game-play is still considered
unmatched by many, despite its great age.

Installer provides easy way to install required data files from
the original game. Can be removed after game data installation.

%prep
%autosetup -n %{name}-%{gitver} -p1

# Use system flags for all products
sed -e 's,^\s*SET(CMAKE_BUILD_TYPE "Release"),# &,' -i cmake/ETLCommon.cmake

%build
%cmake -DBUNDLED_LIBS=OFF -DCROSS_COMPILE32=OFF -DBUILD_MOD=ON \
       -DCLIENT_GLVND=ON \
       -DFEATURE_RENDERER2=OFF -DINSTALL_DEFAULT_BASEDIR=%{_libdir}/%{name} \
       -DINSTALL_DEFAULT_MODDIR=%{_libdir}/%{name} \
       -DFEATURE_AUTOUPDATE=OFF -DINSTALL_EXTRA=OFF
#
%cmake_build


%install
%cmake_install
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_datadir}/%{name}/etmain
touch %{buildroot}%{_libdir}/%{name}/etmain/pak{0,1,2}.pk3
install %{SOURCE1} %{buildroot}%{_datadir}/%{name}/
install -m 0755 %{SOURCE2} %{buildroot}%{_bindir}/etl-launcher
install -m 0755 %{SOURCE3} %{buildroot}%{_bindir}/etl-installer
install misc/etlegacy*.service %{buildroot}%{_unitdir}/
install %{SOURCE4} %{buildroot}%{_datadir}/applications/com.etlegacy.ETLegacy.installer.desktop
sed -e 's/^Exec=etl\(\.[a-z_0-9]\+\)\?\s/Exec=etl-launcher "\1" /' \
    -i %{buildroot}%{_datadir}/applications/com.etlegacy.ETLegacy*.desktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.etlegacy.ETLegacy*.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/com.etlegacy.ETLegacy.installer.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/com.etlegacy.ETLegacy.metainfo.xml


%files
%license COPYING.txt
%doc README.md docs/INSTALL.txt
%{_bindir}/etl{,ded}.*
%{_bindir}/etl-launcher
%{_mandir}/man6/etl*.6*
%{_datadir}/icons/hicolor/scalable/apps/etl*
%{_datadir}/applications/com.etlegacy.ETLegacy*.desktop
%{_metainfodir}/com.etlegacy.ETLegacy.metainfo.xml
%{_datadir}/mime/packages/etlegacy.xml
%{_unitdir}/%{name}*.service
%{_datadir}/%{name}
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/legacy
%{_libdir}/%{name}/librenderer_*.so
%{_libdir}/%{name}/etmain/*.cfg
%dir %{_libdir}/%{name}/etmain
%ghost %{_libdir}/%{name}/etmain/pak0.pk3
%ghost %{_libdir}/%{name}/etmain/pak1.pk3
%ghost %{_libdir}/%{name}/etmain/pak2.pk3


%files installer
%{_bindir}/etl-installer
%{_datadir}/applications/com.etlegacy.ETLegacy.installer.desktop

%changelog
* Thu Aug 03 2023 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 2.81.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Fri Mar 17 2023 Petr Menšík <pemensik@redhat.com> - 2.81.1-1
- Update to 2.81.1

* Wed Mar 01 2023 Petr Menšík <pemensik@fedoraproject.org> - 2.81.0-1
- Update to 2.81.0
- Address feedback from review rfbz#5824
- Build with current cjson-devel package
- Require minizip-ng explicitly for newer releases

* Fri Oct 21 2022 Petr Menšík <pemensik@redhat.com> - 2.80.2-3
- Address review comment #14 suggestions, use glvnd

* Fri Oct 21 2022 Petr Menšík <pemensik@redhat.com> - 2.80.2-2
- Fix issue with recent SDL on f36+

* Wed Jul 06 2022 Petr Menšík <pemensik@redhat.com> - 2.80.2-1
- Update to 2.80.2

* Mon Oct 25 2021 Petr Menšík <pemensik@redhat.com> - 2.78.0-5
- Fix rpmlint detected issues

* Mon Oct 25 2021 Petr Menšík <pemensik@redhat.com> - 2.78.0-4
- Add installer to simplify data installation

* Fri Oct 22 2021 Petr Menšík <pemensik@redhat.com> - 2.78.0-3
- Fix broken x86_64 builds, provide also required platform mods

* Thu Oct 21 2021 Petr Menšík <pemensik@redhat.com> - 2.78.0-2
- Disable link time optimization, add debug symbols to etlded
- Add etl-launcher, which locates game data in more locations
- Directs how to obtain data if they are not present
- Disable annoying autoupdates

* Fri Oct 15 2021 Petr Menšík <pemensik@redhat.com> - 2.78.0-1
- Update to 2.78.0

* Wed May 19 2021 Petr Menšík <pemensik@redhat.com> - 2.77.1-1
- Update to 2.77.1

* Mon Nov 02 2020 Petr Menšík <pemensik@redhat.com> - 2.76-2.20201102git886f0ef0
- Update to more recent commit

* Mon Oct 26 2020 Petr Menšík <pemensik@redhat.com>
- initial package build
