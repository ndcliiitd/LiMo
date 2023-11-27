#import required libraries
import subprocess
import numpy as np
import csv
import re
import os
import csv
import time
import sys
import json

######.............................................................................................................................................######
######.............................................................................................................................................######
#ocean script for the simulation of combinational cell and calculating the value of delays
ocean_script = """

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;SET THE ENVIRONMENT;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;Set up the output file
of = outfile(output_file, "w") 

;;Set the simulator to use
simulator(simulator_name)

;;Set the design directory
design(design_dir)

;;Set the results directory
resultsDir(results_dir)

;;Set the stimulus files
stimulusFile(?xlate nil stimulus_file)

;;Write the legend to the output file
fprintf(of," load, slew_a, slew_b, slew_c, process, voltage, temperature, skew_b, skew_c, rise_delay, fall_delay, rise_slew, fall_slew\n") 

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;DEFINE FUNCTION USED IN THE SCRIPT;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;convert string into floating point number
procedure( StrToNum(arg)
    (float (evalstring arg) )
)

;;Define a function for absolute value
(procedure (absolute x) 
    if( (x >= 1e-15) (x=x) (x=-x) ) 
)

;;if anywhere in dataset generataing the nil convert it into number so that subtarction operation can be performed latter on.
(procedure (conv_nil value)
  (cond ((and (listp value) (null value)) 0)
        ((numberp value) value)
        (t value)
  )
)


;simulate at the input values and calculate the delay
(procedure (simulation pcorners pvdd ptemp pload pslew_a pslew_b pslew_c  pskew_b pskew_c)
     
    ;;SET THE MODEL FILES AND PROCESS CORNERS
    modelFile( list(model_file pcorners ) )

    ;; RUN COMMANDS TO DO TRANSIENT ANALYSIS;;Set the analysis options
    analysis('tran ?param "temp"  ?start  analysis_start  ?stop  analysis_stop  ?step  analysis_step)
    option( 'temp ptemp ) 
    save('all)
    run() 

    ;; DATA ACCESS COMMAND TO PROCESS POST-SIMULATION DATA        
    selectResults('tran)    
    ;; Calculate tplh value for current pskew_b                
 
    ;;output rise delay
    if( (pskew_b > 0 && pskew_c > 0) 
        (if (pskew_b < pskew_c) 
             (tplh = delay( v("/C") pvdd/2.0 1 'rising v("/Y")  pvdd/2.0 1 'rising )) 
	     (tplh = delay( v("/B") pvdd/2.0 1 'rising v("/Y")  pvdd/2.0 1 'rising ))

        )     
	(tplh = delay( v("/A") pvdd/2.0 1 'rising v("/Y")  pvdd/2.0 1 'rising )) 
    )
				   

    ;;output fall delay
    if( (pskew_b > 0 && pskew_c > 0)  
	(tphl = delay( v("/A") pvdd/2.0 1 'falling v("/Y")  pvdd/2.0 1 'falling ))
        (if (pskew_b < pskew_c)
             (tphl = delay( v("/B") pvdd/2.0 1 'rising v("/Y")  pvdd/2.0 1 'falling )) 
             (tphl = delay( v("/C") pvdd/2.0 1 'rising v("/Y")  pvdd/2.0 1 'falling ))
        ) 
    )

    ;;output rise slew 
    tr = riseTime( v("/Y" ?result "tran") 0 nil pvdd nil 10 90 nil "time" ) 

    ;;output fall slew
    tf = fallTime( v("/Y" ?result "tran") pvdd nil 0 nil 10 90 nil "time" ) 
)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;INPUT PARAMETERS;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;; This will create a list for process corners
pcorners_1 = list(pcorners_list)

;; This will create a list for voltage 
pvdd_1 = linRg(StrToNum(pvdd_start) StrToNum(pvdd_stop) StrToNum(pvdd_step)) 

;; This will create a list for temperature
ptemp_1 = linRg(StrToNum(ptemp_start) StrToNum(ptemp_stop) StrToNum(ptemp_step)) 

;; This will create a list for output capacitance , pload_1 is paased from the python 
pload_2 = list(StrToNum(pload_1)) 

;;This will create a list for input slew , slew_a_1 is passed from the python 
pslew_a_2 = list(StrToNum(pslew_a_1))  

;;This will create a list for input slew, slew_b_1 is passed from the python 
pslew_b_2 = list(StrToNum(pslew_b_1))

;;This will create a list for input slew, slew_b_1 is passed from the python 
pslew_c_2 = list(StrToNum(pslew_c_1))

;;This will create a list for input skew 
pskew_b_1 = linRg(StrToNum(pskew_b_start) StrToNum(pskew_b_stop) StrToNum(pskew_b_step))

;;This will create a list for input skew 
pskew_c_1 = linRg(StrToNum(pskew_c_start) StrToNum(pskew_c_stop) StrToNum(pskew_c_step))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;RUNNING SIMULATION AND WRITING OUTPUT INTO FILE;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
foreach((pload) pload_2
    desVar("cap", pload)
        
    foreach( (pslew_a) pslew_a_2
        desVar("slew_a", pslew_a)
                
        foreach( (pslew_b) pslew_b_2
            desVar("slew_b", pslew_b)
                        
            foreach( (pslew_c) pslew_c_2
               desVar("slew_c", pslew_c)
                 
               foreach((pcorners) pcorners_1
                   desVar("corners", pcorners)
                                      
                   foreach( (pvdd) pvdd_1
                       desVar("VDD", pvdd)
                                             
                       foreach( (ptemp) ptemp_1
                           desVar("temp", ptemp) 
                                                      
                           foreach(pskew_b pskew_b_1
                               desVar("skew_b", pskew_b)
                               
                               foreach(pskew_c pskew_c_1
                                   desVar("skew_c", pskew_c)
                                   
                                   ;;simulate at the input values and calculate the delay
				   (simulation pcorners pvdd ptemp pslew_a pslew_b pslew_c pload pskew_b pskew_c)
                                                
                                   ;;if anywhere in dataset generataing the nil convert it into number so that subtarction operation can be performed latter on.
                                   (setq tplh (conv_nil tplh))
                                   (setq tphl (conv_nil tphl))                           
                                   (setq tr (conv_nil tr))
                                   (setq tf (conv_nil tf))

                                                                                                                     
                                   ;; write the value in input_file for python and outuput file for ocean script(dataset.csv)                        
                                   newline(of)
                                   fprintf( of "%e,%e,%e,%e,%s,%f,%L,%L,%L,%L,%L,%L,%L\n", pload, pslew_a, pslew_b, pslew_c, pcorners, pvdd, ptemp, pskew_b, pskew_c, tplh, tphl, tr, tf)                                  
                                ) 
                            )
                        ) 
	            )
                )
            ) 
        )
    )
) 


close(of)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;COMPLETED SCRIPT;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

"""

