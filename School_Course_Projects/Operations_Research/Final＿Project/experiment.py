import numpy as np
import pandas as pd
import random

# ----------- Sampling Functions -----------

def sample_cluster_means(n_cluster, d_min, d_max, delta=0.1):
    """
    Sample the mean (center) of each cluster in 2D.
    Args:
        n_cluster (int): Number of clusters.
        d_min (float): Minimum radial distance from city center.
        d_max (float): Maximum radial distance from city center.
        delta (float): Maximum angular perturbation in radians.
    Returns:
        means: List of shape (n_cluster, 2) with cluster mean coordinates.
    """
    means = []
    if n_cluster == 1:
        means.append(np.array([0.0, 0.0]))
    else:
        for k in range(n_cluster):
            theta_k = 2 * np.pi * k / n_cluster + np.random.uniform(-delta, delta)
            r_k = np.random.uniform(d_min, d_max)
            mu_k = r_k * np.array([np.cos(theta_k), np.sin(theta_k)])
            means.append(mu_k)
    return np.array(means)

def sample_points(cluster_mean, sigma, n_sample):
    """
    Sample points (spots/hotels) from a bivariate normal distribution.
    Args:
        cluster_mean (np.ndarray): Center of the cluster, shape (2,).
        sigma (float): Standard deviation (spread) of the cluster.
        n_sample (int): Number of points to sample.
    Returns:
        points: Array of shape (n_sample, 2) with sampled (x, y) locations.
    """
    return np.random.multivariate_normal(
        mean=cluster_mean,
        cov=sigma**2 * np.eye(2),
        size=n_sample
    )

def sample_airport(cluster_mean, sigma, sigma_ratio_range=(2, 10)):
    """
    Sample an airport location for a given cluster.
    Args:
        cluster_mean (np.ndarray): Center of the cluster, shape (2,).
        sigma (float): Spot density parameter for the cluster.
        sigma_ratio_range (tuple): Range for uniform sampling of sigma_airport as a multiple of sigma.
    Returns:
        airport_location: Array of shape (2,) for airport (x, y) location.
    """
    sigma_airport = np.random.uniform(*sigma_ratio_range) * sigma
    return np.random.multivariate_normal(
        mean=cluster_mean,
        cov=sigma_airport**2 * np.eye(2)
    )

# ----------- Control Variable Sampling -----------

def get_transport_costs(price_level_lambda):
    # Always use medium (Tokyo) as base
    base = {"train": (3, 6), "taxi": (60, 120)}
    train_rate = np.random.uniform(*base["train"]) * price_level_lambda
    taxi_rate = np.random.uniform(*base["taxi"]) * price_level_lambda
    walk_rate = 0.0
    return walk_rate, train_rate, taxi_rate

def compute_hotel_distances(hotels, spots, k_nearest=5):
    from scipy.spatial import distance_matrix
    dists = distance_matrix(hotels, spots)
    # For each hotel, get mean of k nearest spots
    sorted_d = np.sort(dists, axis=1)
    mean_d = np.mean(sorted_d[:, :k_nearest], axis=1)
    return mean_d

def sample_hotel_costs(hotels, spots, price_level_lambda):
    mean_d = compute_hotel_distances(hotels, spots, k_nearest=5)
    d_min = mean_d.min()
    d_max = mean_d.max()
    s = (mean_d - d_min) / (d_max - d_min + 1e-9)  # add epsilon to avoid zero division
    costs = np.zeros_like(s)
    for i, score in enumerate(s):
        if score <= 0.3:
            costs[i] = price_level_lambda * np.random.uniform(6000, 9000)
        elif score <= 0.7:
            costs[i] = price_level_lambda * np.random.uniform(3000, 6000)
        else:
            costs[i] = price_level_lambda * np.random.uniform(1500, 3000)
    return costs

def sample_attraction_costs(n_spots, price_level_lambda):
    paid = np.random.rand(n_spots) < 0.5
    costs = np.zeros(n_spots)
    costs[paid] = price_level_lambda * np.random.uniform(100, 800, size=paid.sum())
    # Free attractions remain zero
    return costs

def sample_attraction_open_close(n_spots):
    open_choices = np.array([5, 6, 7, 8, 9]) * 60  # in minutes
    close_choices = np.array([17, 18, 19, 20, 21]) * 60
    open_times = np.random.choice(open_choices, size=n_spots)
    close_times = np.random.choice(close_choices, size=n_spots)
    return open_times, close_times

def sample_experience_scores(n_spots):
    return np.random.uniform(1, 5, size=n_spots)

def sample_stay_times(n_spots):
    return np.random.uniform(120, 240, size=n_spots)

# ----------- Main Experiment Sampler -----------

