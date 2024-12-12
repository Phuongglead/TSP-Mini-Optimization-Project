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