![Status](https://img.shields.io/badge/status-completed-brightgreen)
![Field](https://img.shields.io/badge/field-computational%20biology-blue)

# 🧬 Protein-Protein Interaction PMF using Molecular Dynamics & Umbrella Sampling

This project explores the **binding strength between two proteins** by computing the **Potential of Mean Force (PMF)** using **Molecular Dynamics (MD)** simulations combined with **Umbrella Sampling (US)**.

The workflow follows a full simulation pipeline using **GROMACS**, from system preparation to free energy reconstruction via **WHAM (Weighted Histogram Analysis Method)**.




## Background & Inspiration

Understanding protein-protein interactions is essential for understanding protein function. Therefore, it is a highly important topic in structural biology and drug design. This project was inspired by the paper *“Coarse-grained versus atomistic simulations: realistic interaction free energies for real proteins”* by May et al. (2014). In that work, protein–protein interaction free energies are computed using **constraint force integration**.

In contrast, this project adopts an alternative approach using **umbrella sampling (US)** combined with the **Weighted Histogram Analysis Method (WHAM)** to reconstruct the Potential of Mean Force (PMF). While constraint force integration directly integrates mean forces along a reaction coordinate, umbrella sampling enhances configurational sampling at discrete points and reconstructs the free energy landscape from biased simulations. This provides a complementary perspective on protein binding energetics.

## Project Overview

In this project, we:

- Simulate the separation of two protein chains (PDB: `1VET`)
- Apply **steered molecular dynamics (SMD)** to generate configurations
- Use **umbrella sampling** to explore the free energy landscape
- Reconstruct the **PMF curve** as a function of center of mass (COM) distance between the two chains
- Investigate the **effect of mutations** on binding affinity to probe biological relevance



## Poster

Below is the poster summarizing the project:

![Research Poster](./Research%20Poster.png)


## Methods

### 1. Molecular Dynamics (MD)

We simulate atomic motion by numerically integrating Newton’s equations:

- Force fields model:
  - Bond stretching
  - Angle bending
  - Electrostatics
  - Van der Waals interactions
- System preparation:
  - Protein cleaning & topology generation
  - Solvation & ion addition
  - Energy minimization
  - NVT & NPT equilibration
  - Production MD run


### 2. Steered Molecular Dynamics (SMD)

To observe rare events, like different conformational states along the (un)folding pathway, an external harmonic force is applied: $$ U_{system(x)} = U_{PPI}(x) + U_{harmonic\ potential}(x) $$

- Proteins are pulled apart along a reaction coordinate (COM distance)
- Generates starting configurations for umbrella sampling



### 3. Umbrella Sampling (US)

Umbrella sampling enhances sampling across the reaction coordinate:

- Apply harmonic bias: $$U_{harmonic\ potential}(x) = 0.5 * k * (x - x₀)²$$
- Multiple simulations (windows) at different distances
- Each window samples configurations near a fixed COM distance



### 4. WHAM Analysis

The **Weighted Histogram Analysis Method (WHAM)** combines the biased probability distributions from all umbrella sampling windows and removes the effect of the applied harmonic potentials. It does this by reweighting each histogram according to its bias and solving self-consistently for the unbiased probability distribution across the reaction coordinate.

The unbiased PMF is then obtained from:

$$PMF(x) = -k_B T \ln P(x) + C$$

where P(x) is the reconstructed unbiased probability distribution, k_B is the Boltzmann constant, T the temperature, and C a shifting constant.

Outputs:
- PMF curve (free energy vs COM distance)
- Histogram overlap (sampling quality)



## Results

### PMF Interpretation

A typical PMF curve includes:

- **Initial decreasing slope** → Decreased free energy due to less steric clashes
- **Minimum** → Stable bound state  (most favorable energy state)
- **Rising slope** → Energy required to separate proteins  
- **Plateau** → Fully unbound state  



### Mutation Analysis

To probe biological relevance of the computational techniques two mutations were studied:

#### 1. Evolutionarily Likely Mutation  (high score in BLOSUM62 substition matrix)
- **GLN → GLU (position 59, chain A)**
- Result:
  - Similar binding free energy (~100 kJ/mol)
  - Likely preserves hydrogen bonding
  - → **Minimal impact on binding**

#### 2. Evolutionarily Unlikely Mutation  (low score in BLOSUM62 substition matrix)
- **THR → VAL (position 52, chain A)**
- Result:
  - Reduced binding free energy
  - Loss of hydrogen bonding + unfavorable interactions
  - → **Weaker binding & easier unbinding**


## Repository Structure

```
project-root/
├── part1/                  # Full atomistic MD setup & simulation
├── part2/                  # Coarse-grained MD (Martini) setup & simulation
├── part3/                  # Coarse-grained MD + Umbrella Sampling + WHAM pipeline
├── part4/                  # PMF pipeline for a mutant template
├── part4_mutant1/          # PMF pipeline + results for a mutant 1 (GLN → GLU) 
├── part4_mutant2/          # PMF pipeline + results for a mutant 2 (THR → VAL)
├── gmx_env.sh              # Load environment for GROMACS
├── combine_pmf.py          # Combine pmf curves of wild type and mutant proteins
├── figures/                # PMF plots & histograms
├── Research_Poster.png     # Final poster
└── README.md
```

## How to Run

### Prerequisites

- GROMACS
- Python 3
- Conda environment (`bioinformatics`)
- MARTINI force field files


### Basic Workflow

```bash
# Load environment
conda activate bioinformatics
source gmx_env.sh

# Run MD simulation (see GROMACS documentation for more detail on gmx commands)
gmx grompp ...
gmx mdrun ...

# Steered MD
gmx mdrun -deffnm pull

# Umbrella sampling setup
bash get_distances.sh
python setupUmbrella.py ...

# Run umbrella windows
bash run_all_umbrellas.sh

# WHAM analysis
bash run_wham.sh

# Plot results
python create_plots.py

```

## Key Insights

- Umbrella sampling enables exploration of **rare events** such as protein unbinding  
- Proper **histogram overlap** is critical for accurate PMF reconstruction  
- Molecular dynamics and Umbrella Sampling are accurate computational tools to study protein interactions while ensuring the simulated proteins maintain expected biological behaviour


## References

- [GROMACS Documentation](https://www.gromacs.org/documentation)  
- Kumar et al. (1992) – Weighted Histogram Analysis Method (WHAM)  
- May et al. (2014) – *Coarse-grained versus atomistic simulations: realistic interaction free energies for real proteins*  
- Monticelli et al. (2008) – MARTINI coarse-grained force field  


## Authors

- Kieran Carroll  
- Jonathan Sierks  

