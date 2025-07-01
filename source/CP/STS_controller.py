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
    :return: The result of the model run.
    """

    init_time = time.time()
    process = subprocess.run(
        ["minizinc", "--solver", solver_name, f"-D n={n}","--json-stream", model_filename],
        capture_output=True, 
        timeout=timeout,
        text=True
    )
    end_time = time.time()
    elapsed_time = math.floor(end_time - init_time)


    return process.stdout, elapsed_time

def encode_solution(output, solver_name,n,time=300):
    """
    Encode the solution from the solver output.
    as a dictionary, to be written as json.
    :param sol: The solution string from the solver.
    """

    
    data = json.loads(output)
    if data["type"]=="solution":
        return {f"{solver_name}":{"sol": json.loads(data["output"]["default"])["sol"], "n": n, "time": time, "optimal":False}}
    elif data["type"]=="status" and data["status"]=="UNSATISFIABLE":
        return {f"{solver_name}":{"sol": [], "solver": solver_name, "n": n, "time": time,"optimal":False}}
    elif data["type"]=="status" and data["status"]=="UNKNOWN":
        return {f"{solver_name}":{"sol": [], "solver": solver_name, "n": n, "time": time,"optimal":False}}

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
        output, elapsed_time = run_minizinc_subproc(model["filename"], model["solver_name"], n, timeout)
        result = encode_solution(output, model["solver_name"], n, elapsed_time)
        results[opt] = result[model["solver_name"]]
    return results
def write_results_to_file(results, n):
    """
    Write the results to a JSON file.
    
    :param results: The results to write.
    :param n: The value of n for which the results were generated.
    """
    
    output_file = pathlib.Path(f"../../res/CP/{n}.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

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