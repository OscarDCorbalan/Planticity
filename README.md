# Planticity

_This project is part of Udacity's Full Stack Developer Nanodegree._

This project is a game built over Google App Engine and Google Datastore, meant to offer infinite scalability while being platform-agnostic.
 
The engine is an API with endpoints that allows anyone to develop a front-end for the game.
 
### Purpose of the game

TODO - write: planting seeds and growing plants to get harvests

### Scores

DONE - score is based on harvest

### Requirements

Some Udacity project requirements :
  * ~~Define what a "score" for each game will be and keep this data in database.~~
  * A well engineered backend; extensible.
  * ~~Each endpoint uses an appropriate HTTP Method.~~
  * ~~Get user games:returns all of a User's active games.~~
  * Cancel game: this endpoint allows users to cancel a game in progress. Ensure that Users are not permitted to remove *completed* games.
  * Get high scores: generate a list of high scores in descending order, a leader-board! Accept an optional parameter `number_of_results` that limits the number of results returned.    
  * Get user rankings: method for ranking the performance of each player. The results should include each Player's name and the 'performance' indicator (eg. win/loss ratio).
  * Get game history: see a 'history' of moves for each game. 
    * For example, Chess uses a format called <a href="https://en.wikipedia.org/wiki/Portable_Game_Notation" target="_blank">PGN</a>) which allows any game to be replayed and watched move by move.
    * Add the capability for a Game's history to be presented in a similar way. 
    * Adding this functionality will require some additional properties in the 'Game' model along with a Form, and endpoint to present the data to the User.

Notificacions:
  * Send an hourly reminder email to every User with an email address that have incomplete games (or some other logic that makes sense).
  * Optional Improvements: implement more sophisticated notifications. For example: "If the User has not made a move in an active game for more than 12 hours, send a reminder email that includes the current game state."

Readme:
  * Instructions for playing the game
  * Detailed descriptions of each endpoint

### Reflect on Your Design
Document your design decisions by answering the following questions:
   
- What additional properties did you add to your models and why?
- What were some of the trade-offs or struggles you faced when implementing the new game logic?

These answers should be in a file Design.txt.
Your responses can be in paragraph form or bulleted lists.
This document should be around 500 words long.