#copied the ocean script into another variable ocean_script_1
ocean_script_1 = ocean_script

######.............................................................................................................................................######
# Set the working directory to the directory of this script
os.chdir(os.path.dirname(__file__))
# Load the input values from the JSON file
with open('input.json', 'r') as f:
    input_values = json.load(f)

# Extract input values
# Extract input values
interim_output_file = "interim/interim_dataset_none.csv"

simulator_name = input_values["simulator_name"]
design_dir = input_values["design_dir"]
results_dir = input_values["results_dir"]
model_file = input_values["model_file"]
stimulus_file = input_values["stimulus_file"]
analysis_start = input_values["analysis_start"]
analysis_stop = input_values["analysis_stop"]
analysis_step = input_values["analysis_step"]
pcorners_list = input_values["pcorners_list"]
pvdd_start = input_values["pvdd_start"]
pvdd_stop = input_values["pvdd_stop"]
pvdd_step = input_values["pvdd_step"]
ptemp_start = input_values["ptemp_start"]
ptemp_stop = input_values["ptemp_stop"]
ptemp_step = input_values["ptemp_step"]
pload_start = input_values["pload_start"]
pload_stop = input_values["pload_stop"]
pload_common_ratio = input_values["pload_common_ratio"]
pslew_a_start = input_values["pslew_a_start"]
pslew_a_stop = input_values["pslew_a_stop"]
pslew_a_common_ratio = input_values["pslew_a_common_ratio"]
pslew_b_start = input_values["pslew_b_start"]
pslew_b_stop = input_values["pslew_b_stop"]
pslew_b_common_ratio = input_values["pslew_b_common_ratio"]
pslew_c_start = input_values["pslew_c_start"]
pslew_c_stop = input_values["pslew_c_stop"]
pslew_c_common_ratio = input_values["pslew_c_common_ratio"]
pskew_b_start = input_values["pskew_b_start"]
pskew_b_stop = input_values["pskew_b_stop"]
pskew_b_step = input_values["pskew_b_step"]
pskew_c_start = input_values["pskew_c_start"]
pskew_c_stop = input_values["pskew_c_stop"]
pskew_c_step = input_values["pskew_c_step"]


