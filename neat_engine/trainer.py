import os
import pickle
import neat

from .features import normalize_metrics
from .strategy import HYPOTHESES


TRAINING_CASES = [
    {
        "metrics": {
            "revenue_change_pct": -10,
            "traffic_change_pct": -30,
            "conversion_change_pct": -5,
            "mobile_conversion_change_pct": -5,
            "payment_failure_change_pct": 5,
            "checkout_error_change_pct": 5,
        },
        "target": "traffic",
    },
    {
        "metrics": {
            "revenue_change_pct": -10,
            "traffic_change_pct": 0,
            "conversion_change_pct": -30,
            "mobile_conversion_change_pct": -10,
            "payment_failure_change_pct": 5,
            "checkout_error_change_pct": 5,
        },
        "target": "conversion",
    },
    {
        "metrics": {
            "revenue_change_pct": -10,
            "traffic_change_pct": 0,
            "conversion_change_pct": -10,
            "mobile_conversion_change_pct": -50,
            "payment_failure_change_pct": 5,
            "checkout_error_change_pct": 5,
        },
        "target": "device",
    },
    {
        "metrics": {
            "revenue_change_pct": -10,
            "traffic_change_pct": 0,
            "conversion_change_pct": -10,
            "mobile_conversion_change_pct": -10,
            "payment_failure_change_pct": 150,
            "checkout_error_change_pct": 20,
        },
        "target": "payment",
    },
    {
        "metrics": {
            "revenue_change_pct": -10,
            "traffic_change_pct": 0,
            "conversion_change_pct": -10,
            "mobile_conversion_change_pct": -10,
            "payment_failure_change_pct": 10,
            "checkout_error_change_pct": 150,
        },
        "target": "technical",
    },
    {
        "metrics": {
            "revenue_change_pct": -10,
            "traffic_change_pct": 0,
            "conversion_change_pct": -10,
            "mobile_conversion_change_pct": -10,
            "payment_failure_change_pct": 10,
            "checkout_error_change_pct": 10,
        },
        "target": "product",
    },
]


def fitness_function(genome, config):
    network = neat.nn.FeedForwardNetwork.create(
        genome,
        config
    )

    total_fitness = 0.0

    for case in TRAINING_CASES:
        inputs = normalize_metrics(case["metrics"])

        outputs = network.activate(inputs)

        predicted_index = max(
            range(len(outputs)),
            key=lambda i: outputs[i]
        )

        predicted = HYPOTHESES[predicted_index]
        target = case["target"]

        if predicted == target:
            total_fitness += 10.0
        else:
            total_fitness -= 1.0

    return total_fitness


def eval_genomes(genomes, config):
    for _, genome in genomes:
        genome.fitness = fitness_function(
            genome,
            config
        )


def main():

    config_path = os.path.join(
        os.path.dirname(__file__),
        "config-feedforward.txt"
    )

    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    population = neat.Population(config)

    population.add_reporter(
        neat.StdOutReporter(True)
    )

    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(
        eval_genomes,
        30
    )

    os.makedirs("data", exist_ok=True)

    output_path = os.path.join(
        "data",
        "neat_best.pkl"
    )

    with open(output_path, "wb") as f:
        pickle.dump(
            winner,
            f
        )

    print()
    print("NEAT training completed.")
    print(f"Best genome saved to: {output_path}")


if __name__ == "__main__":
    main()