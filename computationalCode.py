import random
import math
import pandas as pd

# Constants
RECTILINEAR = 'R'  # 0° and 90°
DIAGONAL = 'D'     # 45° and 135°

# Polarization mapping: (bit, basis) -> angle
polarizations = {
    (0, RECTILINEAR): '0°',
    (1, RECTILINEAR): '90°',
    (0, DIAGONAL): '45°',
    (1, DIAGONAL): '135°'
}

def random_bits(n):
    return [random.randint(0, 1) for _ in range(n)]

def random_bases(n):
    return [random.choice([RECTILINEAR, DIAGONAL]) for _ in range(n)]

def measure(photon_bit, alice_basis, bob_basis, noise_probability=0.02):
    if alice_basis == bob_basis:
        return photon_bit if random.random() >= noise_probability else 1 - photon_bit
    return random.randint(0, 1)

def calculate_error_rate(alice_bits, bob_bits):
    if not alice_bits:
        return 0
    mismatches = sum(a != b for a, b in zip(alice_bits, bob_bits))
    return mismatches / len(alice_bits)

def simulate_trial(n, eavesdropping=False, noise_probability=0.02):
    alice_bits = random_bits(n)
    alice_bases = random_bases(n)
    bob_bases = random_bases(n)

    if not eavesdropping:
        bob_bits = [measure(bit, a_basis, b_basis, noise_probability)
                    for bit, a_basis, b_basis in zip(alice_bits, alice_bases, bob_bases)]
    else:
        eavesdropper_bases = random_bases(n)
        eavesdropper_bits = [measure(bit, a_basis, e_basis, noise_probability)
                             for bit, a_basis, e_basis in zip(alice_bits, alice_bases, eavesdropper_bases)]
        bob_bits = [measure(bit, e_basis, b_basis, noise_probability)
                    for bit, e_basis, b_basis in zip(eavesdropper_bits, eavesdropper_bases, bob_bases)]

    sifted_indices = [i for i in range(n) if alice_bases[i] == bob_bases[i]]
    alice_sifted = [alice_bits[i] for i in sifted_indices]
    bob_sifted = [bob_bits[i] for i in sifted_indices]

    error_rate = calculate_error_rate(alice_sifted, bob_sifted)
    return error_rate * 100

def run_simulation_for_n(n, trials=1000, noise_probability=0.02):
    with_data, without_data = [], []
    with_rates, without_rates = [], []

    with open(f"error_rates_with_eavesdropping_n_{n}.txt", "w") as f_with, \
         open(f"error_rates_without_eavesdropping_n_{n}.txt", "w") as f_without:

        for i in range(trials):
            rate_with = simulate_trial(n, eavesdropping=True, noise_probability=noise_probability)
            rate_without = simulate_trial(n, eavesdropping=False, noise_probability=noise_probability)

            with_data.append({'Trial': i+1, 'Error Rate (%)': rate_with})
            without_data.append({'Trial': i+1, 'Error Rate (%)': rate_without})

            with_rates.append(rate_with)
            without_rates.append(rate_without)

            f_with.write(f"Trial {i+1}: {rate_with:.2f}%\n")
            f_without.write(f"Trial {i+1}: {rate_without:.2f}%\n")

    pd.DataFrame(with_data).to_excel(f"error_rates_with_eavesdropping_n_{n}.xlsx", index=False)
    pd.DataFrame(without_data).to_excel(f"error_rates_without_eavesdropping_n_{n}.xlsx", index=False)

    def stats(values):
        avg = sum(values) / len(values)
        std = math.sqrt(sum((x - avg) ** 2 for x in values) / len(values))
        return avg, std

    avg_with, std_with = stats(with_rates)
    avg_without, std_without = stats(without_rates)

    print(f"\nn = {n}")
    print(f"  With Eavesdropping    -> Avg: {avg_with:.2f}%, Std: {std_with:.2f}%")
    print(f"  Without Eavesdropping -> Avg: {avg_without:.2f}%, Std: {std_without:.2f}%")
    print("-" * 60)

    return {
        'n': n,
        'Avg_Error_With_Eavesdropping': avg_with,
        'Std_Error_With_Eavesdropping': std_with,
        'Avg_Error_Without_Eavesdropping': avg_without,
        'Std_Error_Without_Eavesdropping': std_without
    }

# Run simulations for n = 10, 100, 1000 and collect stats
summary = []
for n in [10, 100, 1000]:
    result = run_simulation_for_n(n)
    summary.append(result)

# Save summary statistics to CSV
summary_df = pd.DataFrame(summary)
summary_df.to_csv("summary_statistics.csv", index=False)

print("\nSummary CSV saved as 'summary_statistics.csv'")
