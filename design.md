# Design

## Models

One of my first decisions was to separate different models into one model per file and grouping them as a Python module, so modifying different entities would be easier.

The Game model relates a User with a Plant, and at the same time keeps trace of every Move (repeated property).

## Endpoints

In a similar fashion, I separated the "endpoint" logic (in planticity.py) from the "actual game" logic (models module), as the actual web interface shouldn't need to know details of the game implementation.

## Trade-offs / struggles
   
The main struggle was using .json data and a Python dictionary, in such a way that allowed less code to be written when checking conditions and opened the possibility to add more plants very easily.
