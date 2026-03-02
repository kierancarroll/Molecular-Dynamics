import os
import sys

def read_summary(filename="summary_distances.dat"):
    """Reads the summary.dat file and returns a dictionary {COM_distance: frame_number}."""
    summary = {}
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            frame, com_distance = int(parts[0]), float(parts[1])
            summary[com_distance] = frame
    return summary

def validate_com_distance(user_com, summary):
    """Checks if the given COM distance exists in summary.dat."""
    user_com = float(user_com)
    if user_com in summary:  
        return user_com, summary[user_com]
    else:
        print(f"Error: The COM distance {user_com} is not found in summary.dat.")
        sys.exit(1)

def generate_scripts(com_distance, frame_number, template_file="umbrella_template.sh"):
    """Creates the required directory and generates the frame-XYZ_run-umbrella.sh script."""
    
    # Create the directory
    folder_name = f"COM_{com_distance:.3f}"
    os.makedirs(folder_name, exist_ok=True)

    # Read umbrella_template.sh
    with open(template_file, "r") as file:
        template_content = file.read()

    # Replace all instances of XXX with frame_number
    script_content = template_content.replace("XXX", str(frame_number))

    # Write to new script file
    script_filename = os.path.join(folder_name, f"frame-{frame_number}_run-umbrella.sh")
    with open(script_filename, "w") as file:
        file.write(script_content)

    # Make script executable
    os.chmod(script_filename, 0o755)

    print(f"Script created: {script_filename}")

def main():
    """Main function to handle user input and script generation."""
    
    if len(sys.argv) != 2:
        print("Usage: python generate_umbrella_scripts.py COM_distance")
        sys.exit(1)

    user_com = sys.argv[1]

    # Read and validate summary.dat
    summary = read_summary()
    com_distance, frame_number = validate_com_distance(user_com, summary)

    # Generate scripts
    generate_scripts(com_distance, frame_number)

if __name__ == "__main__":
    main()
