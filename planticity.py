import endpoints
import logging
from messages.messages import (GameForm, GameForms, MakeMoveForm, MoveForms,
                               NewGameForm, RankingForms, ScoreForms,
                               StringMessage)
from models.game import Game
from models.score import Score
from models.user import User
from protorpc import remote, messages
from utils import get_by_urlsafe

LIMIT_RESULTS_REQUEST = endpoints.ResourceContainer(
    number_of_results=messages.IntegerField(1, required=False))
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))


@endpoints.api(name='planticity', version='v1')
class Planticity(remote.Service):
    '''Game API'''

    # /users

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='users',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        '''Create a User. Requires a unique username'''
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')

        user = User(name=request.user_name, email=request.email)
        user.put()

        return StringMessage(
            message='User {} created!'.format(request.user_name))

    # /games

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='games',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        '''Creates new game'''
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        game = Game.new_game(user.key)

        # Use a task queue to update the plant status.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        # taskqueue.add(url='/tasks/cache_plant_status')
        return game.to_form('Good luck playing Planticity!')

    @endpoints.method(response_message=GameForms,
                      path='games',
                      name='get_games',
                      http_method='GET')
    def get_games(self, request):
        '''Return all the games created by the user.'''
        user_email = endpoints.get_current_user().email()
        user_key = User.query(User.email == user_email).get().key
        games = Game.query(Game.user == user_key, Game.game_over == False)
        logging.debug('Number of games retrieved: %s', games.count())
        game_forms = GameForms(items=[game.to_form() for game in games])
        return game_forms

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='games/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        '''Return the current game state.'''
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            # TODO give detail about the plant status
            return game.to_form('Time to take an action!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='games/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        '''Makes a move. Returns a game state with message'''
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        logging.debug('make_move game %s', game)

        if not game:
            raise endpoints.NotFoundException('Game not found!')

        if game.game_over:
            return game.to_form('Game already over!')

        try:
            action_result = game.take_action(request.action)
        except NotImplementedError as e:
            raise endpoints.BadRequestException(e)

        return game.to_form(action_result)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='games/{urlsafe_game_key}',
                      name='delete_game',
                      http_method='DELETE')
    def delete_game(self, request):
        '''Deletes a game iff it's not finished'''
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        logging.debug('delete game %s', game)

        if not game:
            raise endpoints.NotFoundException('Game not found!')

        if game.game_over:
            raise endpoints.BadRequestException("Can't delete a finished game")

        game.key.delete()
        return StringMessage(
            message='Game {} deleted'.format(request.urlsafe_game_key))

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=MoveForms,
                      path='games/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        '''Resturns the game moves history'''
        game = get_by_urlsafe(request.urlsafe_game_key, Game)

        if not game:
            raise endpoints.NotFoundException('Game not found!')

        moves = game.moves
        return MoveForms(items=[move.get().to_form() for move in moves])

    # /scores

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        '''Returns all of an individual User's scores'''
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key).order(-Score.harvest)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=RankingForms,
                      path='scores/rankings',
                      name='get_rankings',
                      http_method='GET')
    def get_rankings(self, request):
        '''Returns user rankings, in best-first order'''
        users = User.query().order(-User.games_won)
        return RankingForms(items=[user.get_ranking() for user in users])

    @endpoints.method(request_message=LIMIT_RESULTS_REQUEST,
                      response_message=ScoreForms,
                      path='scores/leaderboard',
                      name='get_high_scores',
                      http_method='GET')
    @endpoints.method(request_message=LIMIT_RESULTS_REQUEST,
                      response_message=ScoreForms,
                      path='scores/leaderboard/{number_of_results}',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        '''Returns a leaderboard, in score-descending order'''
        scores = Score.query().order(-Score.harvest)
        if request.number_of_results:
            max_results = int(request.number_of_results)
            # Omit negative values
            if max_results > 0:
                # Force an upper bound of 1000 results
                max_results = min(1000, max_results)
                scores = scores.fetch(max_results)
        return ScoreForms(items=[score.to_form() for score in scores])


api = endpoints.api_server([Planticity])
