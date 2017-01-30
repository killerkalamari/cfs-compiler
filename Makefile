#=========================================================================
# Makefile
#
# Copyright (C) 2017 Jeffry Johnston <cfs@kidsquid.com>
#
# This file is part of cfs.
#
# cfs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cfs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cfs. If not, see <http://www.gnu.org/licenses/>.
#=========================================================================

.PHONY: all
all:;

.PHONY: install
install:
	install cfs.py /usr/local/bin/cfs
	install -d /usr/local/share/cfs
	install *.cfs /usr/local/share/cfs
