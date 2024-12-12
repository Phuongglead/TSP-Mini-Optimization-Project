'''
Input:
    - N: Number of nodes (including depot)
    - t[i][j]: Travel time between node i and node j
    - e[i], l[i]: Earliest and latest allowable times for node i
    - d[i]: Service time at node i
    - K: Number of ants
    - MaxIter: Maximum number of iterations
    - Parameters: α (pheromone influence), β (heuristic influence), ρ (evaporation rate), Q (pheromone deposit factor)

Output:
    - BestSolution: Best path found
    - BestCost: Cost of the best solution

Initialize:
    - Initialize pheromone matrix τ[i][j] = τ₀ for all i, j
    - Define heuristic information η[i][j] = 1 / t[i][j]
    - BestSolution ← ∅, BestCost ← ∞

For iter = 1 to MaxIter do:
    Solutions ← ∅

    For each ant k = 1 to K do:
        - Initialize CurrentNode ← Depot (node 0)
        - Initialize Path ← [Depot]
        - Initialize ArrivalTime ← t₀ (start time)
        - Initialize Visited ← {Depot}

        While |Path| < N + 1 do:
            - Calculate Probabilities for moving to each unvisited node j:
                If j ∉ Visited and ArrivalTime + t[CurrentNode][j] satisfies time windows:
                    P[j] = (τ[CurrentNode][j]^α) * (η[CurrentNode][j]^β)
                Else:
                    P[j] = 0

            - Normalize P[j] to make it a probability distribution.
            - Select next node j based on P[j] (roulette-wheel selection).
            - Update Path, Visited, and ArrivalTime:
                ArrivalTime = max(e[j], ArrivalTime + t[CurrentNode][j]) + d[j]
                Append j to Path, mark j as visited.

        - Calculate Cost for the ant's Path.
        - If Path violates constraints (e.g., time windows):
            Assign a high penalty cost to the Path.
        - Add Path and its Cost to Solutions.

    Update Pheromone:
        - Evaporate pheromones: τ[i][j] = (1 - ρ) * τ[i][j] for all i, j
        - For each ant solution in Solutions:
            If solution is feasible:
                Deposit pheromones along the path:
                τ[i][j] += Q / Cost

    Update BestSolution and BestCost:
        - If any solution in Solutions is better than BestCost:
            Update BestSolution and BestCost.

Return BestSolution, BestCost

'''

import random
from utils import read_input, evaluate

# Global variables for pheromone and heuristic matrices
pheromone = []
heuristic = []

def initialize_pheromone_matrix(n, initial_pheromone=1.0):
    """
    Initialize the pheromone matrix with a given initial pheromone level.
    
    Args:
        n (int): Number of nodes.
        initial_pheromone (float): Initial pheromone level for all edges.

    Returns:
        list of lists: Pheromone matrix.
    """
    global pheromone
    pheromone = [[initial_pheromone for _ in range(n + 1)] for _ in range(n + 1)]

def construct_heuristic(travel_time):
    """
    Construct the heuristic matrix based on travel time.

    Args:
        travel_time (list of lists): Matrix of travel times between nodes.

    Returns:
        list of lists: Heuristic matrix where heuristic[i][j] is the inverse of travel_time[i][j].
    """
    global heuristic
    heuristic = [[1 / travel_time[i][j] if travel_time[i][j] > 0 else 0 for j in range(len(travel_time))] for i in range(len(travel_time))]


def update_pheromone(solutions, evaporation_rate, Q):
    """
    Update the pheromone levels based on the solutions found by ants.

    Args:
        solutions (list of tuples): List of (solution, cost) pairs.
        evaporation_rate (float): Rate at which pheromone evaporates.
        Q (float): Constant for pheromone deposit.

    Returns:
        None
    """     
    global pheromone
    # Evaporate pheromone
    for i in range(len(pheromone)):
        for j in range(len(pheromone)):
            pheromone[i][j] *= (1 - evaporation_rate)

    # Deposit pheromone
    for solution, cost in solutions:
        if cost == -1:
            pheromone_delta = - 0.005 * Q
        else:
            pheromone_delta = Q / cost
        for k in range(len(solution) - 1):
            i, j = solution[k], solution[k + 1]
            pheromone[i][j] += pheromone_delta # One direction 
            # pheromone[i][j] = max(0, pheromone[i][j])


