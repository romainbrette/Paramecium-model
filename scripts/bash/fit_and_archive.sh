#!/bin/bash
# Run model fitting, then create an archive with model fitting results
# Use: fit_and_archive directory fit_names

folder=$1
shift 1

# Pull git repository
cd $HOME/Paramecium-model-fitting
git pull

# Remove the old archive
rm /mnt/storage_s1/Paramecium/results_selection.tar.gz

# Remove old yaml files
for arg in $@
do
    find '/mnt/storage_s1/Paramecium/Electrophysiology/Selection - AP model' -name "$arg.yaml" -delete
done

# Run model fitting
conda activate Paramecium-model-fitting
for arg in $@
do
    echo "Fitting: $arg"
    # Remove old yaml files
    find "$folder/" -name "$arg.yaml" -delete
    # Run fitting
    python scripts/fitting/$arg.py "$folder"
done

# Create the archive
rsync -a --progress --include="*$1.yaml" --include='*/' --exclude='*' '/mnt/storage_s1/Paramecium/Electrophysiology/Selection - AP model/' /mnt/storage_s1/Paramecium/results_selection/
cd /mnt/storage_s1/Paramecium/results_selection
tar czvf ../results_selection.tar.gz .
