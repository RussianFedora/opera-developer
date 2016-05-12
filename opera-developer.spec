%global build_for_x86_64 1
%global build_for_i386 1
%global build_from_rpm 1
%define debug_package %{nil}

Summary:        Fast and secure web browser (Developer stream)
Summary(ru):    Быстрый и безопасный Веб-браузер (разрабатываемая версия)
Name:           opera-developer
Version:    39.0.2226.0
Release:    1%{dist}
Epoch:      5

Group:      Applications/Internet
License:    Proprietary
URL:        http://www.opera.com/browser

%if 0%{?build_for_x86_64}
%if 0%{?build_from_rpm}
Source0:    ftp://ftp.opera.com/pub/%{name}/%{version}/linux/%{name}_%{version}_amd64.rpm
%else
Source0:    ftp://ftp.opera.com/pub/%{name}/%{version}/linux/%{name}_%{version}_amd64.deb
%endif
%endif

%if 0%{?build_for_i386}
%if 0%{?build_from_rpm}
Source1:    ftp://ftp.opera.com/pub/%{name}/%{version}/linux/%{name}_%{version}_i386.rpm
%else
Source1:    ftp://ftp.opera.com/pub/%{name}/%{version}/linux/%{name}_%{version}_i386.deb
%endif
%endif

Source2:    rfremix-%{name}.appdata.xml

BuildRequires:  desktop-file-utils

%if 0%{?fedora} >= 20
BuildRequires:  libappstream-glib
%endif

# BuildRequires:  chrpath

# Provides:   libcrypto.so.1.0.0()(64bit)
# Provides:   libcrypto.so.1.0.0(OPENSSL_1.0.0)(64bit)
# Provides:   libudev.so.0()(64bit)
%ifarch x86_64
Provides:   libssl.so.1.0.0()(64bit)
Provides:   libssl.so.1.0.0(OPENSSL_1.0.0)(64bit)
Provides:   libssl.so.1.0.0(OPENSSL_1.0.1)(64bit)
Provides:   libffmpeg.so()(64bit)
%else
Provides:   libssl.so.1.0.0
Provides:   libssl.so.1.0.0(OPENSSL_1.0.0)
Provides:   libssl.so.1.0.0(OPENSSL_1.0.1)
Provides:   libffmpeg.so
%endif

%if 0%{?build_for_x86_64}
%if !0%{?build_for_i386}
ExclusiveArch:    x86_64
%else
ExclusiveArch:    x86_64 i686
%endif
%else
%if 0%{?build_for_i386}
ExclusiveArch:    i686
%endif
%endif

%description
Opera is a fast, secure and user-friendly web browser. It
includes web developer tools, news aggregation, and the ability
to compress data via Opera Turbo on congested networks.

%description -l ru
Opera — это быстрый, безопасный и дружественный к пользователю
веб-браузер. Он включает средства веб-разработки и сбора новостей,
а также возможность сжимать трафик в перегруженных сетях
посредством технологии Opera Turbo.

%prep
%setup -q -c -T

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}

# Extract DEB/RPM packages:
pushd %{buildroot}
    %ifarch x86_64
        %if 0%{?build_from_rpm}
            rpm2cpio %{SOURCE0} | cpio -idV --quiet
        %else
            ar p %{SOURCE0} data.tar.xz | xz -d > %{name}-%{version}.x86_64.tar
            tar -xf %{name}-%{version}.x86_64.tar
        %endif
    %else
        %if 0%{?build_from_rpm}
            rpm2cpio %{SOURCE1} | cpio -idV --quiet
        %else
            ar p %{SOURCE1} data.tar.xz | xz -d > %{name}-%{version}.i386.tar
            tar -xf %{name}-%{version}.i386.tar
        %endif
    %endif
popd

# Move /usr/lib/%{arch}-linux-gnu/%{name} to %{_libdir} (for DEB source):
%if !0%{?build_from_rpm}
    %ifarch x86_64
        mv %{buildroot}/usr/lib/x86_64-linux-gnu/%{name} %{buildroot}/usr/lib/
        rm -rf %{buildroot}/usr/lib/x86_64-linux-gnu
        mv %{buildroot}/usr/lib %{buildroot}%{_libdir}
    %else
        mv %{buildroot}%{_libdir}/i386-linux-gnu/%{name} %{buildroot}%{_libdir}
        rm -rf %{buildroot}%{_libdir}/i386-linux-gnu
    %endif
