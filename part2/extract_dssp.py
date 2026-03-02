import argparse

def extract_secondary_structure(file_path):
    sec_structure_list = []  
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    header_found = False
    for line in lines:
        if line.startswith("  #"):  # Locate the start of the secondary structure section
            header_found = True
            continue
        if header_found:
            if '!*' in line:  # Skip lines containing the chain separator
                continue
            if len(line) > 16:  # Ensure the line has secondary structure info
                sec_structure = line[16].strip()
                sec_structure_list.append(sec_structure if sec_structure else 'C')  # Replace blank with 'C'
    
    return "".join(sec_structure_list)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract secondary structure from a DSSP file")
    parser.add_argument('input_file', help="Input DSSP file path")
    parser.add_argument('output_file', help="Output file to save the extracted secondary structure")

    args = parser.parse_args()

    # Extract secondary structure from the input file
    sec_structure_sequence = extract_secondary_structure(args.input_file)

    # Print and save the result
    print(f"Extracted Secondary Structure ({len(sec_structure_sequence)} residues):")
    print(sec_structure_sequence)

    # Write the result to the output file
    with open(args.output_file, 'w') as output_file:
        output_file.write(sec_structure_sequence)
    
    print(f"Secondary structure sequence saved to {args.output_file}")

if __name__ == "__main__":
    main()
