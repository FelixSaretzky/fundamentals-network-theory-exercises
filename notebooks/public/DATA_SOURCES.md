# Data of the exercises

## Exercise 1

`enron_people.csv`, `enron_emails.csv`: emails among Enron executives, November 1998 to
June 2002, as compiled by C. E. Priebe, J. M. Conroy, D. J. Marchette and Y. Park,
"Scan Statistics on Enron Graphs", Computational and Mathematical Organization Theory 11
(2005), from the Enron email corpus released by the US Federal Energy Regulatory
Commission. Email accounts of the same person are merged; `emails` counts the emails from
`sender` to `recipient` (ids are row and column indices).

`attack_uses.csv`: which threat actor uses which technique, from MITRE ATT&CK Enterprise
version 19.2 (https://attack.mitre.org). Sub-techniques are counted as their parent
technique.

© 2026 The MITRE Corporation. This work is reproduced and distributed with the permission
of The MITRE Corporation. MITRE ATT&CK and ATT&CK are registered trademarks of The MITRE
Corporation. License, from the ATT&CK Terms of Use
(https://attack.mitre.org/resources/legal-and-branding/terms-of-use/):

> The MITRE Corporation (MITRE) hereby grants you a non-exclusive, royalty-free license to
> use ATT&CK® for research, development, and commercial purposes. Any copy you make for
> such purposes is authorized provided that you reproduce MITRE's copyright designation
> and this license in any such copy.

## Exercise 2

`as_edges.csv`: the Internet at the level of autonomous systems (AS) on 2 January 2000, as
seen in the BGP logs of the University of Oregon Route Views Project. One row per pair of
ASes that exchange traffic; node ids run from 0 to 6473. The rows are copied unchanged from
the SNAP dataset AS-733, snapshot `as20000102` (https://snap.stanford.edu/data/as-733.html),
including its 1323 self-loops. Source: J. Leskovec, J. Kleinberg and C. Faloutsos,
"Graphs over Time: Densification Laws, Shrinking Diameters and Possible Explanations",
ACM SIGKDD 2005.

`power_edges.csv`: the high-voltage power grid of the western United States. Nodes are
generators, transformers and substations (ids 0 to 4940), an edge is a high-voltage
transmission line. Compiled by D. J. Watts and S. H. Strogatz, "Collective dynamics of
'small-world' networks", Nature 393, 440-442 (1998); obtained from the Netzschleuder
collection (https://networks.skewed.de/net/power), which mirrors M. E. J. Newman's network
data page with the same edges and node ids.

## Exercise 3

`as_edges.csv` and `power_edges.csv`: the same two networks as in Exercise 2.

`karate_edges.csv`, `karate_members.csv`: Zachary's karate club, 34 members (ids 0 to 33) and
the 78 friendships among them. `club` is the group each member joined after the club split:
"Mr. Hi" (the instructor, member 0) or "Officer" (the administrator, member 33). `x` and `y`
are positions for drawing only. Source: W. W. Zachary, "An information flow model for conflict
and fission in small groups", Journal of Anthropological Research 33, 452-473 (1977), as
shipped with NetworkX (`karate_club_graph`).

`power_layout.csv`: positions for drawing the power grid, computed with the stress layout of
Graphviz (`neato -Gmode=sgd`). The data have no geographic coordinates, so the drawing is not
a map.