%endif

# Modify DOC directory, *.desktop file and ffmpeg_preload_config.json:
if [ -d %{buildroot}%{_datadir}/doc/%{name}/ ]; then
    mv %{buildroot}%{_datadir}/doc/%{name} %{buildroot}%{_datadir}/doc/%{name}-%{version}
else
    mkdir -p %{buildroot}%{_datadir}/doc/%{name}-%{version}
fi
sed -e 's/TargetEnvironment=Unity/#TargetEnvironment=Unity/g' -i %{buildroot}%{_datadir}/applications/%{name}.desktop
sed -e 's|/usr/lib/chromium-browser/libs|%{_libdir}/%{name}/lib_extra|g' -i %{buildroot}%{_libdir}/%{name}/resources/ffmpeg_preload_config.json

# Install *.desktop file:
desktop-file-install --vendor rfremix \
  --dir %{buildroot}%{_datadir}/applications \
  --add-category Network \
  --add-category WebBrowser \
  --delete-original \
  %{buildroot}%{_datadir}/applications/%{name}.desktop

# Create necessary symbolic link
mkdir -p %{buildroot}%{_libdir}/%{name}/lib
pushd %{buildroot}%{_libdir}/%{name}/lib
#   ln -s ../../libudev.so.1 libudev.so.0
#   ln -s %{_libdir}/libcrypto.so.10 libcrypto.so.1.0.0
    ln -s %{_libdir}/libssl.so.10 libssl.so.1.0.0
popd

# Fix symlink (for DEB source):
%if !0%{?build_from_rpm}
    pushd %{buildroot}%{_bindir}
        rm %{name}
        %ifarch x86_64
            ln -s ../lib64/%{name}/%{name} %{name}
        %else
            ln -s ../lib/%{name}/%{name} %{name}
        %endif
    popd
%endif

# Fix <opera_sandbox> attributes:
chmod 4755 %{buildroot}%{_libdir}/%{name}/opera_sandbox

# Make binaries executable:
pushd %{buildroot}%{_libdir}/%{name}
    chmod +x opera-developer opera_autoupdate opera_crashreporter
popd

# Remove unused directories and tarball (for DEB source):
%if !0%{?build_from_rpm}
    pushd %{buildroot}
        %ifarch x86_64
            rm %{name}-%{version}.x86_64.tar
        %else
            rm %{name}-%{version}.i386.tar
        %endif
        rm -rf %{buildroot}%{_datadir}/lintian
        rm -rf %{buildroot}%{_datadir}/menu
    popd
%endif

## Remove rpath
# find %{buildroot} -name "opera_autoupdate" -exec chrpath --delete {} \; 2>/dev/null
# find %{buildroot} -name "opera_crashreporter" -exec chrpath --delete {} \; 2>/dev/null

# Install appstream data
%if 0%{?fedora} >= 20
    mkdir -p %{buildroot}%{_datadir}/appdata
    install -pm 644 %{SOURCE2} %{buildroot}%{_datadir}/appdata/rfremix-%{name}.appdata.xml

%check
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/rfremix-%{name}.appdata.xml
%endif

%post
update-desktop-database &> /dev/null || :
touch --no-create /usr/share/icons/hicolor &>/dev/null || :
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache --quiet /usr/share/icons/hicolor || :
fi

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create /usr/share/icons/hicolor &>/dev/null
    gtk-update-icon-cache /usr/share/icons/hicolor &>/dev/null || :
fi
update-desktop-database &> /dev/null || :

%posttrans
gtk-update-icon-cache /usr/share/icons/hicolor &>/dev/null || :

%clean
rm -rf %{buildroot}

