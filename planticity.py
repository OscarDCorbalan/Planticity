import logging
import endpoints
from protorpc import remote, messages
from models import StringMessage, User

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

@endpoints.api(name='planticity', version='v1')
class Planticity(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        # TODO Check if user exists: throws exception

        # Create user
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

   
api = endpoints.api_server([Planticity])
