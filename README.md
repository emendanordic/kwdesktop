# kwdesktop

## Introduction

This utility script allows you to automate the process of using the Klocwork Desktop
command line utility.

The idea is that this script can be integrated as part of a build script so that
developers do not need a deep understanding of all the different Klocwork options
but the setup happens automatically, as part of the build. The developer can then
just use Klocwork.

Note that the installation of the desktop tools is a prerequisite

Klocwork Desktop - https://support.roguewave.com/documentation/klocwork/en/11-x/gettingstartedwithklocworkdesktopforcc/#concept800

## Usage

Simply run the script with --help to see the different options, e.g.

python kwdesktop.py --help

## Python version

Currently developed against python v2.7.x (same as comes packaged with klocwork - *kwpython*)
