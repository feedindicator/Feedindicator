# Generate the Debian package for feedindicator
# Remember to change the version number in skeleton/DEBIAN/control

rm -rf package *.deb
cp -r skeleton package
cd package

# Copy program and icons
mkdir usr/bin
mkdir usr/share/feedindicator
cp ../../feedindicator usr/bin/
cp ../../*.desktop usr/share/feedindicator/
cp ../../*.png usr/share/feedindicator/
cp -r ../../dark/ usr/share/feedindicator/
cp -r ../../light/ usr/share/feedindicator/
cp -r ../../hicolor/ usr/share/feedindicator/

# Calculate MD5 sums
md5sum $(find usr -type f) > DEBIAN/md5sums
chmod 644 DEBIAN/md5sums

# Calculate installed size
INSTALLED_SIZE=`du -ks usr|cut -f 1`
sed -e "s/INSTALLED_SIZE/$INSTALLED_SIZE/" ../skeleton/DEBIAN/control > DEBIAN/control

# Generate Debian package
cd ..
VERSION=`grep "Version" skeleton/DEBIAN/control | sed -e "s/.* //"`
fakeroot dpkg-deb -b package feedindicator_$VERSION.deb

# Check the package
lintian -Ivi feedindicator_$VERSION.deb
