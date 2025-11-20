#
# Please submit bugfixes or comments via http://www.trinitydesktop.org/
#

# TDE variables
%define tde_epoch 2
%if "%{?tde_version}" == ""
%define tde_version 14.1.5
%endif
%define tde_pkg kpilot
%define tde_prefix /opt/trinity
%define tde_bindir %{tde_prefix}/bin
%define tde_datadir %{tde_prefix}/share
%define tde_docdir %{tde_datadir}/doc
%define tde_includedir %{tde_prefix}/include
%define tde_libdir %{tde_prefix}/%{_lib}
%define tde_mandir %{tde_datadir}/man
%define tde_tdeappdir %{tde_datadir}/applications/tde
%define tde_tdedocdir %{tde_docdir}/tde
%define tde_tdeincludedir %{tde_includedir}/tde
%define tde_tdelibdir %{tde_libdir}/trinity

%if 0%{?mdkversion}
%undefine __brp_remove_la_files
%define dont_remove_libtool_files 1
%define _disable_rebuild_configure 1
%endif

# fixes error: Empty %files file …/debugsourcefiles.list
%define _debugsource_template %{nil}

%define tarball_name %{tde_pkg}-trinity
%global toolchain %(readlink /usr/bin/cc)


Name:		trinity-%{tde_pkg}
Epoch:		%{tde_epoch}
Version:	0.7
Release:	%{?tde_version}_%{?!preversion:1}%{?preversion:0_%{preversion}}%{?dist}
Summary:	TDE Palm Pilot hot-sync tool
Group:		Applications/Utilities
URL:		http://www.trinitydesktop.org

%if 0%{?suse_version}
License:	GPL-2.0+
%else
License:	GPLv2+
%endif

#Vendor:		Trinity Desktop
#Packager:	Francois Andriot <francois.andriot@free.fr>

Prefix:		%{tde_prefix}

Source0:		https://mirror.ppa.trinitydesktop.org/trinity/releases/R%{tde_version}/main/applications/office/%{tarball_name}-%{tde_version}%{?preversion:~%{preversion}}.tar.xz

BuildRequires:  cmake make
BuildRequires:	trinity-tdelibs-devel >= %{tde_version}
BuildRequires:	trinity-tdebase-devel >= %{tde_version}
BuildRequires:	desktop-file-utils
BuildRequires:	trinity-tdepim-devel >= %{tde_version}
BuildRequires:	gettext

BuildRequires:	trinity-tde-cmake >= %{tde_version}
%if "%{?toolchain}" != "clang"
BuildRequires:	gcc-c++
%endif
BuildRequires:	pkgconfig
BuildRequires:	fdupes

# ACL support
BuildRequires:  pkgconfig(libacl)

# ICAL support
BuildRequires:  pkgconfig(libical)

# IDN support
BuildRequires:	pkgconfig(libidn)

# OPENSSL support
BuildRequires:  pkgconfig(openssl)

# SUSE desktop files utility
%if 0%{?suse_version}
BuildRequires:	update-desktop-files
%endif

%if 0%{?opensuse_bs} && 0%{?suse_version}
# for xdg-menu script
BuildRequires:	brp-check-trinity
%endif

# FLEX
%if 0%{?suse_version} || 0%{?mgaversion}
BuildRequires:	flex
%endif
%if 0%{?rhel} || 0%{?fedora}
BuildRequires:	flex
%if 0%{?rhel} != 5
BuildRequires:	flex-devel
%endif
%endif

# PILOT support
BuildRequires:	pilot-link-devel >= 0.12

BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(ice)
BuildRequires:  pkgconfig(sm)


%description
KPilot is an application that synchronizes your Palm Pilot or similar device
(like the Handspring Visor) with your TDE desktop, much like the Palm HotSync
software does for Windows.  KPilot can back-up and restore your Palm Pilot
and synchronize the built-in applications with their TDE counterparts.


##########

%if 0%{?suse_version} && 0%{?opensuse_bs} == 0
%debug_package
%endif

##########


%prep
%autosetup -n %{tarball_name}-%{tde_version}%{?preversion:~%{preversion}}


%build
unset QTDIR QTINC QTLIB
export PATH="%{tde_bindir}:${PATH}"
export PKG_CONFIG_PATH="%{tde_libdir}/pkgconfig"

if ! rpm -E %%cmake|grep -e 'cd build\|cd ${CMAKE_BUILD_DIR:-build}'; then
  %__mkdir_p build
  cd build
fi

