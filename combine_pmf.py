import argparse
import os
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

"""
combine_pmf.py

Author: Arthur Goetzee
Description: This script processes two Umbrella Sampling simulation folders to generate a 
combined PMF plot.

Usage:
    python combine_pmf.py -wt <folder_path> -mut <folder_path> -o <folder_path>
    python combine_pmf.py --wild-type <folder_path> --mutated <folder_path> --output <folder_path>

Arguments:
    -wt, --wild-type  a
    -mut, --mutated   a
    -o, --output      a

Functions and Classes:
    - pars_args(): Parses input arguments

Example:
    python ../combine_pmf.py -wt part3 -mut part4 -o figures/


"""


class XVGData:
    """Atomic container for GROMACS XVG data"""
    def __init__(self, x, y, xlabel="", ylabel="", title="", path=""):
        self.x = x
        self.y = y
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.path = path

    def __repr__(self):
        return f'XVGData for {self.path}'

class UmbrellaData:
    """Container for US window data"""
    def __init__(self, center, position_data, pull_force_data, potential_data, total_energy_data, com_pull_energy_data):
        self.center = center
        self.position_data = position_data
        self.pull_force_data = pull_force_data
        self.com_pull_energy_data = com_pull_energy_data
        self.potential_data = potential_data
        self.total_energy_data = total_energy_data
        self.folder = None

    @property
    def time(self):
        return self.position_data.x

    @property
    def pull_force(self):
        return self.pull_force_data.y

    @property
    def position(self):
        return self.position_data.y

    @property
    def com_pull_energy(self):
        return self.com_pull_energy_data.y

    @property
    def potential_energy(self):
        return self.potential_data.y

    @property
    def total_energy(self):
        return self.total_energy_data.y

    def __repr__(self):
        return f'UmbrellaData for {self.center}'

