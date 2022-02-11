#!/bin/bash
# Create an archive with model fitting results
# Use: make_archive fit_name
# (Make the script executable with chmod 755 and put it in the path, eg /usr/local/bin)

rm /mnt/storage_s1/Paramecium/results_selection.tar.gz
rsync -a --progress --include="*$1.yaml" --include='*/' --exclude='*' '/mnt/storage_s1/Paramecium/Electrophysiology/Selection - AP model/' /mnt/storage_s1/Paramecium/results_selection/
cd /mnt/storage_s1/Paramecium/results_selection
tar czvf ../results_selection.tar.gz .
