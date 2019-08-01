import numpy as np

# Trying to learn how to implement a Genetic Algorithm
# Following - https://towardsdatascience.com/genetic-algorithm-implementation-in-python-5ab67bb124a6

# Genetic Algorithm

# Inputs to the equation
equation_inputs = [4, -2, 3.5, 5, -11, -4.7];

# Number of weights to consider
num_weights = 6;

# Number of solutions per population
sol_per_population = 8;

# Population Size
# Population size has sol_per_population mutations
pop_size = (sol_per_population, num_weights);

# Create the initial population
new_population = np.random.uniform(low = -4.0, high = 4.0, size = pop_size);