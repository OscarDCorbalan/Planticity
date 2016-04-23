# Planticity

_This project is part of Udacity's Full Stack Developer Nanodegree._

This project is a game built over Google App Engine and Google Datastore, meant to offer infinite scalability while being platform-agnostic.
 
The engine is an API with endpoints that allows anyone to develop a front-end for the game.
 
## Purpose of the game

TODO - write: planting seeds and growing plants to get harvests

## Scores

DONE - score is based on harvest

## Requirements

### Game API Project Overview

_In the Developing Scalable Apps with Python course you learned how to write platform-agnostic apps using Google App Engine backed by Google Datastore. In this project you will use these skills to develop your own game! You will write an API with endpoints that will allow anyone to develop a front-end for your game. Since you aren't required to write a front-end you can use API explorer to test your API_

### Task 1: Explore the Architecture **DONE**

Get the skeleton application up and running. Read through the code and documentation, and test the endpoints with API explorer. Make sure you understand how different entities are created, how they work together, and the overall flow. CMake sure to take a look at the admin Datastore viewer to check out the various entities. The datastore is typically at http://localhost:8000, but you may need to access it on another port.

### Task 2: Implement Your Own Game **DONE**

Come up with a new game to implement! This could be an advanced guessing game such as Hangman, or a simple two player game like Tic-Tac-Toe. We want you to be creative!

  * ~~Score Keeping: Define what a "score" for each game will be and keep this data in your database. You can record any other data that you think is interesting or relevant to your particular game.~~

### Task 3: Extend Your API **CURRENT WORK**

  * ~~**get_user_games**: This returns all of a User's active games. You may want to modify the User and Game models to simplify this type of query. Hint: it might make sense for each game to be a descendant of a User.~~
  * **cancel_game**: This endpoint allows users to cancel a game in progress. You could implement this by deleting the Game model itself, or add a Boolean field such as 'cancelled' to the model. Ensure that Users are not permitted to remove completed games.
  * **get_high_scores**: Remember how you defined a score in Task 2? Now we will use that to generate a list of high scores in descending order, a leader-board! Accept an optional parameter number_of_results that limits the number of results returned.
  * **get_user_rankings**: Come up with a method for ranking the performance of each player. Create an endpoint that returns this player ranking. The results should include each Player's name and the 'performance' indicator (eg. win/loss ratio).
  * **get_game_history**: Your API Users may want to be able to see a 'history' of moves for each game. 
    * For example, Chess uses a format called <a href="https://en.wikipedia.org/wiki/Portable_Game_Notation" target="_blank">PGN</a>) which allows any game to be replayed and watched move by move.
    * Add the capability for a Game's history to be presented in a similar way. 
    * Adding this functionality will require some additional properties in the 'Game' model along with a Form, and endpoint to present the data to the User.
    * For example: If a User made played 'Guess a Number' with the moves: (5, 8, 7), and received messages such as: ('Too low!', 'Too high!', 'You win!'), an endpoint exposing the game_history might produce something like: [('Guess': 5, result: 'Too low'), ('Guess': 8, result: 'Too high'), ('Guess': 7, result: 'Win. Game over')].

  * Notificacions:
    * Send an hourly reminder email to every User with an email address that have incomplete games (or some other logic that makes sense).
    * Optional Improvements: implement more sophisticated notifications. For example: "If the User has not made a move in an active game for more than 12 hours, send a reminder email that includes the current game state."

  * Readme:
    * Instructions for playing the game
    * Detailed descriptions of each endpoint

### Other Udacity project requirements :
  * ~~Define what a "score" for each game will be and keep this data in database.~~
  * A well engineered backend; extensible.
  * ~~Each endpoint uses an appropriate HTTP Method.~~



### Reflect on Your Design
Document your design decisions by answering the following questions:
   
- What additional properties did you add to your models and why?
- What were some of the trade-offs or struggles you faced when implementing the new game logic?

These answers should be in a file Design.txt.
Your responses can be in paragraph form or bulleted lists.
This document should be around 500 words long.