def sample_city_experiment(
    n_cluster=3,
    cluster_sigma=1.5,
    n_spots=150,
    n_hotels=30,
    n_lambda=1,
    price_level_lambda=1
):

    # 1. Clusters
    cluster_sigmas = [cluster_sigma for _ in range(n_cluster)]
    clusters = sample_cluster_means(n_cluster, 3 * cluster_sigma, 6 * cluster_sigma)
    
    # 2. Sample spots/hotels
    # Even allocation: distribute remainder one by one to the first clusters
    spots_per_cluster = [n_spots // n_cluster] * n_cluster
    hotels_per_cluster = [n_hotels // n_cluster] * n_cluster
    
    # Distribute the remaining spots
    for i in range(n_spots % n_cluster):
        spots_per_cluster[i] += 1
    
    # Distribute the remaining hotels
    for i in range(n_hotels % n_cluster):
        hotels_per_cluster[i] += 1
    
    spots = []
    hotels = []
    for i, mu in enumerate(clusters):
        s = sample_points(mu, cluster_sigma, spots_per_cluster[i])
        h = sample_points(mu, cluster_sigma, hotels_per_cluster[i])
        spots.append(s)
        hotels.append(h)
    spots = np.vstack(spots)
    hotels = np.vstack(hotels)
    
    # 3. Airports (arrival, departure)
    cluster_indices = np.arange(n_cluster)
    arr_idx = np.random.choice(cluster_indices)
    dep_idx = arr_idx if (n_cluster == 1 or np.random.rand() < 0.5) else np.random.choice(cluster_indices[cluster_indices != arr_idx])
    arrival_airport = sample_airport(clusters[arr_idx], cluster_sigma)
    departure_airport = sample_airport(clusters[dep_idx], cluster_sigma)
    airports = [arrival_airport, departure_airport]
    
    # 4. Control variables
    walk_rate, train_rate, taxi_rate = get_transport_costs(price_level_lambda)
    hotel_costs = sample_hotel_costs(hotels, spots, price_level_lambda) # hotel_costs: shape (n_hotels, 1)
    attraction_costs = sample_attraction_costs(len(spots), price_level_lambda)
    open_times, close_times = sample_attraction_open_close(len(spots))
    experience_scores = sample_experience_scores(len(spots))
    stay_times = sample_stay_times(len(spots))

    Day1Arrival = random.uniform(0, 720)     # 第一天抵達的時間
    DayDReturnArrival = random.uniform(720, 1440)  # 最後一天離開的時間
    
    # 5. Fixed parameters
    leaving_time = 9 * 60    # 09:00 in minutes
    return_time = 23 * 60    # 23:00 in minutes
    
    # Pack results
    return {
        "clusters": clusters,
        "spots": spots,
        "hotels": hotels,
        "airports": airports,
        "hotel_costs": hotel_costs,
        "attraction_costs": attraction_costs,
        "attraction_open_times": open_times,
        "attraction_close_times": close_times,
        "experience_scores": experience_scores,
        "stay_times": stay_times,
        "transport_cost_rates": {
            "walk": walk_rate,
            "train": train_rate,
            "taxi": taxi_rate
        },
        "leaving_time": leaving_time,
        "return_time": return_time,
        "LH_1": Day1Arrival,
        "RH_D": DayDReturnArrival
    }

# ----------- Simulation -----------
# !!!!! The M here excludes the two airports, so actually 5+2, 25+2, 50+2, returns are correct
def simulation(scenario_number, scale_dict): 
    scenario_dict = {
        1: {"scale": "medium", "lambda": "medium", "Budget": "medium", "n_cluster": "medium", "sigma": "medium"},
        2: {"scale": "small", "lambda": "medium", "Budget": "medium", "n_cluster": "medium", "sigma": "medium"},
        3: {"scale": "large", "lambda": "medium", "Budget": "medium", "n_cluster": "medium", "sigma": "medium"},
        4: {"scale": "medium", "lambda": "small", "Budget": "medium", "n_cluster": "medium", "sigma": "medium"},
        5: {"scale": "medium", "lambda": "large", "Budget": "medium", "n_cluster": "medium", "sigma": "medium"},
        6: {"scale": "medium", "lambda": "medium", "Budget": "small", "n_cluster": "medium", "sigma": "medium"},
        7: {"scale": "medium", "lambda": "medium", "Budget": "large", "n_cluster": "medium", "sigma": "medium"},
        8: {"scale": "medium", "lambda": "medium", "Budget": "medium", "n_cluster": "small", "sigma": "medium"},
        9: {"scale": "medium", "lambda": "medium", "Budget": "medium", "n_cluster": "large", "sigma": "medium"},
        10: {"scale": "medium", "lambda": "medium", "Budget": "medium", "n_cluster": "medium", "sigma": "small"},
        11: {"scale": "medium", "lambda": "medium", "Budget": "medium", "n_cluster": "medium", "sigma": "large"},
    }

    scaleof = scenario_dict[scenario_number]

    # Parameters for simulation
    n_cluster = scale_dict[scaleof["n_cluster"]]["n_cluster"]
    sigma = scale_dict[scaleof["sigma"]]["sigma"]
    n_lambda = scale_dict[scaleof["lambda"]]["lambda"]
    n_hotels = scale_dict[scaleof["scale"]]["M"] # excluding airports
    n_spots = scale_dict[scaleof["scale"]]["I"]
    price_level_lambda = n_lambda

    # 1. Generate synthetic instance
    sampled = sample_city_experiment(
        n_cluster=n_cluster,
        cluster_sigma=sigma,
        n_spots=n_spots,
        n_hotels=n_hotels,
        price_level_lambda=price_level_lambda
    )

    # 2. Assign variables for simulation()
    # Budget and other scale parameters
    M = scale_dict[scaleof["scale"]]["M"] + 2
    I = scale_dict[scaleof["scale"]]["I"]
    P = M + I
    D = scale_dict[scaleof["scale"]]["D"]
    total_budget = D * n_lambda * scale_dict[scaleof["Budget"]]["Budget"] # Total
    K = 3  # Only 3 methods
    
    # STAY and HAPPINESS as pandas Series
    STAY = pd.Series(sampled["stay_times"])
    HAPPINESS = pd.Series(sampled["experience_scores"])

    # Arrival/return times as pandas Series
    LH = pd.Series([sampled["leaving_time"] for _ in range(D)])
    RH = pd.Series([sampled["return_time"] for _ in range(D)])
    LH.iloc[0] = sampled["LH_1"]  # Day 1 arrival time
    RH.iloc[-1] = sampled["RH_D"]  # Last day return time

    # 3. Combine all locations for travel matrices
    # hotels, spots, airports (arrival, departure)
    spots = sampled["spots"]
    hotels = sampled["hotels"]
    airports = np.array(sampled["airports"])
    first_airport = airports[0].reshape(1, -1)
    last_airport = airports[1].reshape(1, -1)
    
    locations = np.vstack([
        spots,
        first_airport,
        hotels,
        last_airport
    ])
    n_locs = locations.shape[0]

    # 4. Compute time matrices
    from scipy.spatial import distance_matrix
    walk_speed_kmh = 5
    walk_time = distance_matrix(locations, locations) / walk_speed_kmh * 60  # time in minutes

    train_speed_kmh = 20
    train_time = distance_matrix(locations, locations) / train_speed_kmh * 60
    car_speed_kmh = 30
    car_time = distance_matrix(locations, locations) / car_speed_kmh * 60

    DURATION = {
        'Walk': walk_time,
        'Train': train_time,
        'Car': car_time
    }

    # 5. Travel costs: elementwise time * rate
    train_rate = sampled["transport_cost_rates"]["train"]
    car_rate = sampled["transport_cost_rates"]["taxi"]
    
    # Elementwise multiplication, time in minutes
    train_cost_matrix = DURATION['Train'] * train_rate
    car_cost_matrix = DURATION['Car'] * car_rate
    walk_cost_matrix = np.zeros((n_locs, n_locs))  # Walk is always free
    
    C_TRAVEL = {
        'Walk': walk_cost_matrix,
        'Train': train_cost_matrix,
        'Car': car_cost_matrix
    }

    # 6. Hotel costs
    row = np.concatenate(([0], sampled["hotel_costs"], [0])) # Build the row: [0, hotel1, hotel2, ..., hotelN, 0]
    hotel_costs_matrix = np.tile(row, (D, 1)) # Repeat for each day
    C_HOTEL = hotel_costs_matrix

    # 7. Attraction costs (expand to (n_spots, 1) if necessary)
    C_ATTRACTION = sampled["attraction_costs"]

    # 8. Attraction open/close times
    ATTRACTION_OPEN = np.tile(sampled["attraction_open_times"].reshape(-1, 1), (1, D))
    ATTRACTION_CLOSE = np.tile(sampled["attraction_close_times"].reshape(-1, 1), (1, D))

    # 9. Return dictionary
    results = {
        'BUDGET': total_budget,
        'M': M,
        'I': I,
        'P': P,
        'D': D,
        'K': K,
        'LH': LH,
        'RH': RH,
        'Day1Arrival': LH.iloc[0],
        'STAY': STAY,
        'HAPPINESS': HAPPINESS,
        'DURATION': DURATION,
        'C_TRAVEL': C_TRAVEL,
        'C_HOTEL': C_HOTEL,
        'C_ATTRACTION': C_ATTRACTION,
        'ATTRACTION_OPEN': ATTRACTION_OPEN,
        'ATTRACTION_CLOSE': ATTRACTION_CLOSE
    }

    return results