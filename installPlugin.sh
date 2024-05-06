#!/bin/sh
WSPLUGINDIR=~/.local/lib/wireshark/plugins

mkdir ${WSPLUGINDIR} || true
dirTP=$(pwd)
cd ${WSPLUGINDIR}
ln -s ${dirTP}/plugin.lua .