class UmbrellaSimulation:
    """Container for multiple Umbrella Sampling windows."""
    def __init__(self, base_path):
        self.base_path = base_path
        self.umbrella_windows = []
        self.profile = load_xvg(os.path.join(self.base_path, 'profile.xvg'))
        self.histogram = load_xvg(os.path.join(self.base_path, 'histo.xvg'))

        # Find all folders starting with "COM_"
        window_folders = [f for f in os.listdir(self.base_path) if f.startswith("COM_")]
        window_folders.sort(key=lambda x: float(x.split('_')[-1]))  # Sort numerically by COM value

        for folder in tqdm(window_folders):
            folder_path = os.path.join(self.base_path, folder)
            if os.path.isdir(folder_path):
                try:
                    window = process_US_folder(folder_path)
                    window.folder = folder_path
                    self.umbrella_windows.append(window)
                except FileNotFoundError as e:
                    print(f"Warning: {e}")

    def _plot_and_save(self, x, y, xlabel, ylabel, title, out_path, save, type='plot'):
        """Helper function to plot data and either show or save the figure."""
        plt.figure(figsize=(10, 6), dpi=200)
        if type == 'plot':
            plt.plot(x, y, label=title)
        elif type == 'scatter':
            plt.scatter(x, y, label=title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.legend()
        plt.tight_layout()
        if save:
            plt.savefig(out_path)
            plt.close()
        else:
            plt.show()

    def save_all_plots(self, save=True):
        """For each umbrella window, save individual plots in its folder."""
        for window in self.umbrella_windows:
            folder = window.folder
            if not folder:
                continue

            print(folder)
            # Save Pull Force over Time for this window
            self._plot_and_save(window.time, window.pull_force,
                                 "Time (ps)", "Pulling Force (kJ/mol/nm)",
                                 f"Pull Force Over Time (COM {window.center})",
                                 os.path.join(folder, "pull_force_over_time.png"),
                                 save)
            # Save Position over Time for this window
            self._plot_and_save(window.time, window.position,
                                 "Time (ps)", "COM Separation (nm)",
                                 f"Position Over Time (COM {window.center})",
                                 os.path.join(folder, "position_over_time.png"),
                                 save)
            # Save Total Energy over Time for this window
            self._plot_and_save(window.time, window.total_energy,
                                 "Time (ps)", "Total Energy (kJ/mol)",
                                 f"Total Energy Over Time (COM {window.center})",
                                 os.path.join(folder, "total_energy_over_time.png"),
                                 save)
            # Save Potential Energy over Time for this window
            self._plot_and_save(window.time, window.potential_energy,
                                 "Time (ps)", "Potential Energy (kJ/mol)",
                                 f"Potential Energy Over Time (COM {window.center})",
                                 os.path.join(folder, "potential_energy_over_time.png"),
                                 save)
            # Save COM-Pull Energy over Time for this window
            self._plot_and_save(window.time, window.com_pull_energy,
                                 "Time (ps)", "COM-Pull Energy (kJ/mol)",
                                 f"COM-Pull Energy Over Time (COM {window.center})",
                                 os.path.join(folder, "com_pull_energy_over_time.png"),
                                 save)
            # Save Position vs Potential Energy for this window
            self._plot_and_save(window.position, window.potential_energy,
                                 "Position (nm)", "Potential Energy (kJ/mol)",
                                 f"Position vs Potential Energy (COM {window.center})",
                                 os.path.join(folder, "position_vs_potential.png"),
                                 save, 'scatter')

    def plot_histogram(self, save=True):
        plt.figure(figsize=(10, 6), dpi=200)
        for series in self.histogram.y:
            plt.plot(self.histogram.x, series)
        plt.xlabel('COM Separation (nm)')
        plt.ylabel('Counts')
        plt.title('Umbrella Histograms')
        # plt.legend()
        plt.tight_layout()
        if save:
            plt.savefig(os.path.join(self.base_path, 'histo.png'))
            plt.close()
            print(f'Histogram saved to {os.path.join(self.base_path, "histo.png")}')
        else:
            plt.show()
    

    def plot_profile(self, save=True):
        plt.figure(figsize=(10, 6), dpi=200)
        plt.plot(self.profile.x, self.profile.y)
        plt.xlabel('COM Separation (nm)')
        plt.ylabel('Potential of Mean Force (kJ/mol)')
        plt.title('Potential of Mean Force')
        # plt.legend()
        plt.tight_layout()
        if save:
            plt.savefig(os.path.join(self.base_path, 'profile.png'))
            plt.close()
            print(f'PMF saved to {os.path.join(self.base_path, "profile.png")}')
        else:
            plt.show()

    def plot_all_positions_vs_potential(self, save=True):
        plt.figure(figsize=(10, 6), dpi=200)

        for window in self.umbrella_windows:
            plt.scatter(window.position, window.potential_energy)
        plt.xlabel('COM Separation (nm)')
        plt.ylabel('Potential Energy (kJ/mol)')
        plt.title('Potential of Mean Force')
        # plt.legend()
        plt.tight_layout()
        if save:
            plt.savefig(os.path.join(self.base_path, 'COMvsPotential.png'))
            plt.close()
            print(f'COM distance vs potential energy saved to {os.path.join(self.base_path, "COMvsPotential.png")}')
        else:
            plt.show()

def load_xvg(xvg_path):
    """Instantiates a GROMACS XVG file as XVGData object"""
    x, y = [], []
    metadata = {}

    with open(xvg_path, 'r') as f:
        for line in f:
            if line.startswith('#'): # Comment
                continue
            elif line.startswith('@'): # Metadata
                parts = line.split()
                
                # Labels
                if 'title' in parts:
                    lab = ' '.join(parts[2:]).replace('"', '')
                    metadata['title'] = lab
                elif 'yaxis' in parts and 'label' in parts:
                    lab = ' '.join(parts[3:]).replace('"', '')
                    metadata['ylabel'] = lab
                elif 'xaxis' in parts and 'label' in parts:
                    lab = ' '.join(parts[3:]).replace('"', '')
                    metadata['xlabel'] = lab
                elif '@TYPE' in parts and parts[1] != 'xy':
                    raise TypeError(f"Only xy data is supported, got {parts[1]}.")

        if 'histogram' in metadata['title']:
            data = np.loadtxt(fname=xvg_path, comments=['@', '#']).T
            return XVGData(x=data[0], y=data[1:], xlabel=metadata['xlabel'], ylabel=metadata['ylabel'], title=metadata['title'], path=xvg_path)
        
        else:
            data = np.loadtxt(fname=xvg_path, comments=['@', '#']).T
        
    return XVGData(x=data[0], y=data[1], xlabel=metadata['xlabel'], ylabel=metadata['ylabel'], title=metadata['title'], path=xvg_path)

def process_US_folder(folder_path):
    """Instantiates this window as a UmbrellaData object"""
    center = float(folder_path.split('_')[-1])
    pullx_xvg = None
    pullf_xvg = None
    com_pull_en_xvg = None
    potential_xvg = None
    total_energy_xvg = None


    # Find the XVG files
    files = os.listdir(folder_path)
    for file in files:
        if file.endswith("_pullx.xvg") and "#" not in file:
            pullx_xvg = os.path.join(folder_path, file)
        elif file.endswith("_pullf.xvg") and "#" not in file:
            pullf_xvg = os.path.join(folder_path, file)
        elif file.endswith("com_pull_en.xvg") and "#" not in file:
            com_pull_en_xvg = os.path.join(folder_path, file)
        elif file.endswith("potential.xvg") and "#" not in file:
            potential_xvg = os.path.join(folder_path, file)
        elif file.endswith("total_energy.xvg") and "#" not in file:
            total_energy_xvg = os.path.join(folder_path, file)

    if not pullx_xvg or not pullf_xvg or not com_pull_en_xvg or not potential_xvg or not total_energy_xvg:
        raise FileNotFoundError(f"Missing required files in {folder_path}")
    
    
    # Process them into objects
    pullx = load_xvg(pullx_xvg)
    pullf = load_xvg(pullf_xvg)
    com_pull_eng = load_xvg(com_pull_en_xvg)
    potential = load_xvg(potential_xvg)
    total_energy = load_xvg(total_energy_xvg)

    return UmbrellaData(center = center,
                        position_data = pullx,
                        pull_force_data = pullf,
                        potential_data = com_pull_eng,
                        total_energy_data = potential,
                        com_pull_energy_data = total_energy)




def parse_args():
    parser = argparse.ArgumentParser(
        description="""\tCombine the PMFs into a single plot.
            
    This script processes two Umbrella Sampling simulation folders to generate a 
    combined PMF plot ('CombinedPMF.png')""", formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-wt', '--wild-type',
                        type=str,
                        required=True,
                        help='Path to the US folder for the wild-type protein.')
    
    parser.add_argument('-mut', '--mutated',
                        type=str,
                        required=True,
                        help='Path to the US folder for the mutated protein.')
    
    parser.add_argument('-o', '--output',
                        default=os.getcwd(),
                        type=str,
                        help='Output path for the combined PMF plot. Default: Current working directory')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print(f'Wild type folder: {args.wild_type}')
    print(f'Mutated folder: {args.mutated}')

    print('Loading US data...')
    umb_wt = UmbrellaSimulation(base_path=args.wild_type)
    umb_mut = UmbrellaSimulation(base_path=args.mutated)

    print('Creating plot...')
    plt.figure(figsize=(10, 6), dpi=200)
    plt.plot(umb_wt.profile.x, umb_wt.profile.y, label='Wild type')
    plt.plot(umb_mut.profile.x, umb_mut.profile.y, label='Mutant')

    plt.xlabel('COM Separation (nm)')
    plt.ylabel('Potential of Mean Force (kJ/mol)')
    plt.title('Potential of Mean Force')
    plt.legend()
    plt.tight_layout()

    # Save the figure in the output directory
    output_path = os.path.join(args.output, 'CombinedPMF.png')

    if not os.path.exists(args.output):
        os.mkdir(args.output)
    
    plt.savefig(output_path)
    plt.close()
    print(f"Plot saved to {output_path}")
