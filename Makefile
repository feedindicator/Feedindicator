BASH_COMPLETION_DIR=/usr/share/bash-completion/completions/
BIN_DIR=/usr/bin/
DOC_DIR=/usr/share/doc/feedindicator/
MAN_DIR=/usr/share/man/man1/
SHARE_DIR=/usr/share/feedindicator/


all: bin/feedindicator bin/feedindicator.desktop


bin:
	@mkdir bin


build:
	@mkdir build


build/package/DEBIAN: build
	@mkdir -p build/package/DEBIAN


bin/feedindicator: bin
	@echo "#!/usr/bin/env bash\n" > bin/feedindicator
	@echo "cd $(SHARE_DIR)" >> bin/feedindicator
	@echo "python3 -m feedindicator \$$@" >> bin/feedindicator
	@chmod a+x bin/feedindicator


bin/feedindicator.desktop: bin
	@echo "[Desktop Entry]" > bin/feedindicator.desktop
	@echo "Version=2.0.0" >> bin/feedindicator.desktop
	@echo "Type=Application" >> bin/feedindicator.desktop
	@echo "Terminal=false" >> bin/feedindicator.desktop
	@echo "Exec=feedindicator" >> bin/feedindicator.desktop
	@echo "Icon=feedindicator" >> bin/feedindicator.desktop
	@echo "Name=Feedindicator" >> bin/feedindicator.desktop
	@echo "Comment=A RSS feed reader for the indicator area." >> bin/feedindicator.desktop
	@echo "Categories=Internet;Network;" >> bin/feedindicator.desktop
	@chmod a+x bin/feedindicator.desktop


build/package/DEBIAN/md5sums: bin/feedindicator bin/feedindicator.desktop build/copyright build/changelog build/feedindicator.1 build/package/DEBIAN
	@mkdir -m 755 -p build/package$(BASH_COMPLETION_DIR)
	@mkdir -m 755 -p build/package$(BIN_DIR)
	@mkdir -m 755 -p build/package$(DOC_DIR)
	@mkdir -m 755 -p build/package$(MAN_DIR)
	@mkdir -m 755 -p build/package$(SHARE_DIR)
	@find build/package -type d -exec chmod 755 {} \;

	@cp -r bin/feedindicator build/package$(BIN_DIR)
	@chmod 755 build/package$(BIN_DIR)feedindicator
	@cp bin/feedindicator.desktop build/package$(SHARE_DIR)
	@chmod 755 build/package$(SHARE_DIR)feedindicator.desktop
	@cp -r feedindicator build/package$(SHARE_DIR)
	@cp -r icons build/package$(SHARE_DIR)
	@find build/package$(SHARE_DIR) -type f -exec chmod 644 {} \;
	@find build/package$(SHARE_DIR) -type d -exec chmod 755 {} \;
	@cp feedindicator.bash-completion build/package$(BASH_COMPLETION_DIR)
	@chmod 644 build/package$(BASH_COMPLETION_DIR)feedindicator.bash-completion

	@cat build/feedindicator.1 | gzip -n9 > build/package$(MAN_DIR)feedindicator.1.gz
	@chmod 644 build/package$(MAN_DIR)feedindicator.1.gz

	@cat build/changelog | gzip -n9 > build/package$(DOC_DIR)changelog.gz
	@chmod 644 build/package$(DOC_DIR)changelog.gz

	@cp build/copyright build/package$(DOC_DIR)copyright
	@chmod 644 build/package$(DOC_DIR)copyright

	@mkdir -p build/package/DEBIAN
	@md5sum `find build/package -type f -not -path "*DEBIAN*"` > build/md5sums
	@sed -e "s/build\/package\///" build/md5sums > build/package/DEBIAN/md5sums
	@chmod 644 build/package/DEBIAN/md5sums


