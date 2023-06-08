from dash import Dash, dcc, html, Input, Output, State
from DashProtected import DashProtected, NULL_TOKEN
import uuid


class DummyAuthApi:
    ''' 
    Example AuthApi for DashProtected. This has a hardcoded set of valid 
    usernames and passwords, and invalidates tokens after five usages.
    
    This is a demobstration implementation only.  A production implementation
    should call a real backend API to authenticate/authorize users and 
    invalidate tokens.    
    '''
    def __init__(self):
        ''' Sets up valid user list and sets usage count to 0. '''
        self.Count = 0
        self._LoginData = {'Alice'   : 'AlicePassword',
                           'Bob'     : 'BobPassword',
                           'Charlie' : 'CharliePassword'}
                           

    def get_new_token(self, username, password):
        ''' Returns a GUID if info matches the hardcoded list, or returns None '''
        if username in self._LoginData and password == self._LoginData[username]:
            return str(uuid.uuid1())
        else:
            return None

            
    def get_token_status(self, api_token):
        ''' Returns the given api token is usages are under 5, or returns None '''
        self.Count = self.Count + 1
        if self.Count >= 5:
            self.Count = 0
            return None
        return api_token


    def invalidate_token(self, api_token):
        ''' Sets the usage count back to zero for the next login. '''
        self.Count = 0
            

class LoginViewBuilder:    
    ''' 
    Example that contains a method that builds a layout with user/pass text 
    inputs to be shown when the user is logged out. 
    '''
    def build_layout(self, options=None):
        ''' Returns an example layout with user/pass text inputs. '''
        return [ 
            html.Label(id='username_label', htmlFor='username', children='Email Address:'),
            dcc.Input(id='username', type='text'),
            html.Label(id='password_label', htmlFor='password', children='Password:'),
            dcc.Input(id='password', type='password')
        ]


class ContentViewBuilder:
    ''' 
    Example that contains a method that builds a layout with application 
    content to be shown when the user is logged in. 
    '''
    def build_layout(self, options=None):
        ''' 
        Returns a layout with application content to be shown when the user is 
        logged in. In this example, it is a single checkbox with a rest button. 
        ''' 
        return [
            dcc.Checklist(id='chk1', options=['One', 'Two', 'Three'], value = 'Two'),
            html.Button(id = 'reset', children = 'Reset'),
            dcc.Store(id='username', data='dummy'),  # Needed to process callback
            dcc.Store(id='password', data='dummy')   # Needed to process callback
        ]


# Create Dash Application
app = Dash(__name__)

# Instantiate the view builders
login_view_builder = LoginViewBuilder()
content_view_builder = ContentViewBuilder()

# Set toplevel app layout with initial view set to login view
app.layout = html.Div([
    html.Div(id='main', children=login_view_builder.build_layout()),
    html.Button(id='loginout', children='Log In/Out'), 
    dcc.Store(id='current_api_token', storage_type='session', data=NULL_TOKEN),
    dcc.Store(id='last_api_token', storage_type='session', data=NULL_TOKEN),
])

# Create an auth api instance
auth_api = DummyAuthApi()

# Create a protected wrapper around the dash application that adds login
# and logout capabilities
dash_protected = DashProtected(app, auth_api, login_view_builder, content_view_builder)

# If per-call token checking is a desired feature, then decorate the handler 
# with the @dash_protected version of the callback.  If this is not a desired 
# feature then just use the @app.callback as usual.
@dash_protected.callback(
    Output('chk1', 'value'),
    Input('reset', 'n_clicks'),
    State('chk1', 'value'))
def reset(n, chk1value):
    output_data = ['One','Three']        
    return output_data
        

if __name__ == '__main__':
    app.run_server()