%files
%{_defaultdocdir}/%{name}-%{version}
%{_bindir}/%{name}
%{_libdir}/%{name}/*
%{_datadir}/applications/*.desktop
%{_datadir}/icons/*
%{_datadir}/mime/packages/*
%{_datadir}/pixmaps/*
%if 0%{?fedora} >= 20
%{_datadir}/appdata/rfremix-%{name}.appdata.xml
%endif

%changelog
* Thu May 12 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:39.0.2226.0-1
- Update to 39.0.2226.0

* Fri Apr 29 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:38.0.2213.0-1
- Update to 38.0.2213.0

* Thu Apr 21 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:38.0.2205.0-1
- Update to 38.0.2205.0

* Thu Apr 14 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:38.0.2198.0-1
- Update to 38.0.2198.0

* Wed Apr 06 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:38.0.2190.0-1
- Update to 38.0.2190.0

* Sun Mar 20 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:37.0.2171.0-1
- Update to 37.0.2171.0

* Fri Mar 11 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:37.0.2163.0-1
- Update to 37.0.2163.0

* Wed Mar 09 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:37.0.2157.0-4
- Move libffmpeg.so search path into */lib_extra/ instead */lib/

* Fri Mar 04 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:37.0.2157.0-3
- Fix making binaries executable

* Fri Mar 04 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:37.0.2157.0-2
- Make binaries executable

* Thu Mar 03 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:37.0.2157.0-1
- Update to 37.0.2157.0

* Wed Feb 17 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:37.0.2142.0-1
- Update to 37.0.2142.0

* Thu Feb 04 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:36.0.2129.0-1
- Update to 36.0.2129.0

* Sat Jan 30 2016 carasin.berlogue <carasin DOT berlogue AT mail DOT ru> - 5:36.0.2120.0-1
- Update to 36.0.2120.0
- Revert changes of 5:36.0.2106.0-2 build

* Wed Jan 20 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:36.0.2106.0-3
- Fix ffmpeg_preload_config.json

* Wed Jan 20 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:36.0.2106.0-2
- Add Requires: chromium-libffmpeg & Obsoletes: %{name}-libffmpeg

* Wed Jan 13 2016 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:36.0.2106.0-1
- Update to 36.0.2106.0

* Mon Dec 21 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:36.0.2079.0-1
- Update to 36.0.2079.0

* Sat Dec 12 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:36.0.2072.0-1
- Update to 36.0.2072.0

* Thu Dec 03 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:35.0.2064.0-1
- Update to 35.0.2064.0

* Fri Nov 27 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:35.0.2060.0-1
- Update to 35.0.2060.0

* Tue Nov 24 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:35.0.2052.0-1
- Update to 35.0.2052.0
- Add switchers for RPM / DEB source packages

* Thu Nov 12 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:34.0.2044.0-1
- Update to 34.0.2044.0

* Fri Nov 06 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:34.0.2036.2-1
- Update to 34.0.2036.2

* Tue Oct 27 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:34.0.2026.0-1
- Update to 34.0.2026.0

* Tue Oct 20 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:34.0.2023.0-1
- Update to 34.0.2023.0

* Fri Oct 09 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:34.0.2011.0-2
- Add %{_datadir}/mime/packages/opera-developer.xml into <%files> section

* Fri Oct 09 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:34.0.2011.0-1
- Update to 34.0.2011.0

* Wed Sep 23 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:34.0.1996.0-1
- Update to 34.0.1996.0

* Thu Sep 10 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:33.0.1982.0-1
- Update to 33.0.1982.0

* Mon Aug 31 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:33.0.1967.0-1
- Update to 33.0.1967.0

* Sat Aug 22 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:33.0.1963.0-1
- Update to 33.0.1963.0

* Sat Aug 08 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:32.0.1933.0-2
- Add Provides: libssl.so.1.0.0
- Fix <provides> section for 32 bit builds

* Wed Jul 22 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:32.0.1933.0-1
- Update to 32.0.1933.0

* Wed Jul 15 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:32.0.1926.0-1
- Update to 32.0.1926.0

* Wed Jul 01 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:32.0.1910.0-1
- Update to 32.0.1910.0

* Thu Jun 18 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:32.0.1899.0-1
- Update to 32.0.1899.0

