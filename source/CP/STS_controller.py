#!/usr/bin/env python3
import subprocess
import argparse
import time
import math
import json
import pathlib

# Define the run options
option={
        "gecode": {"filename": "STS_model.mzn", "solver_name": "gecode"},
        "chuffed": {"filename": "STS_model.mzn", "solver_name": "chuffed"},
        #"gecode_symbreak": {"filename": "STS_model.mzn", "solver_name": "gecode"}, #TODO: define models with symbreak and optimality
        #"gecode_optimality": {"filename": "STS_model.mzn", "solver_name": "gecode"},
    }

def run_minizinc_subproc(model_filename, solver_name, n, timeout=300):
    """
    Run the model with the specified solver and timeout.
    
    :param model_filename: The filename of the model to run.
    :param soolver_name: The name of the solver to use.
    :param timeout: The timeout for the solver in seconds.
    :return: The result of the model run, the elapsed time, and whether it timed out.
    """

    init_time = time.time()
    timed_out = False
    try:
        process = subprocess.run(
            ["minizinc", "--solver", solver_name, f"-D n={n}","--json-stream", model_filename],
            capture_output=True, 
            timeout=timeout,
            text=True
        )
    
    except subprocess.TimeoutExpired:
        timed_out = True
        process = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="Timeout expired")
    finally:
        end_time = time.time()
        elapsed_time = math.floor(end_time - init_time)


    return process.stdout, elapsed_time, timed_out

def encode_solution(output, solver_name,n,time=300, timed_out=False):
    """
    Encode the solution from the solver output.
    as a dictionary, to be written as json.
    :param output: The output from the solver.
    :param solver_name: The name of the solver used.
    :param n: The value for n.
    :param time: The time taken for the solver to run.
    :param timed_out: Whether the solver timed out.
    :return: A dictionary with the solution, n, time, and optimality status.
    """

    if timed_out:
        return {f"{solver_name}":{"sol": [], "n": n, "time": 300, "optimal":False}}
    
    for line in output.strip().splitlines():
        if not line: continue
        data = json.loads(line)
        if data["type"]=="solution":
            result= {f"{solver_name}":{"sol": json.loads(data["output"]["default"])["sol"], "n": n, "time": time, "optimal":True}}
        elif data["type"]=="status" and (data["status"]=="UNSATISFIABLE" or data["status"]=="UNKNOWN"):
            result = {f"{solver_name}":{"sol": [], "n": n, "time": 300,"optimal":False}}
        elif data["type"]=="status" and data["status"]=="OPTIMAL_SOLUTION":
            result[f"{solver_name}"]["optimal"] = True
        else:
            result[f'{solver_name}']['optimal'] = False

    return result
    
def run_models(options:list[str], n, timeout):
    """
    Run the models with the specified options and parameters.
    :param options: The list of solver/model options to use.
    :param n: The value for n.
    :param timeout: The timeout in seconds.
    :return: A dictionary with the results for each option.
    """

    results = dict()
    for opt in options:
        model = option[opt]
        output, elapsed_time, timed_out = run_minizinc_subproc(model["filename"], model["solver_name"], n, timeout)
        result = encode_solution(output, model["solver_name"], n, elapsed_time,timed_out)
        results[opt] = result[model["solver_name"]]
    return results
def write_results_to_file(results, n):
    """
    Write the results to a JSON file.
    
    :param results: The results to write.
    :param n: The value of n for which the results were generated.
    """
    try:
        output_file = pathlib.Path(f"../../res/CP/{n}.json") #TODO: to be ajjusted to docker path
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
    except FileNotFoundError:
        print(f"Error: The directory {output_file.parent} does not exist. Please create it before running the script.")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

def main(opt,n,timeout):
    """
    Main function to run the MiniZinc model with the specified options.
    
    :param option: The solver/model option to use.
    :param n: The value for n.
    :param timeout: The timeout in seconds.
    """
    if n%2 != 0: raise ValueError("n must be an even number")

    if opt == "all_models":
        results= run_models(option.keys(), n, timeout)
        write_results_to_file(results, n)
    elif opt == "all_models_up_to_n":
        for i in range(2, n + 1,2):
            results = run_models(option.keys(), i, timeout)
            write_results_to_file(results, i)    
    elif opt in option:
        results = run_models([opt], n, timeout)
        write_results_to_file(results, n)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MiniZinc model with specified options.")
    parser.add_argument(
        "option",
        choices=["gecode", "chuffed", "gecode_symbreak", "gecode_optimality", "all_models", "all_models_up_to_n"],
        help="Solver/model option to use"
    )
    parser.add_argument("n", type=int, help="Value for n")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds (default: 300)")
    args = parser.parse_args()
    main(args.option, args.n, args.timeout)