%cmake \
  -DCMAKE_BUILD_TYPE="RelWithDebInfo" \
  -DCMAKE_C_FLAGS="${RPM_OPT_FLAGS}" \
  -DCMAKE_CXX_FLAGS="${RPM_OPT_FLAGS}" \
  -DCMAKE_SKIP_RPATH=OFF \
  -DCMAKE_SKIP_INSTALL_RPATH=OFF \
  -DCMAKE_INSTALL_RPATH="%{tde_libdir}" \
  -DCMAKE_VERBOSE_MAKEFILE=ON \
  \
  -DCMAKE_INSTALL_PREFIX="%{tde_prefix}" \
  -DSHARE_INSTALL_PREFIX="%{tde_datadir}" \
  -DLIB_INSTALL_DIR="%{tde_libdir}" \
  \
  -DWITH_ALL_OPTIONS=ON \
  -DWITH_GCC_VISIBILITY=ON \
  \
  -DBUILD_ALL=ON \
  -DBUILD_DOC=ON \
  -DBUILD_TRANSLATIONS=ON \
  ..

%__make %{?_smp_mflags} || %__make


%install
export PATH="%{tde_bindir}:${PATH}"
%__make install DESTDIR=%{buildroot} -C build

%find_lang %{tde_pkg}

# Unwanted files
%__rm -f %{?buildroot}%{tde_libdir}/libkpilot.so
%__rm -fr %{?buildroot}%{tde_tdeincludedir}/kpilot/ %{?buildroot}%{tde_includedir}/kpilot/ %{?buildroot}%{_includedir}/kpilot/

# Updates applications categories for openSUSE
%if 0%{?suse_version}
%suse_update_desktop_file -r    %{?buildroot}%{tde_tdeappdir}/kpilot.desktop          Utility  PDA SyncUtility X-KDE-Utilities-Peripherals
%suse_update_desktop_file -u -r %{?buildroot}%{tde_tdeappdir}/kpalmdoc.desktop        Utility  PDA X-TDE-Utilities-File
%endif


%files -f %{tde_pkg}.lang
%defattr(-,root,root,-)
%{tde_bindir}/kpalmdoc
%{tde_bindir}/kpilot
%{tde_bindir}/kpilotDaemon
%{tde_libdir}/libkpilot.la
%{tde_libdir}/libkpilot.so.0
%{tde_libdir}/libkpilot.so.0.0.0
%{tde_tdelibdir}/conduit_address.la
%{tde_tdelibdir}/conduit_address.so
%{tde_tdelibdir}/conduit_doc.la
%{tde_tdelibdir}/conduit_doc.so
%{tde_tdelibdir}/conduit_knotes.la
%{tde_tdelibdir}/conduit_knotes.so
%{tde_tdelibdir}/conduit_memofile.la
%{tde_tdelibdir}/conduit_memofile.so
%{tde_tdelibdir}/conduit_notepad.la
%{tde_tdelibdir}/conduit_notepad.so
%{tde_tdelibdir}/conduit_popmail.la
%{tde_tdelibdir}/conduit_popmail.so
%{tde_tdelibdir}/conduit_sysinfo.la
%{tde_tdelibdir}/conduit_sysinfo.so
%{tde_tdelibdir}/conduit_time.la
%{tde_tdelibdir}/conduit_time.so
%{tde_tdelibdir}/conduit_todo.la
%{tde_tdelibdir}/conduit_todo.so
%{tde_tdelibdir}/conduit_vcal.la
%{tde_tdelibdir}/conduit_vcal.so
%{tde_tdelibdir}/kcm_kpilot.la
%{tde_tdelibdir}/kcm_kpilot.so
%{tde_tdeappdir}/kpalmdoc.desktop
%{tde_tdeappdir}/kpilot.desktop
%{tde_tdeappdir}/kpilotdaemon.desktop
%{tde_datadir}/apps/kaddressbook/contacteditorpages/
%{tde_datadir}/apps/tdeconf_update/kpalmdoc.upd
%{tde_datadir}/apps/tdeconf_update/kpilot.upd
%{tde_datadir}/apps/kpilot
%{tde_datadir}/config.kcfg/*.kcfg
%{tde_datadir}/icons/crystalsvg/*/apps/*.png
%{tde_datadir}/icons/hicolor/*/apps/*.png
%{tde_datadir}/services/*.desktop
%{tde_datadir}/servicetypes/kpilotconduit.desktop
%{tde_tdedocdir}/HTML/en/kpilot/