* Tue May 26 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:31.0.1876.0-1
- Update to 31.0.1876.0

* Sat May 09 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:31.0.1857.0-2
- Bump version for Fedora >= 22

* Sat May 09 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:31.0.1857.0-1
- Update to 31.0.1857.0

* Wed Apr 15 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:30.0.1835.6-1
- Update to 30.0.1835.6

* Wed Apr 15 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:30.0.1833.0-1
- Update to 30.0.1833.0
- Add i386 support
- Add switchers for x86_64 / i386 packages

* Sat Apr 04 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:30.0.1820.0-1
- Update to 30.0.1820.0

* Tue Mar 24 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:30.0.1812.0-1
- Update to 30.0.1812.0

* Tue Mar 17 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1795.14-1
- Update to 29.0.1795.14

* Wed Mar 11 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1795.0-1
- Update to 29.0.1795.0

* Fri Mar 06 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1794.0-1
- Update to 29.0.1794.0

* Sat Feb 28 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1788.0-1
- Update to 29.0.1788.0

* Thu Feb 26 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1785.0-1
- Update to 29.0.1785.0

* Sat Feb 21 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1781.0-1
- Update to 29.0.1781.0

* Wed Feb 18 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1778.0-1
- Update to 29.0.1778.0

* Fri Feb 13 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1773.0-1
- Update to 29.0.1773.0

* Tue Feb 10 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:29.0.1770.1-1
- Update to 29.0.1770.1

* Tue Feb 03 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1750.11-1
- Update to 28.0.1750.11

* Wed Jan 28 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1750.5-1
- Update to 28.0.1750.5

* Tue Jan 20 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1747.0-1
- Update to 28.0.1747.0

* Fri Jan 16 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1745.0-1
- Update to 28.0.1745.0

* Fri Jan 09 2015 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1738.0-1
- Update to 28.0.1738.0

* Mon Dec 29 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1719.0-4.1
- Remove <icon>, <categories> and <architectures> sections from *.appdata.xml

* Sun Dec 28 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1719.0-4
- Fixed <files> section
- Remove RHEL >=8 condition
- Add <check> section

* Sat Dec 27 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1719.0-3
- Add *.appdata.xml for Fedora >=20 and RHEL >=8
- Remove category X-Fedora from *.desktop file

* Tue Dec 23 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1719.0-2
- Remove libcrypto.so and libudev.so symlinks:
  http://ruario.ghost.io/2014/12/19/installing-opera-on-distributions-other-than-debian-ubuntu-or-derivatives/#comment-1751015398
- Remove chrpath action:
  http://ruario.ghost.io/2014/12/15/opera-packages-for-fedora-with-updates/#comment-1755224247

* Sat Dec 20 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:28.0.1719.0-1
- Update to 28.0.1719.0
- Clean up spec file

* Wed Dec 10 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:27.0.1689.22-2
- Add BR: chrpath

* Fri Dec 05 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:27.0.1689.22-1
- Update to 26.0.1689.22
- Remove wrapper scripts for opera_autoupdate and opera_crashreporter binaries
- Remove bundled libs from Ubuntu 12.04

* Tue Dec 02 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:27.0.1689.13-1
- Update to 27.0.1689.13

* Thu Nov 20 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:27.0.1689.2-1
- Update to 27.0.1689.2

* Thu Nov 20 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:27.0.1689.0-1
- Update to 27.0.1689.0

* Thu Nov 13 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:27.0.1683.0-1
- Update to 27.0.1683.0

* Fri Nov 07 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:27.0.1676.0-1
- Update to 27.0.1676.0

* Fri Oct 31 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:27.0.1670.0-1
- Update to 27.0.1670.0

* Fri Oct 24 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:26.0.1656.5-1
- Update to 26.0.1656.5

* Thu Oct 16 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:26.0.1655.0-1
- Update to 26.0.1655.0

* Tue Oct 07 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:26.0.1646.0-1
- Update to 26.0.1646.0
- Update bundled libssl from Ubuntu 12.04 to 1.0.0_1.0.1-4ubuntu5.18

