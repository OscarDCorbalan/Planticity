# Planticity

_This project is part of Udacity's Full Stack Developer Nanodegree._

This project is a game built over Google App Engine and Google Datastore, meant to offer infinite scalability while being platform-agnostic.

The engine is an API with REST endpoints that allow anyone to develop a front-end for the game.

Live at [App Engine](https://planticity-1.appspot.com/_ah/api/explorer)

## Stack developed with:
  - **Language**: [Python](http://python.org)
  - **Cloud PaaS**: [App Engine](https://developers.google.com/appengine)
  - **RESTful API created with**: [Google Cloud Endpoints](https://developers.google.com/appengine/docs/python/endpoints/)
  - **noSQL Database**: [Google Datastore](https://cloud.google.com/datastore/)

# Documentation

## Game Description

Planticity is a game about planting and growing plants to get harvests. Each game begins with a seed, e.g. a pea, which has to be planted and taken care of with a daily 'action' like watering, fertilizing or fumigating, among other actions. As the game progresses, the seed evolves to a growing plant and then to a mature one, which will give you harvest in the form of new fecundated flowers every day, until it ends the end of its life.

'Actions' are sent to the `make_move` endpoint which will reply with the new plant status. Every species needs different care; for example, watering peas too much is a bad idea. Carefully reading the plant status after each action gives hints, as well as keeping track of of how much is it growing, or much it is blossoming, with some given conditions. The `get_game_history` endpoint is useful to read this info if you don't want to care tracking or remembering it.

Possible actions are:
  * **wait**: Do nothing this day.
  * **plant seed**: Plants your seed, which will become a plant after a few days.
  * **water**: Increments water available. Should be around your plant's ideal requirements for an optimum growth.
  * **fungicide**: Removes plagues and prevents future fungi infection for some days, at the expense of incrementing the plant stress.
  * **fumigate**: Removes plagues and prevents future plague infection for some days, at the expense of incrementing the plant stress.
  * **fertilize**: Increases the nutrients present. Can cause toxicity when too high.


Many different Planticity games can be played by many different Users at any given time. Each game can be retrieved or played by using the path parameter `urlsafe_game_key`.

## Set-Up Instructions:

If you want to develop or run locally the game, follow the next steps

**Pre-requirements**:
1. Install [Python 2.7](https://www.python.org/downloads/release/python-2710/) if you don't have it already.
2. Grab a copy of the project. You can either:
  * Clone the repo with git: `git clone https://github.com/OscarDCorbalan/Planticity.git`.
  * [Clone with GitHub Desktop](github-windows://openRepo/https://github.com/OscarDCorbalan/Planticity).
  * [Download the latest release](https://github.com/OscarDCorbalan/Planticity/archive/master.zip)
3. Create a Google Account and register in [Google App Engine](https://appengine.google.com/).
4. Install the [Google App Engine SDK](https://cloud.google.com/appengine/downloads).

**Developing or running locally**:
1. Register (free) for a new application in App Engine.
2. Update the value of application in app.yaml to the app ID you have registered in the App Engine admin console and would like to use to host your instance of this sample.
3. Run the Google App Engine Launcher (installed with the SDK) with the devserver using the main repo directory, and ensure it's running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer).
4. (Optional) Generate your client library(ies) with the endpoints tool.
5. (Optional) Deploy your application!

## Endpoints Included

 - **create_user**
    - Path: 'users'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique.
    - Raises: ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'games'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game.
    - Raises: NotFoundException if user_name does not exist.

 - **get_games**
    - Path: 'games'
    - Method: GET
    - Parameters: -
    - Returns: GameForms, which contains 1 GameForm (current state of the game) for every active game.
    - Description: Return all the games created by the current user.

 - **get_game**
    - Path: 'games/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    - Raises: NotFoundException if the game does not exist.

 - **make_move**
    - Path: 'games/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, action
    - Returns: GameForm with new game state.
    - Description: Accepts an 'action' and returns the updated state of the game, also creating a Move entity will be created, to keep the history of the game. If the action causes a game to end, a corresponding Score entity will be created.
    - Raises: NotFoundException if the game does not exist. BadRequestException if the 'action' is not possible.

 - **delete_game**
    - Path: 'games/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: Message confirming the deletion of the Game.
    - Description: Returns the game moves history.
    - Raises: NotFoundException if the Game does not exist. BadRequestException if the Game is already finished.

 - **get_game_history**
    - Path: 'games/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: MoveForms, which contains 1 MoveForm (date, action, result) for every move in the game.
    - Description: Returns the game history.
    - Raises: NotFoundException if the Game does not exist.

 - **get_rankings**
    - Path: 'scores/rankings'
    - Method: GET
    - Parameters: -
    - Returns: RankingForms.
    - Description: Returns a list of the number of games won by each user, in highest-first order.

 - **get_high_scores**
    - Path: 'scores/leaderboard/{number_of_results}'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: RankingForms.
    - Description: Returns a list of the best scores by each user, in highest-first order. If parameter is present, limits the number of results to the number specified.

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms, which contains 1 ScoreForm per game.
    - Description: Returns all Scores recorded by the provided player, in highest-first order.
    - Raises: Will raise a NotFoundException if the User does not exist.

## Udacity Project Requirements

### Game API Project Overview

_In the Developing Scalable Apps with Python course you learned how to write platform-agnostic apps using Google App Engine backed by Google Datastore. In this project you will use these skills to develop your own game! You will write an API with endpoints that will allow anyone to develop a front-end for your game. Since you aren't required to write a front-end you can use API explorer to test your API_

### Task 1: Explore the Architecture - _DONE_

  - [x] Get the skeleton application up and running.
  - [x] Read through the code and documentation, and test the endpoints with API explorer.
  - [x] Understand how different entities are created, how they work together, and the overall flow.
  - [x] Take a look at the admin Datastore viewer to check out the various entities.

### Task 2: Implement Your Own Game - _DONE_

  - [x] **Create a game**: Come up with a new game to implement! This could be an advanced guessing game such as Hangman, or a simple two player game like Tic-Tac-Toe. We want you to be creative!
  - [x] **Score Keeping**: Define what a "score" for each game will be and keep this data in your database. You can record any other data that you think is interesting or relevant to your particular game.

### Task 3: Extend Your API - _DONE_

  - [x] **get_user_games**: This returns all of a User's active games. You may want to modify the User and Game models to simplify this type of query. Hint: it might make sense for each game to be a descendant of a User.
  - [x] **cancel_game**: This endpoint allows users to cancel a game in progress. You could implement this by deleting the Game model itself, or add a Boolean field such as 'cancelled' to the model. Ensure that Users are not permitted to remove completed games.
  - [x] **get_high_scores**: Remember how you defined a score in Task 2? Now we will use that to generate a list of high scores in descending order, a leader-board! Accept an optional parameter number_of_results that limits the number of results returned.
  - [x] **get_user_rankings**: Come up with a method for ranking the performance of each player. Create an endpoint that returns this player ranking. The results should include each Player's name and the 'performance' indicator (eg. win/loss ratio).
  - [x] **get_game_history**: Your API Users may want to be able to see a 'history' of moves for each game.
    - [x] Define and save game history.
    - [x] Add the capability for a Game's history to be presented. For example: If a User played 'Guess a Number' with the moves: (5, 8, 7), and received messages such as: ('Too low!', 'Too high!', 'You win!'), an endpoint exposing the game_history might produce something like: [('Guess': 5, result: 'Too low'), ('Guess': 8, result: 'Too high'), ('Guess': 7, result: 'Win. Game over')].

### Task 4: Improve Notifications - _DONE_

  - [x] Send an hourly reminder email to every User with an email address that have incomplete games (or some other logic that makes sense).

### Task 5: README and API Documentation

README file should include:
  - [x] Instructions for playing the game
  - [x] Detailed descriptions of each endpoint
  - [x] Remember, you are documenting an API that another programmer may want to use as the basis for a web or mobile app. An api user should not need to read the source code to understand how to use it. You may follow the format of 'Guess a Number' for your README.
  - [x] Create design.txt file, around 500 characters long, explaining: model properties, abd trade-offs/struggles when implementing the game logic.

## Author

[OscarDCorbalan](http://www.oscardc.com)
