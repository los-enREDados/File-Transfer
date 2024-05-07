#!/bin/sh
WSPLUGINDIR=${HOME}/.local/lib/wireshark/plugins


mkdir -p ${WSPLUGINDIR} || true
dirTP=$(pwd)
cd ${WSPLUGINDIR}
ln -s ${dirTP}/plugin.lua .