* Wed Sep 24 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:26.0.1632.0-1
- Update to 26.0.1632.0
- Rename *.spec file to <opera-developer.spec>

* Sat Sep 13 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:25.0.1614.5-1
- Update to 25.0.1614.5

* Fri Sep 05 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:25.0.1613.1-1
- Update to 25.0.1613.1

* Thu Sep 04 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:25.0.1606.0-1
- Update to 25.0.1606.0
- Fix paths at wrapper scripts for opera_autoupdate and opera_crashreporter
- Remove --force-native-window-frame=false from EXEC string at *.desktop file

* Wed Aug 20 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:25.0.1597.0-1
- Update to 25.0.1597.0

* Sun Aug 17 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:25.0.1592.0-1
- Update to 25.0.1592.0

* Tue Aug 12 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:25.0.1583.1-2
- Update bundled libssl from Ubuntu 12.04 to 1.0.0_1.0.1-4ubuntu5.17
- Clean up spec file

* Fri Aug 08 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:25.0.1583.1-1
- Update to 25.0.1583.1
- Move /usr/lib/x86_64-linux-gnu/%{name} to %{_libdir}
- Clean up spec file

* Mon Aug 04 2014 Vasiliy N. Glazov <vascom2@gmail.com> - 5:24.0.1558.21-3
- Remove BR: dpkg

* Tue Jul 29 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:24.0.1558.21-2
- Hot fix: application icon does not appear in the KDE menu

* Tue Jul 29 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:24.0.1558.21-1
- Update to 24.0.1558.21
- Add --force-native-window-frame=false to EXEC string at *.desktop file

* Fri Jul 25 2014 Vasiliy N. Glazov <vascom2@gmail.com> - 5:24.0.1558.17-1
- Update to 24.0.1558.17

* Thu Jul 17 2014 Vasiliy N. Glazov <vascom2@gmail.com> - 5:24.0.1558.3-1
- Update to 24.0.1558.3
- Correct build arch

* Fri Jun 27 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:24.0.1555.0-1
- Update to 24.0.1555.0
- Remove bundled libudev.so.0 from Ubuntu 12.04
- Add wrapper scripts for opera_autoupdate and opera_crashreporter binaries
- Clean up spec file

* Fri Jun 27 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:24.0.1543.0-1
- Update to 24.0.1543.0

* Fri Jun 27 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:24.0.1537.0-3
- Fix bundled dependencies on libs from Ubuntu 12.04

* Tue Jun 24 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:24.0.1537.0-2
- Apply libs from Ubuntu 12.04

* Mon Jun 23 2014 carasin berlogue <carasin DOT berlogue AT mail DOT ru> - 5:24.0.1537.0-1
- Update to 24.0.1537.0

* Mon Jul 29 2013 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.16-1.R
- Update to 12.16

* Tue May 07 2013 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.15-1.R
- Update to 12.15

* Fri Feb 15 2013 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.14-2.R
- exclude badlinked opera_autoupdatechecker

* Thu Feb 14 2013 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.14-1.R
- Update to 12.14

* Tue Nov 20 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.12-1.R
- Update to 12.12

* Tue Nov 20 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.11-1.R
- Update to 12.11

* Tue Nov 06 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.10-1.R
- Update to 12.10

* Fri Aug 31 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.02-1.R
- Update to 12.02

* Thu Jun 14 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.00-2.R
- Corrected spec for EL6

* Thu Jun 14 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:12.00-1.R
- Update to 12.00

* Thu May 10 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:11.64-1.R
- Update to 11.64

* Tue Mar 27 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:11.62-1.R
- Update to 11.62

* Tue Jan 24 2012 Vasiliy N. Glazov <vascom2@gmail.com> - 5:11.61-1.R
- Added description in russian language
- Update to 11.61

* Wed Dec 07 2011 Vasiliy N. Glazov <vascom2@gmail.com> - 5:11.60-1.R
- Added description in russian language
- Update to 11.60

* Wed Oct 19 2011 Vasiliy N. Glazov <vascom2@gmail.com> - 5:11.52-1.R
- update to 11.52

