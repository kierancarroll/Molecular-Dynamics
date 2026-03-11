#!/bin/bash

# Get the absolute path to the directory where the script is located
WORKDIR=$(cd "$(dirname "$0")" && pwd)
cd "$WORKDIR" || exit 1  # Navigate to the script's directory

# Define absolute paths for the parent directory files
PARENT_DIR=$(dirname "$WORKDIR")
NPT_MDP="$PARENT_DIR/eq_umbrella.mdp"
MD_MDP="$PARENT_DIR/md_umbrella.mdp"
CONF_GRO="$PARENT_DIR/conf71.gro"
TOP_FILE="$PARENT_DIR/1vet.top"
INDEX_FILE="$PARENT_DIR/index.ndx"

# Short equilibration
gmx grompp -f "$NPT_MDP" -c "$CONF_GRO" -r "$CONF_GRO" -p "$TOP_FILE" -n "$INDEX_FILE" -o npt71.tpr -maxwarn 1
if [ $? -ne 0 ]; then
    echo "FAIL: grompp equilibration failed" > FAIL
    exit 1
fi

gmx mdrun -deffnm npt71 -nt 1 -v
if [ $? -ne 0 ]; then
    echo "FAIL: mdrun equilibration failed" > FAIL
    exit 1
fi

# Umbrella run
gmx grompp -f "$MD_MDP" -c npt71.gro -r npt71.gro -t npt71.cpt -p "$TOP_FILE" -n "$INDEX_FILE" -o umbrella71.tpr -maxwarn 1
if [ $? -ne 0 ]; then
    echo "FAIL: grompp umbrella failed" > FAIL
    exit 1
fi

gmx mdrun -deffnm umbrella71 -nt 1 -v
if [ $? -ne 0 ]; then
    echo "FAIL: mdrun umbrella failed" > FAIL
    exit 1
fi
