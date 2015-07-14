#! /usr/bin/env bash
mkdir /var/lib/fmm
useradd -M -U fmm
chown fmm:fmm /var/lib/fmm
chmod 755 /var/lib/fmm
