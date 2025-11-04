Optimal Vaccination Centre Placement

A Streamlit-based web application that uses a Greedy Algorithm to optimally place vaccination centers in a city or region.
The app determines the minimum number of centers needed to cover all areas within a specified coverage distance.

Features

Interactive Streamlit UI
Dynamic graph visualization using NetworkX
Highlights vaccination centers and covered/uncovered nodes
Adjustable coverage distance (X)
Displays population coverage percentage

Algorithm Used – Greedy Approach

The greedy algorithm selects the node that covers the maximum number of uncovered locations within a given distance X.
Once a center is placed, all its reachable nodes are marked covered.
This process repeats until all nodes are covered.

How It Works

Input the number of locations and their populations.
Choose the coverage distance (X).
The app builds a connected graph of locations.
The Greedy algorithm selects optimal center placements.

Visualization shows covered and uncovered areas.
