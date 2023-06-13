from dash import dcc, html, Input, Output, State, ctx, no_update


NULL_TOKEN = 'null'


class _CallbackState:
    ''' 
    Manages wrapping and unwrapping of function arguments and outputs 
    (For internal use)
    '''

    def __init__(self, *data):
        ''' 
        Initializes _CallbackState with input data coming from a Dash callback.
        Saves the input data and sets the current API token, which should be 
        the last argument.
        '''
        self.CurrentApiToken = data[-1]
        self.LastApiToken = self.CurrentApiToken
        self.Data = data
        
    def unwrap_input(self):
        ''' 
        Returns argument input expected by wrapped function.  This should be 
        everything EXCEPT the last argument which is the current api token.
        '''
        return self.Data[0:-1]
        
    def wrap_output(self, *data):
        ''' 
        Constructs wrapped output expected by Dash.  For callbacks that have been  
        wrapped with DashProtect, the first two arguments should be the current 
        and previous api tokens.
        '''
        retval = [self.CurrentApiToken, self.LastApiToken]
        retval.extend(*data)
        return tuple(retval)
    

class DashProtected:
    ''' 
    Works with Dash to provide auth capabilities using a token-based 
    backend API 
    '''

    def __init__(self, dash_app, auth_api, login_view_builder, content_view_builder):
        ''' 
        Initializes a wrapper around Dash that provides auth capabilities using
        a backend API. 

        Parameters:

            dash_app: The Dash application being wrapped.

            auth_api: A backend API that supports the following methods:
                         -get_initial_token(username, password) 
                            Returns: string api_token on success, 
                                     or None on failure
                         -get_token_status(api_token) 
                            Returns: same api_token on success, 
                                     or None on invalid token
                         -invalidate_token(api_token):
                            Invalidates token and returns None

            login_view_builder, 
            content_view_builder: View builders for the login screen and the main 
                                  content respectively.  Each must support a method:
                                      -build_layout()
                                          Returns a Dash layout object 

                                  The view returned by login_view_builder must have
                                  text inputs with ids 'username' and 'password.

                                  The view returned by content_view_builder must have
                                  dummy elements with ids 'username' and 'password to 
                                  prevent callback errors; ie- a pair of dcc.Store with '
                                  dummy values can be used.
                                     
        '''
        
        self.DashApp = dash_app
        self.AuthApi = auth_api        
        self.LoginViewBuilder = login_view_builder
        self.ContentViewBuilder = content_view_builder                
                
        # Sets up a dash callback to toggele the view between 
        # login and content based on token values
        self.DashApp.callback(
            Output ('main',              'children'), 
            Output ('user_info_display', 'children'), 
            Input  ('current_api_token', 'data'),
            State  ('last_api_token',    'data'), 
            State  ('user_info',         'data'), 
            State  ('main',              'children')) (self._show_view) 

        # Sets up a dash callback to handle login.  Prevent initial call is required
        # to be true because of the allow duplicate
        self.DashApp.callback(
            Output ('current_api_token', 'data', allow_duplicate=True),
            Output ('last_api_token',    'data', allow_duplicate=True),
            Output ('user_info',         'data', allow_duplicate=True),
            Input  ('login',             'n_clicks'),
            State  ('current_api_token', 'data'),
            State  ('username',          'value'),
            State  ('password',          'value'), prevent_initial_call=True) (self._login)

        # Sets up a dash callback to handle logout.  Prevent initial call is required
        # to be true because of the allow duplicate
        self.DashApp.callback(
            Output ('current_api_token', 'data', allow_duplicate=True),
            Output ('last_api_token',    'data', allow_duplicate=True),
            Output ('user_info',         'data', allow_duplicate=True),
            Input  ('logout',            'n_clicks'),
            State  ('current_api_token', 'data'), prevent_initial_call=True) (self._logout)

        
    def _show_view(self, current_api_token, last_api_token, user_info, existing_layout):
        ''' 
        Returns either the login or the content view if the token changed; 
        otherwise returns the existing view 
        '''
        if last_api_token == current_api_token:
            return no_update, no_update
        elif current_api_token == NULL_TOKEN:
            return self.LoginViewBuilder.build_layout(), NULL_TOKEN
        else:
            return self.ContentViewBuilder.build_layout(), user_info


    def _login(self, n, current_api_token, username, password):
        ''' 
        Processes the api token in response to login 
        '''
        last_api_token = current_api_token
        new_api_token = self.AuthApi.get_new_token(username, password)
        user_info = username
        if new_api_token is None:
            new_api_token = NULL_TOKEN
            user_info = NULL_TOKEN
        return new_api_token, last_api_token, user_info


    def _logout(self, n, current_api_token):
        ''' 
        Processes the api token in response to login or logout 
        '''
        if n is None:  # Protect against spurious invocations not related to clicking the button
            return no_update, no_update, no_update
        last_api_token = current_api_token
        self.AuthApi.invalidate_token(current_api_token)
        return NULL_TOKEN, last_api_token, NULL_TOKEN


    @staticmethod
    def _wrap(*specifiers):
        ''' 
        Adds input/output dependencies to wrapped Dash callback to handle api tokens 
        (For internal use)
        ''' 
        retval = [ 
            Output('current_api_token', 'data', allow_duplicate=True),    # maps to a toplevel dcc.Store
            Output('last_api_token',    'data', allow_duplicate=True)     # maps to a toplevel dcc.Store
        ]
        retval.extend(specifiers)
        retval.append(
            State('current_api_token', 'data')
        )
        return retval

    
    def callback(self, *args):
        ''' 
        A decorator that handles API tokens.  Use this descorator when the 
        wrapped callback should check tokens for validity, expiry, etc. An 
        expired or revoked token will trigger a state change and cause the 
        login view to be displayed.

        If the callback does NOT require API token checking, use the usual
        Dash callback instead.        
        '''
        def wrap_func(func):
        
            def apply_func(*func_args):
                dpcs = _CallbackState(*func_args)
                unwrapped_args = dpcs.unwrap_input()

                output_data = func(*unwrapped_args)
                if not isinstance(output_data, tuple) or len(output_data) == 1:
                    output_data = [ output_data ]                
                
                dpcs.CurrentApiToken = self.AuthApi.get_token_status(dpcs.CurrentApiToken)
                if dpcs.CurrentApiToken is None:
                    dpcs.CurrentApiToken = NULL_TOKEN

                retval = dpcs.wrap_output(output_data)
                return retval
        
            return self.DashApp.callback(DashProtected._wrap(*args), 
                prevent_initial_call=True) (apply_func)

        return wrap_func
    