build/package/DEBIAN/control: build/package/DEBIAN/md5sums
	@echo "Package: feedindicator" > build/package/DEBIAN/control
	@echo "Version: `grep "__version_info__ =" feedindicator/__init__.py | grep -oE "[0-9]+, [0-9]+, [0-9]+" | sed -e "s/, /./g"`" >> build/package/DEBIAN/control
	@echo "Section: web" >> build/package/DEBIAN/control
	@echo "Priority: optional" >> build/package/DEBIAN/control
	@echo "Architecture: all" >> build/package/DEBIAN/control
	@echo "Depends: python3 (>= 3), python3-feedparser, python3-gi, python3-configobj, hicolor-icon-theme, indicator-application, xdg-utils" >> build/package/DEBIAN/control
	@echo "Installed-Size: `du -csk build/package/usr | grep -oE "[0-9]+\stotal" | cut -f 1`" >> build/package/DEBIAN/control
	@echo "Maintainer: Nathanael Philipp <mail@jnphilipp.org>" >> build/package/DEBIAN/control
	@echo "Homepage: https://github.com/jnphilipp/Feedindicator" >> build/package/DEBIAN/control
	@echo "Description: RSS feed updates in the indicator area\n Editable, sortable list of feed URLs.\n Notification popups of new feed items.\n Adjustable update timer." >> build/package/DEBIAN/control


build/package/DEBIAN/postinst: build/package/DEBIAN
	@echo "#!/bin/sh -e" > build/package/DEBIAN/postinst
	@echo "xdg-icon-resource install --theme hicolor --novendor --size 512 $(SHARE_DIR)icons/active.png feedindicator-active" >> build/package/DEBIAN/postinst
	@echo "xdg-icon-resource install --theme hicolor --novendor --size 512 $(SHARE_DIR)icons/attention.png feedindicator-attention" >> build/package/DEBIAN/postinst
	@echo "xdg-icon-resource install --theme hicolor --novendor --size 128 --context apps $(SHARE_DIR)icons/logo-128x128.png feedindicator" >> build/package/DEBIAN/postinst
	@echo "xdg-icon-resource install --theme hicolor --novendor --size 48 --context apps $(SHARE_DIR)icons/logo-48x48.png feedindicator" >> build/package/DEBIAN/postinst
	@echo "xdg-desktop-menu install --novendor $(SHARE_DIR)feedindicator.desktop" >> build/package/DEBIAN/postinst
	@chmod 755 build/package/DEBIAN/postinst


build/package/DEBIAN/prerm: build/package/DEBIAN
	@echo "#!/bin/sh -e" > build/package/DEBIAN/prerm
	@echo "xdg-icon-resource uninstall --theme hicolor --novendor --size 512 feedindicator-active" >> build/package/DEBIAN/prerm
	@echo "xdg-icon-resource uninstall --theme hicolor --novendor --size 512 feedindicator-attention" >> build/package/DEBIAN/prerm
	@echo "xdg-icon-resource uninstall --theme hicolor --novendor --size 128 --context apps feedindicator" >> build/package/DEBIAN/prerm
	@echo "xdg-icon-resource uninstall --theme hicolor --novendor --size 48 --context apps feedindicator" >> build/package/DEBIAN/prerm
	@echo "xdg-desktop-menu uninstall --novendor feedindicator.desktop" >> build/package/DEBIAN/prerm
	@chmod 755 build/package/DEBIAN/prerm


