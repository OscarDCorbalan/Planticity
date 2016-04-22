import endpoints
import logging
from google.appengine.ext import ndb
from messages.messages import (GameForm, GameForms, MakeMoveForm, NewGameForm,
    StringMessage)
from models.game import Game
from models.user import User
from protorpc import remote, messages
from utils import get_by_urlsafe

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
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        '''Create a User. Requires a unique username'''
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')

        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))


    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
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

        if game.game_over:
            return game.to_form('Game already over!')

        try:
            action_result = game.take_action(request.action)
        except NotImplementedError as e:
            raise endpoints.BadRequestException(e)

        return game.to_form(action_result)

api = endpoints.api_server([Planticity])
