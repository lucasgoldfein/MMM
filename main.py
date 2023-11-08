import numpy as np
from collections import Counter

# Function to apply D'Hondt method for Proportional Representation
def d_hondt(votes, candidate_parties, parties, seats):
    party_votes = Counter({party: 0 for party in parties})
    for candidate, vote_count in votes.items():
        party_votes[candidate_parties[candidate]] += vote_count

    seats_won = {party: 0 for party in parties}
    for _ in range(seats):
        d_hondt_scores = {party: party_votes[party] / (seats_won[party] + 1) for party in parties}
        winning_party = max(d_hondt_scores, key=d_hondt_scores.get)
        seats_won[winning_party] += 1

    pr_winners = []
    for party, count in seats_won.items():
        pr_winners += [party] * count
    return pr_winners

# Function to simulate an election with different systems
def simulate_election(voters, candidates, parties, initial_strengths, iterations):
    election_results = {
        'FPTP': [],
        'MMM': [],
        'PR': []
    }
    party_strength = {party: strength for party, strength in zip(parties, initial_strengths)}
    vote_share_history = []
    party_strength_history = []

    # Repeat the election for the specified number of times
    for _ in range(iterations):
        # Assign each voter a position on the ideology scale
        voter_positions = np.random.uniform(0, 100, voters)
        # Assign each candidate a position on the ideology scale and a party based on party strength
        candidate_positions = np.random.uniform(0, 100, candidates)
        candidate_parties = np.random.choice(parties, candidates, p=list(party_strength.values()))

        # Voters vote for the nearest candidate, considering the strength of the candidate's party
        votes = {candidate: 0 for candidate in range(candidates)}
        vote_counts = {party: 0 for party in parties}
        for voter_position in voter_positions:
            distances = np.abs(candidate_positions - voter_position)
            # Adjust distances by the inverse of party strength, avoiding division by zero
            adjusted_distances = distances * [1 / (party_strength[candidate_parties[c]] or 1) for c in range(candidates)]
            nearest_candidate = np.argmin(adjusted_distances)
            votes[nearest_candidate] += 1
            vote_counts[candidate_parties[nearest_candidate]] += 1

        # Calculate the vote share for each party
        total_votes = sum(vote_counts.values())
        vote_share = {party: count / total_votes for party, count in vote_counts.items()}
        vote_share_history.append(vote_share)

        # First Past The Post (FPTP)
        fptp_winners = Counter(votes).most_common(20)
        election_results['FPTP'].append([candidate_parties[w[0]] for w in fptp_winners])

        # Mixed Member Proportional (MMM)
        mmm_winners = Counter(votes).most_common(10)
        pr_seats = d_hondt(votes, candidate_parties, parties, 10)
        election_results['MMM'].append([candidate_parties[w[0]] for w in mmm_winners] + pr_seats)

        # Proportional Representation (PR) using D'Hondt method
        pr_winners = d_hondt(votes, candidate_parties, parties, 20)
        election_results['PR'].append(pr_winners)

        # Update party strength based on seats won in the PR system
        pr_seats_won = Counter(pr_winners)
        seats_total = sum(pr_seats_won.values())
        for party in parties:
            party_strength[party] = pr_seats_won[party] / seats_total if seats_total > 0 else 0
        party_strength_history.append(party_strength.copy())

    return election_results, party_strength, vote_share_history, party_strength_history

# Simulate the election and get results
voters = 500
candidates = 40
parties = ['Party A', 'Party B', 'Party C', 'Party D', 'Party E']
initial_strengths = [0.35, 0.25, 0.20, 0.15, 0.05]  # Updated strengths
iterations = 5  # Set iterations to a low number for brevity

# Run the simulation
results, final_party_strength, vote_shares, party_strengths = simulate_election(
    voters, candidates, parties, initial_strengths, iterations
)

results, final_party_strength, vote_shares, party_strengths
