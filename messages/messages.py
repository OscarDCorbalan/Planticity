from protorpc import messages

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    
    
class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_status = messages.StringField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    
    
class GameForms(messages.Message):
    """Return multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    harvest = messages.IntegerField(4, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    action = messages.StringField(1, required=True)
