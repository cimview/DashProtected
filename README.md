# DashProtected

## Introduction

DashProtected is a thin wrapper that adds auth capabilities to Dash applications. 
- Login/Logout
- Login Status (timeout, revocation, etc.)
DashProtected is a Dash-only solution, and does not require any knowledge of underlying server architecture or HTTP redirects in order to work.  

DashProtected requires a Dash application, an Auth API object that implements the methods described below, objects that can build a login view and a content view, and a top level layout with a main section and a button with id 'loginout'.

### Dash Application

This is a normal Dash application.

### Auth API object

This is an object with the three methods signatures below.
1. **api_token = get_initial_token(username, password)** This method takes a username or password and returns a unique string api, or None if the user could not be authenticated or was unauthorized. 
2. **api_token = get_token_status(api_token)** This method takes an existing string api token and returns the same if the token is valid, or None if the token is invalid for some reason, ie- the token exceeded some timeout, was revoked on the backend, etc.
3. **invalidate_token(api_token)** This method takes an existing string api token and invalidates it. 

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
- **layout = content_view_builder.build_layout()** This method generates your application layout when logged in, which must also least have elements with ids 'username' and 'password' to keep the callbacks happy; although in the content view they can be dummies.



