
def take_input():
    return {
        "output_filename": "/home/poojabe/Desktop/PhD_Research/src_project/ml_lib_char/LiMo/output/NAND2X8/GPr3_main_dataset_NAND2X8.csv",
        "simulator_name": "spectre",
        "design_dir": "/home/poojabe/Desktop/PhD_Research/src_project/ml_lib_char/LiMo/gates/NAND2X8/simulation/schematic/netlist/netlist",
        "results_dir": "/home/poojabe/Desktop/PhD_Research/src_project/ml_lib_char/LiMo/gates/NAND2X8/simulation/schematic",
        "model_file": "/cadence/FOUNDRY/analog/45nm/gpdk045/../models/spectre/gpdk045.scs",
        "stimulus_file": "/home/poojabe/Desktop/PhD_Research/src_project/ml_lib_char/LiMo/gates/NAND2X8/simulation/schematic/netlist/_graphical_stimuli_1.scs",

        "analysis_start": "0",
        "analysis_stop": "21e-9",
        "analysis_step": "0.1e-9",

        "pcorners_list": ["tt", "ss", "ff", "sf", "fs"],

        "pvdd_start": 1.0,
        "pvdd_stop": 1.4,
        "pvdd_step": 0.2,

        "ptemp_start": 25,
        "ptemp_stop": 126,
        "ptemp_step": 125,

        "pload_start": 10e-15,
        "pload_stop": 301e-15,
        "pload_common_ratio": 3,

        "pslew_a_start": 10e-12,
        "pslew_a_stop": 290e-12,
        "pslew_a_common_ratio": 3,

        "pslew_b_start": 10e-12,
        "pslew_b_stop": 290e-12,
        "pslew_b_common_ratio": 3,

        "pskew_b_start": -1000e-12,
        "pskew_b_stop": 1000e-12,
        "pskew_b_step": 50e-12,
   
 }
    
   
