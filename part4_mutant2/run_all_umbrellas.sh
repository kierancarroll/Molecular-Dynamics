#!/bin/bash

display_help() {
    cat << EOF
Usage: $0 [options] [--failed-only]

Options:
  -d INPUT_DIR    Specify the directory containing COM_* directories (default: current directory).
  -h, --help      Display this help message and exit.

Flags:
  --failed-only   Only execute scripts in directories containing a FAIL file.

Example:
  $0 -d /path/to/input_directory --failed-only
EOF
    exit 0
}

# Default values
failed_only=false
input_dir="."

# First handle long options
while [[ "$1" == --* ]]; do
    case "$1" in
        --failed-only)
            failed_only=true
            shift
            ;;
        --help)
            display_help
            ;;
        *) break ;;
    esac
done

# Parse short options
while getopts ":d:h" opt; do
    case $opt in
        d) input_dir="$OPTARG" ;;
        h) display_help ;;
        \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
        :)  echo "Option -$OPTARG requires an argument." >&2; exit 1 ;;
    esac
done
shift $((OPTIND - 1))

# Check if GROMACS is sourced
if ! which gmx &>/dev/null; then
    echo "You need to source GROMACS first."
    exit 1
fi

# Change to the input directory
if [ -d "$input_dir" ]; then
    cd "$input_dir" || { echo "Failed to change directory to $input_dir"; exit 1; }
else
    echo "Input directory '$input_dir' does not exist."
    exit 1
fi

# Setup logging: redirect all output to a log file while still displaying it on the terminal
LOGFILE="umbrella_run.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "Starting execution in directory: $(pwd)"
echo "Log file: $LOGFILE"

# Collect all .sh scripts in COM_* directories
scripts=()
for script in COM_*/frame-*_run-umbrella.sh; do
    if [ -f "$script" ]; then
        script_dir=$(dirname "$script")
        fail_file="$script_dir/FAIL"
        
        # If --failed-only is set, check for FAIL file
        if $failed_only && [ ! -f "$fail_file" ]; then
            continue
        fi
        
        scripts+=("$script")
    fi
done

# If no scripts found, exit
if [ ${#scripts[@]} -eq 0 ]; then
    echo "No shell scripts found to execute."
    exit 1
fi

# Print summary of all scripts
echo "The following shell scripts will be executed:"
for s in "${scripts[@]}"; do
    echo " - $s"
done

# Ask for confirmation
read -p "Do you want to execute all these scripts? (y/n): " confirm

if [[ "$confirm" =~ ^[Yy]$ ]]; then
    # Execute each script with logging
    for script in "${scripts[@]}"; do
        script_dir=$(dirname "$script")  # Extract the directory path
        
        # Extract the frame number (XXX) from the filename
        frame_number=$(echo "$script" | grep -oP 'frame-\K[0-9]+')
        
        # Define the log file name as frame-XXX.log
        log_file="$script_dir/frame-${frame_number}.log"

        echo "Running $script... (Logging to $log_file)"
        
        # Execute the script and log both stdout and stderr
        bash "$script" > "$log_file" 2>&1

        # Check for execution success or failure
        if [ $? -ne 0 ]; then
            echo "Execution of $script failed. Check $log_file for details."
        else
            echo "Execution of $script completed successfully."
            
            # Remove the FAIL file if execution was successful
            fail_file="$script_dir/FAIL"
            if [ -f "$fail_file" ]; then
                rm "$fail_file"
                echo "Removed FAIL file from $script_dir."
            fi
        fi
    done
    echo "All scripts executed."
else
    echo "Execution canceled by the user."
    exit 0
fi
