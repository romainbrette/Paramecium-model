#!/bin/bash
# Get the results by ftp, then unarchive

cd "$HOME/hodgkin/Paramecium/Electrophysiology/Selection - AP model"
rm results_selection.tar.gz

# Download the results file
scp ganglion:/mnt/storage_s1/Paramecium/results_selection.tar.gz .

# Unarchive
tar xzvf results_selection.tar.gz
