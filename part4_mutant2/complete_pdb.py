# Import the MODELLER module
from modeller import *
from modeller.scripts import complete_pdb
import argparse

# Set up argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="Complete missing atoms in a PDB file using MODELLER.")
    parser.add_argument('input_pdb', help="Input PDB file path")
    parser.add_argument('output_pdb', help="Output PDB file path")
    
    return parser.parse_args()

def main():
    # Parse arguments from the command line
    args = parse_arguments()

    # Initialize the MODELLER environment
    env = environ()
    env.io.atom_files_directory = ['../atom_files']
    env.libs.topology.read(file='$(LIB)/top_heav.lib')
    env.libs.parameters.read(file='$(LIB)/par.lib')

    # Complete missing atoms
    mdl = complete_pdb(env, args.input_pdb)

    # Write out the completed PDB structure to the specified output file
    mdl.write(file=args.output_pdb)

    print(f"Completed PDB saved to {args.output_pdb}")

if __name__ == "__main__":
    main()
