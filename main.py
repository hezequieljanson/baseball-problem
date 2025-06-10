# main.py
from baseball import BaseballElimination

be = BaseballElimination("baseball/teams12.txt")

for team in be.teams:
    print(f"{team}: Wins = {be.get_wins(team)}, Losses = {be.get_losses(team)}, Remaining = {be.get_remaining(team)}")
    if be.is_eliminated(team):
        cert = be.certificate_of_elimination(team)
        print(f"{team} is eliminated by the subset R = {{ {' '.join(cert)} }}")
    else:
        print(f"{team} is not eliminated")
