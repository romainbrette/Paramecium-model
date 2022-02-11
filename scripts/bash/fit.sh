#!/bin/bash
# Run model fitting with multiple fitting scripts
# Use: fit directory fit_names

folder=$1
shift 1

cd $HOME/Paramecium-model-fitting

for arg in $@
do
    echo "Fitting: $arg"
    # Remove old yaml files
    find "$folder/" -name "$arg.yaml" -delete
    # Run fitting
    python scripts/fitting/$arg.py "$folder"
done