output_filename = input_values["output_filename"]

def generate_points(start, end, common_ratio):
    
    points = []

    current_point = start
    while current_point <= end:
        points.append(current_point)
        current_point *= common_ratio
    if points[-1] != end:
        points.append(end)
        
    return points

def generate_points2(start, end, common_ratio):
    
    points = []

    current_point = start
    while current_point <= end:
        points.append(current_point)
        current_point *= common_ratio
    
    return points


pload = generate_points2(pload_start, pload_stop, pload_common_ratio)
pslew_a = generate_points2(pslew_a_start, pslew_a_stop, pslew_a_common_ratio)
pslew_b = generate_points2(pslew_b_start, pslew_b_stop, pslew_b_common_ratio)
pslew_c = generate_points2(pslew_c_start, pslew_c_stop, pslew_c_common_ratio)

# Function to append values from input CSV to output CSV
def append_csv_values(input_file, output_file):
    with open(input_file, 'r', errors='ignore') as input_csv, open(output_file, 'a', newline='') as output_csv:
        reader = csv.reader(input_csv)
        writer = csv.writer(output_csv)
        # Skip the first line of the input CSV
        next(reader, None)
        # Append values from input CSV to output CSV
        for row in reader:
            writer.writerow(row)


#Write the legend to the output file
with open(output_filename, 'w') as f:
    f.write(" load, slew_a, slew_b, slew_c, process, voltage, temperature, skew_b, skew_c, rise_delay, fall_delay, rise_slew, fall_slew\n")


######.............................................................................................................................................######
######.............................................................................................................................................######
# function to replace the placeholders in the ocean script with the values
#The replace() method in Python is used to replace all occurrences of a specified substring with a new substring.In this command, ocean_script is a string variable and replace() is used to replace the substring "pcorners" in ocean_script with the value of corners variable.
def replace_placeholders(ocean_script, output_file, simulator_name, design_dir, results_dir, model_file, stimulus_file, analysis_start, analysis_stop, analysis_step,  load_1, slew_a_1, slew_b_1, slew_c_1):
    
    
    ocean_script = ocean_script.replace("output_file", f'"{output_file}"')
    ocean_script = ocean_script.replace("simulator_name", f'"{simulator_name}"')
    ocean_script = ocean_script.replace("design_dir", f'"{design_dir}"')
    ocean_script = ocean_script.replace("results_dir", f'"{results_dir}"')
    ocean_script = ocean_script.replace("model_file", f'"{model_file}"')
    ocean_script = ocean_script.replace("stimulus_file", f'"{stimulus_file}"')

    ocean_script = ocean_script.replace("analysis_start", f'"{analysis_start}"')
    ocean_script = ocean_script.replace("analysis_stop", f'"{analysis_stop}"')
    ocean_script = ocean_script.replace("analysis_step", f'"{analysis_step}"')

    pcorner_replacement = " ".join([f'"{item}"' for item in pcorners_list])
    ocean_script = ocean_script.replace("pcorners_list", pcorner_replacement)

    ocean_script = ocean_script.replace("pvdd_start", f'"{pvdd_start}"')
    ocean_script = ocean_script.replace("pvdd_stop", f'"{pvdd_stop}"')
    ocean_script = ocean_script.replace("pvdd_step", f'"{pvdd_step}"')

    ocean_script = ocean_script.replace("ptemp_start", f'"{ptemp_start}"')
    ocean_script = ocean_script.replace("ptemp_stop", f'"{ptemp_stop}"')
    ocean_script = ocean_script.replace("ptemp_step", f'"{ptemp_step}"')

    ocean_script = ocean_script.replace("pskew_b_start", f'"{pskew_b_start}"')
    ocean_script = ocean_script.replace("pskew_b_stop", f'"{pskew_b_stop}"')
    ocean_script = ocean_script.replace("pskew_b_step", f'"{pskew_b_step}"')

    ocean_script = ocean_script.replace("pskew_c_start", f'"{pskew_c_start}"')
    ocean_script = ocean_script.replace("pskew_c_stop", f'"{pskew_c_stop}"')
    ocean_script = ocean_script.replace("pskew_c_step", f'"{pskew_c_step}"')
  
    #print("Replace the pload in the ocean script with the current load =", load_1)
    ocean_script = ocean_script.replace("pload_1", f'"{(load_1)}"')
    #print("Replace the pslew_a in the ocean script with the current slew_a =", slew_a_1)
    ocean_script = ocean_script.replace("pslew_a_1", f'"{(slew_a_1)}"')
    #print("Replace the pslew_b in the ocean script with the current slew_b=", slew_b_1)
    ocean_script = ocean_script.replace("pslew_b_1", f'"{(slew_b_1)}"')
    #print("Replace the pslew_c in the ocean script with the current slew_b=", slew_c_1)
    ocean_script = ocean_script.replace("pslew_c_1", f'"{(slew_c_1)}"')

    #print("print the current ocean script", ocean_script)
    return ocean_script

