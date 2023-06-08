# DashProtected

## Introduction

DashProtected is a thin wrapper that adds auth capabilities to new or existing Dash applications. 
- Login/Logout
- Login Status (timeout, revocation, etc.)

DashProtected is a Dash-only solution, and does not require any knowledge of the underlying server or HTTP protocol in order to work.  All you need to provide are 
- a Dash application with a layout containing a div with id 'main', a button with id 'loginout', and storage for api tokens
- an auth API object that implements the methods described below
- objects that can build a login view and a content view

The application will be protected with a login screen.  If it is also desired for a callback to check the status of a login session for expiry or revocatiom, simply use the callback decorator from the DashProtected instance.  Otherwise, use the callback decorator from the native Dash app.    

### Dash Application

This is a normal Dash application that has a div with id 'main', a button with id 'loginout', and storage for two api tokens. Tha main div will contain a login screen when the user is logged out, and will contain the application content when the user is logged in.  Example:
```
    html.Div([
                html.Div(id='main', children=[login or content view]),
                html.Button(id='loginout', children='Log In/Out'), 
                dcc.Store(id='current_api_token', storage_type='session', data=NULL_TOKEN),
                dcc.Store(id='last_api_token', storage_type='session', data=NULL_TOKEN),
            ])
```
If this is being used on an existing Dash application, your existing layout will probbably be served up by the Content view builder below.  This could be a simple cut and paste operation.

### Auth API object

This is an object with the three methods signatures below.
1. **api_token = get_initial_token(username, password)** This method takes a username or password and returns a unique string api, or None if the user could not be authenticated or was unauthorized. 
2. **api_token = get_token_status(api_token)** This method takes an existing string api token and returns the same if the token is valid, or None if the token is invalid for some reason, ie- the token exceeded some timeout, was revoked on the backend, etc.
3. **invalidate_token(api_token)** This method takes an existing string api token and invalidates it. 

The auth API object can implement simple login functionality such as the hardcoded functionality below, or it can 

### Login view builder

This is an object with the following method signature.
- **layout = login_view_builder.build_layout()** This method generates a login screen layout, which must at least have text input elements with ids 'username' and 'password'.
Example:
```
    class LoginLayoutBuilder:
        def build_layout(self, options=None):
            return [ 
                html.Label(id='username_label', htmlFor='username', children='Email Address:'),
                dcc.Input(id='username', type='text'),
                html.Label(id='password_label', htmlFor='password', children='Password:'),
                dcc.Input(id='password', type='password')
            ]
```

### Content view builder

This is an object with the following method signature.
- **layout = content_view_builder.build_layout()** This method generates your application layout when logged in, which must also least have elements with ids 'username' and 'password' to keep the callbacks happy; although in this view they can be dummies.
```
class ContentLayoutBuilder:
    def build_layout(self, options=None):    
        return [
            dcc.Checklist(id='chk1', options=['One', 'Two', 'Three'], value = 'Two'),
            html.Button(id = 'reset', children = 'Reset'),
            dcc.Store(id='username', data='dummy'),
            dcc.Store(id='password', data='dummy')
        ]
```

## Usage

- Import DashProtected and NULL_TOKEN from the DashProtected module.
- Create a Dash app as usual, eg- ``` app = Dash(__name__)``` with layout as specified above. (Use NULL_TOKEN as the initial API token values.)
- Create instances of the Auth Api, LoginViewBuilder and ContentViewBuilder
- Create DashProtected instance with the Dash instance, the Auth Api instance, and view builders.
- Any callbacks that should check login status should use the dash protected instance callback decorator.  Otherwise use the Dash instance callback decorator as usual.

## Example

A complete example can be found in the examples/DashProtectedExample.py.

## Considerations

DashProtected is a Dash-only auth solution that works by obtaining and storing a token, and by changing the layout in a subsequent callback when the token changes.  The solution can be hardened agaist token spoofing or token replay attacks by taking suitable care that the Auth Api is checking token validity rigorously.  

Advantages that DashProtected has over Basic Auth include the ability to style the login screen and to actually log out without closing the browser window.  

Disadvantages include the addition of more parameters to Dash callbacks, and some constraints (albeit light ones) on the application layout.

## Known Issues

Specific browser gymnastics can sometimes result in username and password text inputs becoming unmoored from the React.js Dash frontend.  The symptoms are that a correct username/password pair is entered but the backend gets empty inputs, and thus a bad login.  The solution is to refresh the login screen and re-enter the username password.

Some callback return values that appear as a list may have items appended to the output instead of the list. The symptom is that a Dash schema exception is thrown on the backend, and the solution is to return embed the calback values into another list.    

