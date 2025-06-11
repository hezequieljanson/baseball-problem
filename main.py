# main.py
from baseball import BaseballElimination

be = BaseballElimination("baseball/teams12.txt")
for team in be.teams:
    if be.is_eliminated(team):
        cert = be.certificate_of_elimination(team)
        print(f"{team} is eliminated by the subset R = {{ {' '.join(cert)} }}")
    else:
        print(f"{team} is not eliminated")
