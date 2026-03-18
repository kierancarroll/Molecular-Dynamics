import matplotlib.pyplot as plt
import numpy as np
from sys import argv
import os
from tqdm import tqdm
import argparse

"""
create_plots.py

Author: Arthur Goetzee
Description: This script processes GROMACS-generated XVG files to extract and visualize data from Umbrella 
Sampling simulations. It will create figures in each umbrella window folder for simulation diagnostics, and
the PMF ('profile.png'), histograms ('histo.png') and the COM versus potential energy ('all_position_vs_COMPull.png)
will be generated in the root folder specified by -f or --folder.

Usage:
    python create_plots.py -f <folder_path>
    python create_plots.py --folder <folder_path>

Arguments:
    -f, --folder  Path to the umbrella simulation folder containing the XVG files.
                  (default: current working directory)

Functions and Classes:
    - load_xvg(xvg_path): Loads and processes a GROMACS XVG file into an XVGData object.
    - process_US_folder(folder_path): Processes a umbrella simulation folder and returns an UmbrellaData object.
    - parse_args(): Parses arguments.
    - XVGData: Class for storing individual XVG file data.
    - UmbrellaData: Class for storing XVGData from a single umbrella sampling simulation.
    - UmbrellaSimulation: Class for managing and plotting umbrella sampling data across multiple UmbrellaData objects.

Example:
    python create_plots.py -f /path/to/umbrella_simulation_folder


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
        self.warnings = False
        self.warninglist = []
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
                    print(f"WARNING: {e}")
                    self.warnings = True
                    self.warninglist.append(folder_path)

        if self.warnings == True:
            print("="*5)
            print(f"WARNING: There were problems with processing {len(self.warninglist)} US folder(s):")
            print("\n".join(self.warninglist))
            print("Check the terminal output, folders, XVG files and logfiles for more details.")
            print("="*5)

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
            self._plot_and_save(window.position, window.com_pull_energy,
                                 "Position (nm)", "COM-Pull Energy (kJ/mol)",
                                 f"Position vs COM-Pull Energy (COM {window.center})",
                                 os.path.join(folder, "position_vs_COMPull.png"),
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
            plt.scatter(window.position, window.com_pull_energy)
        plt.xlabel('COM Separation (nm)')
        plt.ylabel('Potential Energy (kJ/mol)')
        plt.title('All Umbrella COM Pull energy vs Distance')
        # plt.legend()
        plt.tight_layout()
        if save:
            plt.savefig(os.path.join(self.base_path, 'all_position_vs_COMPull.png'))
            plt.close()
            print(f'COM distance vs potential energy saved to {os.path.join(self.base_path, "all_position_vs_COMPull.png")}')
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
    files = sorted(os.listdir(folder_path))
    for file in files:
        if file.startswith('umbrella') and file.endswith("_pullx.xvg") and "#" not in file:
            pullx_xvg = os.path.join(folder_path, file)
        elif file.startswith('umbrella') and file.endswith("_pullf.xvg") and "#" not in file:
            pullf_xvg = os.path.join(folder_path, file)
        elif file.startswith('umbrella') and file.endswith("com_pull_en.xvg") and "#" not in file:
            com_pull_en_xvg = os.path.join(folder_path, file)
        elif file.startswith('umbrella') and file.endswith("potential.xvg") and "#" not in file:
            potential_xvg = os.path.join(folder_path, file)
        elif file.startswith('umbrella') and file.endswith("total_energy.xvg") and "#" not in file:
            total_energy_xvg = os.path.join(folder_path, file)

    # In case we cant find files, which ones are missing?
    if not pullx_xvg or not pullf_xvg or not com_pull_en_xvg or not potential_xvg or not total_energy_xvg:
        missing_files = []
        if not pullx_xvg:
            missing_files.append("pullx_xvg")
        if not pullf_xvg:
            missing_files.append("pullf_xvg")
        if not com_pull_en_xvg:
            missing_files.append("com_pull_en_xvg")
        if not potential_xvg:
            missing_files.append("potential_xvg")
        if not total_energy_xvg:
            missing_files.append("total_energy_xvg")
        raise FileNotFoundError(f"The following files are missing: {', '.join(missing_files)}")

    # Process them into objects
    pullx = load_xvg(pullx_xvg)
    pullf = load_xvg(pullf_xvg)
    com_pull_eng = load_xvg(com_pull_en_xvg)
    potential = load_xvg(potential_xvg)
    total_energy = load_xvg(total_energy_xvg)

    return UmbrellaData(center = center,
                        position_data = pullx,
                        pull_force_data = pullf,
                        potential_data = potential,
                        total_energy_data = total_energy,
                        com_pull_energy_data = com_pull_eng)

def parse_args():
    parser = argparse.ArgumentParser(
        description="""\tGenerate plots for an umbrella simulation folder. By Arthur Goetzee.
        
This script processes GROMACS-generated XVG files to extract and visualize data from Umbrella 
Sampling simulations. It will create figures in each umbrella window folder for simulation diagnostics, and
the PMF ('profile.png'), histograms ('histo.png') and the COM versus COM Pull energy ('all_position_vs_COMPull.png)
will be generated in the root folder specified by -f or --folder.""", formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-f", "--folder",
        type=str,
        default=os.getcwd(),
        help="Path to the umbrella simulation folder (default: current working directory)."
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    print(f"Umbrella simulation folder: {args.folder}")

    print('Loading US data...')
    umb = UmbrellaSimulation(base_path=args.folder)
    print("Generating plots for individual US windows...")
    umb.save_all_plots()
    print('Plotting histogram...')
    umb.plot_histogram()
    print('Plotting PMF...')
    umb.plot_profile()
    print('Plotting COM distance vs COM pull energy...')
    umb.plot_all_positions_vs_potential()