* Thu Sep 01 2011 Vasiliy N. Glazov <vascom2@gmail.com> - 5:11.51-1.R
- update to 11.51

* Mon Jun 27 2011 Arkady L. Shane <ashejn@yandex-team.ru> - 5:11.50-1.R
- update to 11.50

* Tue Apr 12 2011 Arkady L. Shane <ashejn@yandex-team.ru> - 5:11.10-2
- fix license window

* Tue Apr 12 2011 Arkady L. Shane <ashejn@yandex-team.ru> - 5:11.10-1
- update to 11.10

* Thu Jan 27 2011 Arkady L. Shane <ashejn@yandex-team.ru> - 5:11.01-1
- update to 11.01

* Thu Dec 16 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 5:11.00-1
- update to 11.00

* Tue Oct 12 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 5:10.63-2
- put 32bit binary to separate package

* Tue Oct 12 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 10.63-1
- update to 10.63

* Mon Sep 20 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 10.62-1
- update to 10.62

* Fri Aug 13 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 10.61-1
- update to 10.61

* Thu Jul  1 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 10.60-1
- update to 10.60

* Wed Jun 30 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 10.11-1
- update to 10.11

* Tue Jun  1 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 10.10-1
- update to 10.10

* Wed Oct 28 2009 Arkady L. Shane <ashejn@yandex-team.ru> - 10.01-1
- update to 10.01

* Tue Sep 15 2009 Arkady L. Shane <ashejn@yandex-team.ru> - 10.00-2
- qt4 version

* Mon Sep  7 2009 Arkady L. Shane <ashejn@yandex-team.ru> - 10.00-1
- update to final 10.00

* Fri Jul 17 2009 Arkady L. Shane <ashejn@yandex-team.ru> - 10.00-0.3.beta2
- update to beta2

* Wed Jun 24 2009 Arkady L. Shane <ashejn@yandex-team.ru> - 10.00-0.2.beta1
- we had problem for F11 i586 arch in spec file. Fixed now.

* Wed Jun  3 2009 Arkady L. Shane <ashejn@yandex-team.ru> - 10.00-0.1.beta1
- update to 10.00 beta 1

* Wed Mar  4 2009 Arkady L. Shane <ashejn@yandex-team.ru> - 9.64-1
- update to 9.64

* Tue Dec 16 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.63-1
- update to 9.63

* Thu Oct 30 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.62-1
- update to 9.62

* Tue Oct 21 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.61-1
- update to 9.61

* Wed Oct  8 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.60-1
- update to 9.60

* Mon Aug 25 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.52-1
- update to 9.52

* Fri Jul  4 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.51-1
- update to 9.51

* Fri Jun 13 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.50-1
- final 9.50

* Thu Jun 12 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.50-0.2034
- update to RC

* Wed May 21 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.50b2-0.1
- add opera.desktop file

* Mon Apr 28 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.50b2-0
- update to 9.50b2

* Thu Apr  3 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.27-1
- 9.27

* Wed Feb 20 2008 Arkady L. Shane <ashejn@yandex-team.ru> - 9.26-1
- 9.26

* Thu Dec 20 2007 Arkady L. Shane <ashejn@yandex-team.ru> - 9.25-1
- 9.25

* Thu Aug 16 2007 Arkady L. Shane <ashejn@yandex-team.ru> - 9.23-1
- 9.23

* Thu Jul 19 2007 Arkady L. Shane <ashejn@yandex-team.ru> - 9.22-1
- 9.22

* Wed Jun 20 2007 Arkady L. Shane <ashejn@yandex-team.ru> - 9.21-2
- add R for qt 3

* Thu May 17 2007 Arkady L. Shane <ashejn@yandex-team.ru> - 9.21-1
- 9.21

* Thu Apr 12 2007 Arkady L. Shane <ashejn@yandex-team.ru> - 9.20-0%{?dist}
- 9.20

* Fri Dec 22 2006 Arkady L. Shane <ashejn@yandex-team.ru> - 9.10-0%{?dist}
- 9.10

* Wed Jun 21 2006 Arkady L. Shane <shejn@msiu.ru> - 9.0-1%{?dist}
- rebuilt package with russian langpack