build/copyright: build
	@echo "Upstream-Name: feedindicator\nSource: https://github.com/jnphilipp/Feedindicator\n\nFiles: *\nCopyright: Copyright 2010-2017 Dave Gardner <eunbolt@gmail.com>, Michael Judge <email@clickopen.co.uk>, Nicolas Raoul <nicolas.raoul@gmail.com>, Nathanael Philipp (jnphilipp) <mail@jnphilipp.org>\nLicense: GPL-3+\n This program is free software; you can redistribute it\n and/or modify it under the terms of the GNU General Public\n License as published by the Free Software Foundation; either\n version 3 of the License, or (at your option) any later\n version.\n .\n This program is distributed in the hope that it will be\n useful, but WITHOUT ANY WARRANTY; without even the implied\n warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR\n PURPOSE.  See the GNU General Public License for more\n details.\n .\n You should have received a copy of the GNU General Public\n License along with this package; if not, write to the Free\n Software Foundation, Inc., 51 Franklin St, Fifth Floor,\n Boston, MA  02110-1301 USA\n .\n On Debian systems, the full text of the GNU General Public\n License version 3 can be found in the file\n '/usr/share/common-licenses/GPL-3'." > build/copyright


build/changelog: build
	@git log --oneline --decorate > build/changelog


build/feedindicator.1: build
	@help2man -n "feedindicator - A RSS feed reader for the indicator area." feedindicator > build/feedindicator.1


install: bin/feedindicator bin/feedindicator.desktop build/copyright build/changelog build/feedindicator.1
	@apt install python3 python3-gi python3-feedparser python3-configobj hicolor-icon-theme indicator-application xdg-utils
	@xdg-icon-resource install --theme hicolor --novendor --size 512 icons/active.png feedindicator-active
	@xdg-icon-resource install --theme hicolor --novendor --size 512 icons/attention.png feedindicator-attention
	@xdg-icon-resource install --theme hicolor --novendor --size 128 --context apps icons/logo-128x128.png feedindicator
	@xdg-icon-resource install --theme hicolor --novendor --size 48 --context apps icons/logo-48x48.png feedindicator
	@xdg-desktop-menu install --novendor bin/feedindicator.desktop
	@mkdir -p $(SHARE_DIR)
	@cp -r feedindicator $(SHARE_DIR)
	@install bin/feedindicator $(BIN_DIR)
	@install feedindicator.bash-completion $(BASH_COMPLETION_DIR)
	@cat build/feedindicator.1 | gzip -n9 > $(MAN_DIR)feedindicator.1.gz
	@mkdir -p $(DOC_DIR)
	@cat build/changelog | gzip -n9 > $(DOC_DIR)changelog.gz
	@install build/copyright $(DOC_DIR)copyright
	@echo "feedindicator install completed."


uninstall:
	@rm -r $(SHARE_DIR)
	@rm -r $(DOC_DIR)
	@rm $(BIN_DIR)/feedindicator
	@rm $(BASH_COMPLETION_DIR)feedindicator.bash-completion
	@rm $(MAN_DIR)feedindicator.1.gz
	@xdg-icon-resource uninstall --theme hicolor --novendor --size 512 feedindicator-active
	@xdg-icon-resource uninstall --theme hicolor --novendor --size 512 feedindicator-attention
	@xdg-icon-resource uninstall --theme hicolor --novendor --size 128 --context apps feedindicator
	@xdg-icon-resource uninstall --theme hicolor --novendor --size 48 --context apps feedindicator
	@xdg-desktop-menu uninstall --novendor feedindicator.desktop
	@if [ -f ~/.config/feedindicator/feedindicator.desktop ]; then\
		unlink ~/.config/feedindicator/feedindicator.desktop;\
	fi
	@if [ -d ~/.cache/feedindicator ]; then\
		rm -r ~/.cache/feedindicator;\
	fi
	@if [ -d ~/.config/feedindicator ]; then\
		rm -r ~/.config/feedindicator;\
	fi
	@if [ -d ~/.local/share/feedindicator ]; then\
		rm -r ~/.local/share/feedindicator;\
	fi
	@echo "feedindicator uninstall completed."


deb: build/package/DEBIAN/control build/package/DEBIAN/postinst build/package/DEBIAN/prerm
	fakeroot dpkg-deb -b build/package build/feedindicator.deb
	lintian -Ivi build/feedindicator.deb


clean:
	@rm -rf ./bin
	@rm -rf ./build
	@find . -name __pycache__ -exec rm -rf {} \;
