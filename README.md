# DashProtected

## Introduction

DashProtected is a thin wrapper that adds auth capabilities to Dash applications. 
- Login/Logout
- Login Status (timeout, revocation, etc.)
DashProtected is a Dash-only solution, and does not require any knowledge of underlying server architecture or HTTP redirects in order to work.  

DashProtected requires a Dash application, an Auth API object that implements the methods described below, and objects that can build a login view and a content view.

### Dash Application

This is a normal Dash application.

### Auth API object

This is an object with the three methods signatures below.
1. *api_token = get_initial_token(username, password)*  
2. api_token = get_token_status(api_token)
3. invalidate_token(api_token)