######.............................................................................................................................................######
######.............................................................................................................................................######
#Perform the simulation for the given set of input and return the value pf tplh, tphl, tr , tf

def simulate(ocean_script, interim_output_file, simulator_name, design_dir, results_dir, model_file, stimulus_file, analysis_start, analysis_stop, analysis_step, load_1, slew_a_1, slew_b_1, slew_c_1):
    ocean_script = replace_placeholders(ocean_script, interim_output_file, simulator_name, design_dir, results_dir, model_file, stimulus_file, analysis_start, analysis_stop, analysis_step, load_1, slew_a_1, slew_b_1, slew_c_1)

    # Start a new csh shell in a subproces  
    #print("Number of combination for load and slew (how many time changing enviroment) =", index)                        
    #print("Start a new csh shell in a subprocess \n \n Ocean script running......wait ")
            
    # Run the "ocean" command using C shell and then run ocean script, capture the output
    ocean_script_output = subprocess.run(["csh", "-c", "source /cadence/cshrc; ocean"], input=ocean_script, capture_output=True, text=True)
    # Print the captured output
    print("Standard Output AND3X4:")
    print( ocean_script_output.stdout)

    print("Standard Error AND3X4:")
    print( ocean_script_output.stderr)
    
    #Check if the command was successful or not and print a message accordingly
    if ocean_script_output.returncode == 0:
        print("Ocean environment started successfully AND3X4")
    else:
        print("Error: Failed to start ocean environment AND3X4")
    return ocean_script_output



######.............................................................................................................................................######
######.............................................................................................................................................######

######.............................................................................................................................................######
######.............................................................................................................................................######
#start to form the dataset
index=0
# Start the overall timer
total_start_time = time.time() 



#print("start for load")
for load_1 in pload:
    #print("start for slew_a")      
    for slew_a_1 in pslew_a:
        #print("start for slew_b")
        for slew_b_1 in pslew_b:
            #print("start for slew_c")
            for slew_c_1 in pslew_c:
                # To see how the number of loops run
                index = index + 1
                print("DATASET GENERATION STARTED FOR GIVEN INPUT AND3X4")
 
                # Simulate at the input given at a time 
                ocean_script_output = simulate(ocean_script, interim_output_file, simulator_name, design_dir, results_dir, model_file, stimulus_file, analysis_start, analysis_stop, analysis_step, load_1, slew_a_1, slew_b_1, slew_c_1)
           
                # Append values from input CSV to output CSV
                append_csv_values(interim_output_file, output_filename)
                          
                # Replace the values in the ocean script with the variable again
                ocean_script = ocean_script_1



######.............................................................................................................................................######
######.............................................................................................................................................######

print("\n**************************************\n")
print("\nDATASET GENERATION COMPLETED AND3X4\n")

# Stop the overall timer
total_end_time = time.time() 
total_elapsed_time = total_end_time - total_start_time
print(f"Total simulation time AND3X4: {total_elapsed_time} seconds")

######.............................................................................................................................................######
######.............................................................................................................................................######





