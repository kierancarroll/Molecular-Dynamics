import numpy as np
import argparse

# Function to parse PDB file
def parse_pdb(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

# Function to apply rotation matrix to a point
def apply_rotation(coord, transformation_matrix):
    return np.dot(transformation_matrix, coord)

# Function to extract C-alpha atoms of specific residues from a chain
def get_specific_ca_atoms(pdb_lines, chain_id, residue_numbers):
    ca_atoms = {}
    for line in pdb_lines:
        if line.startswith("ATOM") and line[21] == chain_id and " CA " in line:
            residue_num = int(line[22:26].strip())
            if residue_num in residue_numbers:
                atom_info = {
                    'x': float(line[30:38].strip()),
                    'y': float(line[38:46].strip()),
                    'z': float(line[46:54].strip())
                }
                ca_atoms[residue_num] = atom_info
                if len(ca_atoms) == len(residue_numbers):
                    break
    return ca_atoms

# Function to create the rotation matrix from axis and angle
def rotation_matrix(axis, theta):
    axis = axis / np.linalg.norm(axis)
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    return np.array([[a*a + b*b - c*c - d*d, 2*(b*c - a*d), 2*(b*d + a*c)],
                     [2*(b*c + a*d), a*a + c*c - b*b - d*d, 2*(c*d - a*b)],
                     [2*(b*d - a*c), 2*(c*d + a*b), a*a + d*d - b*b - c*c]])

# Function to update all atom coordinates with rotation
def rotate_structure(pdb_lines, transformation_matrix):
    rotated_pdb_lines = []
    for line in pdb_lines:
        if line.startswith("ATOM"):
            x = float(line[30:38].strip())
            y = float(line[38:46].strip())
            z = float(line[46:54].strip())
            
            # Apply the transformation
            rotated_coord = apply_rotation(np.array([x, y, z]), transformation_matrix)
            
            # Reformat the new coordinates into the original line format
            new_line = (line[:30] + 
                        f"{rotated_coord[0]:8.3f}{rotated_coord[1]:8.3f}{rotated_coord[2]:8.3f}" + 
                        line[54:])
            rotated_pdb_lines.append(new_line)
        else:
            rotated_pdb_lines.append(line)
    return rotated_pdb_lines

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Rotate a PDB structure based on the binding interface plane.")
    parser.add_argument('input_file', help="Input PDB file path")
    parser.add_argument('output_file', help="Output file to save the rotated structure")
    
    args = parser.parse_args()

    # Hardcoded residues for binding interface
    res1 = 69
    res2 = 72
    res3 = 72
    res4 = 55
    residue_numbers = [res1, res2, res3, res4]

    # Load and parse the PDB file
    pdb_lines = parse_pdb(args.input_file)

    # Extract C-alpha atoms of binding interface residues from chain A
    ca_atoms_chain_a = get_specific_ca_atoms(pdb_lines, chain_id='A', residue_numbers=residue_numbers)

    # Get coordinates of residues
    atoms = [np.array([ca_atoms_chain_a[res]['x'], ca_atoms_chain_a[res]['y'], ca_atoms_chain_a[res]['z']]) 
             for res in residue_numbers]
    
    # Calculate the two vectors defining the plane
    vector1 = atoms[0] - atoms[1]
    vector2 = atoms[2] - atoms[3]

    # Calculate the normal vector to the plane (cross product of the two vectors)
    normal_vector = np.cross(vector1, vector2)
    normal_vector_norm = normal_vector / np.linalg.norm(normal_vector)  # Normalize the normal vector

    # The target normal vector for the x,z plane is [0, 1, 0] (aligned with y-axis)
    # We need to rotate the normal vector to align with the y-axis

    # Find the axis of rotation (cross product of the normal vector and the target vector)
    target_vector = np.array([0, 1, 0])
    rotation_axis = np.cross(normal_vector_norm, target_vector)
    rotation_axis_norm = rotation_axis / np.linalg.norm(rotation_axis)

    # Find the angle of rotation (using dot product)
    angle = np.arccos(np.dot(normal_vector_norm, target_vector))

    # Calculate the rotation matrix to align the binding interface plane
    rotation_matrix_binding_groove = rotation_matrix(rotation_axis_norm, angle)

    # Apply the rotation to align the binding interface plane
    aligned_pdb_lines = rotate_structure(pdb_lines, rotation_matrix_binding_groove)

    # Write the final rotated structure to a new PDB file
    with open(args.output_file, 'w') as output_file:
        output_file.writelines(aligned_pdb_lines)

    print(f"Rotation complete. Output saved to {args.output_file}")

if __name__ == "__main__":
    main()
