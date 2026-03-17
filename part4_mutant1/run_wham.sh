#!/bin/bash

# Help function
display_help() {
    echo "Usage: $0 [-d INPUT_DIR]"
    echo ""
    echo "Extracts energy terms from GROMACS umbrella sampling simulations."
    echo ""
    echo "Options:"
    echo "  -d INPUT_DIR  Specify the directory containing COM_* directories (default: current directory)"
    echo "  -h            Display this help message"
    exit 0
}

# Default values
input_dir="."

# Parse command-line options
while getopts ":d:h" opt; do
    case ${opt} in
        d ) input_dir="$OPTARG" ;;
        h ) display_help ;;
        \? ) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
        : ) echo "Option -$OPTARG requires an argument." >&2; exit 1 ;;
    esac
done

cd "$input_dir" || { echo "Cannot change directory to $input_dir"; exit 1; }


# Check if GROMACS is sourced
if ! which gmx &>/dev/null; then
    echo "You need to source GROMACS first."
    exit 1
fi

# Output files
tpr_output="umbrella_tpr_paths.dat"
pullf_output="umbrella_pullf_paths.dat"

# Clear output files
> "$tpr_output"
> "$pullf_output"

# Iterate over matching directories
for dir in "$input_dir"/COM_*.[0-9][0-9][0-9]; do
    # Check if the directory exists
    if [[ -d "$dir" ]]; then
        echo "Checking folder: $dir"

        # Skip if FAIL file exists
        if [[ -e "$dir/FAIL" ]]; then
            echo "Skipping $dir (contains FAIL)"
            continue
        fi

        # Find the umbrella tpr and pullf files (ignoring backups with '#' in their name)
        tpr_file=$(ls "$dir"/umbrella*.tpr 2>/dev/null | grep -v '#' | head -n 1)
        pullf_file=$(ls "$dir"/umbrella*_pullf.xvg 2>/dev/null | grep -v '#' | head -n 1)

        # Debug output
        if [[ -n "$tpr_file" ]]; then
            echo "Found TPR: $tpr_file"
        else
            echo "No umbrella*.tpr found in $dir"
        fi

        if [[ -n "$pullf_file" ]]; then
            echo "Found PULLF: $pullf_file"
        else
            echo "No umbrella*_pullf.xvg found in $dir"
        fi

        # Run gmx energy for each energy term separately
        if [[ -n "$tpr_file" ]]; then
            edr_file="${tpr_file%.tpr}.edr"

            # COM-Pull-En
            energy_out_com="${tpr_file%.tpr}_com_pull_en.xvg"
            echo "Extracting COM-Pull-En energy..."
            echo COM-Pull-En | gmx energy -s "$tpr_file" -f "$edr_file" -o "$energy_out_com"

            # Potential
            energy_out_pot="${tpr_file%.tpr}_potential.xvg"
            echo "Extracting Potential energy..."
            echo Potential | gmx energy -s "$tpr_file" -f "$edr_file" -o "$energy_out_pot"

            # Total-Energy
            energy_out_tot="${tpr_file%.tpr}_total_energy.xvg"
            echo "Extracting Total-Energy..."
            echo Total-Energy | gmx energy -s "$tpr_file" -f "$edr_file" -o "$energy_out_tot"
        fi

        # Append to output files if both exist
        if [[ -n "$tpr_file" && -n "$pullf_file" ]]; then
            echo "$tpr_file" >> "$tpr_output"
            echo "$pullf_file" >> "$pullf_output"
        fi
    fi
done

echo "Paths saved to $tpr_output and $pullf_output"

gmx wham -it "$tpr_output" -if "$pullf_output" -o profile.xvg -hist histo.xvg -unit kJ -xvg xmgrace -temp 300
