from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def read_input():
    N = int(input().strip())  # Number of customers (not counting the depot)
    e, l, d = [], [], []
    
    # Read e(i), l(i), and d(i) for each customer 1 to N
    for _ in range(N):
        ei, li, di = map(int, input().split())
        e.append(ei)
        l.append(li)
        d.append(di)
    
    # Read the time matrix t(i, j) for 0 <= i, j <= N
    t = []
    for _ in range(N+1):
        row = list(map(int, input().split()))
        t.append(row)
    
    data = {}
    data['N'] = N
    data['time_matrix'] = t
    data['time_windows'] = [(0, 100000)] + list(zip(e, l))
    data['service_time'] = [0] + d  # depot has 0 service time
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data

def print_solution(data, manager, routing, solution):
    # Extract the route
    vehicle_id = 0
    index = routing.Start(vehicle_id)
    route = []
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node != data['depot']:
            route.append(node)
        index = solution.Value(routing.NextVar(index))
    
    # Print results according to the problem requirements
    print(data['N'])
    print(" ".join(map(str, route)))

def main():
    data = read_input()
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           data['num_vehicles'], 
                                           data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        travel_time = data["time_matrix"][from_node][to_node]
        serv_time = data["service_time"][from_node]
        return travel_time + serv_time

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    
    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Add time window constraints
    time = "Time"
    routing.AddDimension(
        transit_callback_index,
        600000, 
        600000,  
        False,
        time,
    )
    time_dimension = routing.GetDimensionOrDie(time)
    
    # Set time windows for each node
    for location_idx, time_window in enumerate(data["time_windows"]):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    
    # Minimize start and end times
    vehicle_id = 0
    routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.Start(vehicle_id)))
    routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(vehicle_id)))
    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        pass

if __name__ == "__main__":
    main()