def choose_next_node(current_node, visited, alpha, beta, timer, travel_time, time_windows):
    """
    Choose the next node based on pheromone and heuristic information.

    Args:
        current_node (int): Current position of the ant.
        visited (set): Set of visited nodes.
        alpha (float): Pheromone influence.
        beta (float): Heuristic influence.

    Returns:
        int: The chosen next node.
    """
    global pheromone, heuristic
    probabilities = []
    total_prob = 0
    for next_node in range(len(pheromone)):
        if next_node not in visited and timer + travel_time[current_node][next_node] <= time_windows[next_node][1]:
            prob = (pheromone[current_node][next_node] ** alpha) * (heuristic[current_node][next_node] ** beta)
            probabilities.append((next_node, prob))
            total_prob += prob

    if len(probabilities) == 0:
        return -1, -1

    if total_prob == 0:
        next_node = random.choice([node for node in range(len(pheromone)) if node not in visited])
        timer = max(timer + travel_time[current_node][next_node], time_windows[next_node][0]) + time_windows[next_node][2]
        return timer, next_node

    probabilities = [(node, prob / total_prob) for node, prob in probabilities]
    r = random.random()
    cumulative = 0
    for next_node, prob in probabilities:
        cumulative += prob
        if r <= cumulative:
            timer = max(timer + travel_time[current_node][next_node], time_windows[next_node][0]) + time_windows[next_node][2]
            return timer, next_node


def construct_solution(n, alpha, beta, travel_time, time_windows):
    """
    Construct a solution for an ant.

    Args:
        n (int): Number of nodes.
        pheromone (list of lists): Pheromone matrix.
        heuristic (list of lists): Heuristic matrix (e.g., inverse of distance).
        alpha (float): Pheromone influence.
        beta (float): Heuristic influence.

    Returns:
        list: A solution represented as a sequence of node indices.
    """
    global pheromone, heuristic
    solution = [0]
    visited = set()
    current_node = 0
    visited.add(current_node)
    timer = 0


    while len(visited) < n + 1:
        timer, next_node = choose_next_node(current_node, visited, alpha, beta, timer, travel_time, time_windows)
        if timer == -1:
            return False, solution, timer
        solution.append(next_node)
        visited.add(next_node)
        current_node = next_node
    
    timer += travel_time[current_node][0]

    return True, solution, timer

# Example usage
if __name__ == "__main__":
    use_file = True
    file_path = "TestCase\Subtask_10\input1.txt"
    
    N, time_windows, travel_time = read_input(from_file=use_file, file_path=file_path)
    initialize_pheromone_matrix(N)
    construct_heuristic(travel_time)

    alpha = 2.0  # Pheromone influence
    beta = 1.0   # Heuristic influence
    evaporation_rate = 0.1
    Q = 100  # Pheromone deposit constant
    num_ants = 10
    num_iterations = 100

    best_solution = None
    best_cost = float('inf')

    for iteration in range(num_iterations):
        solutions = []
        for _ in range(num_ants):
            is_valid, solution, cost = construct_solution(N, alpha, beta, travel_time, time_windows)
            # print(solution[1:])
            solutions.append((solution, cost))

            if is_valid:
                if cost < best_cost:
                    best_solution = solution
                    best_cost = cost
            
        # print(solutions)
            
            

        # update_pheromone(solutions, evaporation_rate, Q)
        # for row in pheromone:
        #     for e in row:
        #         print(f"%.2f"%e, end=" ")
        #     print()
        print(f"Iteration {iteration + 1}: Best Cost = {best_cost}")

    print("Best Solution:", best_solution)
    print("Best Cost:", best_cost)
