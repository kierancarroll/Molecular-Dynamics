#!/bin/bash

# Get the absolute path to the directory where the script is located
WORKDIR=$(cd "$(dirname "$0")" && pwd)
cd "$WORKDIR" || exit 1  # Navigate to the script's directory

# Define absolute paths for the parent directory files
PARENT_DIR=$(dirname "$WORKDIR")
NPT_MDP="$PARENT_DIR/eq_umbrella.mdp"
MD_MDP="$PARENT_DIR/md_umbrella.mdp"
CONF_GRO="$PARENT_DIR/conf188.gro"
TOP_FILE="$PARENT_DIR/1vet.top"
INDEX_FILE="$PARENT_DIR/index.ndx"

# Short equilibration
gmx grompp -f "$NPT_MDP" -c "$CONF_GRO" -r "$CONF_GRO" -p "$TOP_FILE" -n "$INDEX_FILE" -o npt188.tpr -maxwarn 1
if [ $? -ne 0 ]; then
    echo "FAIL: grompp equilibration failed" > FAIL
    exit 1
fi

gmx mdrun -deffnm npt188 -nt 1 -v
if [ $? -ne 0 ]; then
    echo "FAIL: mdrun equilibration failed" > FAIL
    exit 1
fi

# Umbrella run
gmx grompp -f "$MD_MDP" -c npt188.gro -r npt188.gro -t npt188.cpt -p "$TOP_FILE" -n "$INDEX_FILE" -o umbrella188.tpr -maxwarn 1
if [ $? -ne 0 ]; then
    echo "FAIL: grompp umbrella failed" > FAIL
    exit 1
fi

gmx mdrun -deffnm umbrella188 -nt 1 -v
if [ $? -ne 0 ]; then
    echo "FAIL: mdrun umbrella failed" > FAIL
    exit 1
fi
