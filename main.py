import numpy as np
import pandas as pd
from collections import Counter
np.random.seed(10)
# Constants
N_VOTERS = 1000
N_CANDIDATES = 100
N_PARTIES = 5
N_SEATS = 50
PARTY_VOTE_SHARES = [0.30, 0.25, 0.20, 0.15, 0.10]


# Functions for the electoral model
def generate_ideologies(n, scale=100):
  """Generate random ideologies on a scale from 0 to 100."""
  return np.random.uniform(0, scale, n)


def assign_votes(voters, candidates):
  """Assign each voter to the nearest candidate."""
  votes = np.argmin(abs(voters[:, None] - candidates), axis=1)
  return votes


def join_parties(candidates, parties, party_strength):
  """Candidates join or switch to the nearest party, with a bias towards parties closer to 50% strength."""
  # Calculate the attractiveness of each party to each candidate
  attractiveness = 1 / (abs(candidates[:, None] - parties)*.01 +(0.5 - party_strength)**2)
  # Candidates join the party with the highest attractiveness score
  memberships = np.argmax(attractiveness, axis=1)

  return memberships


def calculate_vote_shares(votes, memberships, n_parties):
  """Calculate the vote shares for each party."""
  party_votes = Counter(memberships[votes])
  vote_shares = np.array([party_votes.get(i, 0)
                          for i in range(n_parties)]) / len(votes)
  return vote_shares


def fptp_district_election(voters, candidates, memberships, n_districts, n_parties):
  """Run a district-based First-Past-The-Post election."""
  district_size = len(voters) // n_districts
  seats = np.zeros(n_parties, dtype=int)
  
  for i in range(n_districts):
      district_voters = voters[i * district_size:(i + 1) * district_size]
      district_votes = assign_votes(district_voters, candidates)
      district_memberships = memberships[district_votes]
      winner_party = Counter(district_memberships).most_common(1)[0][0]
      seats[winner_party] += 1
  
  return seats


def mmm_election(candidates, votes, memberships, n_winners, n_pr_winners):
  """Run a Mixed-Member Majoritarian election."""
  fptp_winners = fptp_district_election(voters, candidates, memberships, N_SEATS, N_PARTIES)
  party_votes = calculate_vote_shares(votes, memberships, N_PARTIES)
  pr_winners = np.argsort(-party_votes)[:n_pr_winners]
  return fptp_winners, pr_winners


def pr_election(vote_shares, n_seats):
  """Run a Proportional Representation election using the D'Hondt method."""
  seats = np.zeros(len(vote_shares), dtype=int)
  for _ in range(n_seats):
    quotients = vote_shares / (seats + 1)
    party = np.argmax(quotients)
    seats[party] += 1
  return seats

def fptp_seats_allocation(memberships, winners, n_seats, n_parties):
  """Allocate FPTP seats to parties based on winners."""
  party_wins = Counter(memberships[winners])
  seats = [party_wins.get(i, 0) for i in range(n_parties)]
  return seats

def mmm_seats_allocation(fptp_winners, pr_winners, memberships, n_seats, n_parties):
  """Allocate MMM seats to parties based on FPTP and PR winners."""
  # Allocate FPTP seats
  fptp_seats = fptp_seats_allocation(memberships, fptp_winners, n_seats - 10, n_parties)
  # Allocate PR seats
  pr_seats = [0] * n_parties
  for winner in pr_winners:
      pr_seats[winner] += 1
  # Combine FPTP and PR seats
  mmm_seats = [fptp_seats[i] + pr_seats[i] for i in range(n_parties)]
  return mmm_seats
# Simulate elections
voters = generate_ideologies(N_VOTERS)
candidates = generate_ideologies(N_CANDIDATES)
parties = np.linspace(0, 100, N_PARTIES)
party_strength = np.array(PARTY_VOTE_SHARES)

print("Starting Party Strength: " + str(party_strength))
print("")

# Initialize a dictionary to hold all election results
all_election_results = {
    'fptp': [],
    'mmm': [],
    'pr': []
}

# Run FPTP elections
for _ in range(3):
  votes = assign_votes(voters, candidates)
  memberships = join_parties(candidates, parties, party_strength)
  fptp_seats = fptp_district_election(voters, candidates, memberships, N_SEATS, N_PARTIES)
  fptp_vote_shares = calculate_vote_shares(votes, memberships, N_PARTIES)
  fptp_strength = fptp_seats / N_SEATS
  all_election_results['fptp'].append({
      'vote_shares': fptp_vote_shares,
      'seats': fptp_seats,
      'strength': fptp_strength
  })
  party_strength = np.array(fptp_strength)

party_strength = np.array(PARTY_VOTE_SHARES)
# Run MMM elections
for _ in range(3):
    votes = assign_votes(voters, candidates)
    memberships = join_parties(candidates, parties, party_strength)
    mmm_winners, mmm_pr_winners = mmm_election(candidates, votes, memberships, N_SEATS, N_SEATS // 2)
    mmm_vote_shares = calculate_vote_shares(votes, memberships, N_PARTIES)
    mmm_seats = mmm_seats_allocation(mmm_winners, mmm_pr_winners, memberships, N_SEATS, N_PARTIES)
    mmm_strength = [s/N_SEATS for s in mmm_seats]
    all_election_results['mmm'].append({
        'vote_shares': mmm_vote_shares,
        'seats': mmm_seats,
        'strength': mmm_strength
    })
    party_strength = np.array(mmm_strength)
party_strength = np.array(PARTY_VOTE_SHARES)
# Run PR elections
for _ in range(3):
    votes = assign_votes(voters, candidates)
    memberships = join_parties(candidates, parties, party_strength)
    pr_vote_shares = calculate_vote_shares(votes, memberships, N_PARTIES)
    pr_seats = pr_election(pr_vote_shares, N_SEATS)
    pr_strength = [s/N_SEATS for s in pr_seats]
    all_election_results['pr'].append({
        'vote_shares': pr_vote_shares,
        'seats': pr_seats,
        'strength': pr_strength
    })
    party_strength = np.array(pr_strength)

# Displaying the results
for election_type, results in all_election_results.items():
    for i, result in enumerate(results, start=1):
        print(f"{election_type.upper()} Election {i}:")
        print(
            f"Total Party Vote Share: {result['vote_shares']}, Seats: {result['seats']}, Strength: {result['strength']}"
        )
    print()

