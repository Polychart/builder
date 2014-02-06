Overview of OAuth 2.0 in Polychart
==================================
The OAuth 2.0 protocol is used in the Polychart Query package in implementing
the Google Analytics data sources (Salesforce no longer supported). These data
sources differ from others in two parts: first, with regards to *creating* a
new data source, OAuth data sources require the user to authenticate Polychart
through their own credentials with an external account; and second, after
authentication, all requests are handled by means of OAuth entities known as
tokens.

OAuth 2.0 Authentication Flow
-----------------------------
Polychart uses a server-side authentication flow, which amounts to having the
Polychart backend obtain tokens from the service provider after the user has
logged in on the service provider end. In this section, the overall process for
authentication, as implemented in the Polychart Query package, will be detailed.

    ╭────────────────────────────────────────────────────────────────────╮
    │ User/Browser ─── CREATE DATA SOURCE REQUSET ─── Polychart Server   │
    │                                                        │           │
    │                                                    REDIRECT TO     │
    │                                                   AUTH ENDPOINT    │
    │                                                        │           │
    │ OAuth Provider ───── REDRIECT w/ CALLBACK URL ───── User/Browser   │
    │       │                                                            │
    │     USER                                                           │
    │ AUTHENTICATION                                                     │
    │       │                                                            │
    │ OAuth Provider ──────── REDIRECT w/ CODE ──────── Polychart Server │
    │                                                          │         │
    │                                                    POST REQUEST    │
    │                                                     w/ CODE AND    │
    │                                                   CLIENT SECRET/ID │
    │                                                          │         │
    │ Polychart Server ─── RESPONSE w/ REFRESH TOKEN ─── OAuth Provider  │
    │        │                                                           │
    │   HTTP RESPONSE                                                    │
    │    FOR SUCCESS                                                     │
    │        │                                                           │
    │   User/Browser                                                     │
    ╰────────────────────────────────────────────────────────────────────╯
         Figure 1. Schemeatic view of OAuth authentication process.

1. When the user tries to *Create a Datasource* which is an OAuth data
   source---namely, a Google Analytics connection. The user is
   then redirected to the service provider's OAuth 2.0 authentication URL, from
   which the user logs in and chooses whether or not to grant Polychart
   permissions to access his or her data.
    - This step is primarily frontend code: the user steps through the Data
      Source creation form and inputs any additional settings requested (a
      Google Analytics profile ID, for instance); then, the client sends a POST
      to the `/data-source/create` URL containing information about the type of
      data source to be created and any additional information provided. This
      information is then processed by the corresponding view handler function.

2. After the request to create an OAuth data source is received and processed by
   the backend, an HTTP response containing the field `redirect` is returned to
   the client. The value of this field will be the OAuth 2.0 authentication URL
   for the service provider in question.
    - Note that there are some additional pieces to the authentication URL that
      we redirect the client to. In particular, the type of request, a callback
      URL, an OAuth Client ID and other information are appended as part of the
      query string. See the function `oauthRedirect` in `oauth.py` for more
      details.

3. At this point, the user is redirected by the frontend to the off-site
   authentication endpoint, where the user logs in to their account and may or
   may not authorize Polychart. Supposing that authentication is successful,
   the client is redirected back to `/api/data-source/callback` along with some
   data a query string. This query string is scraped and passed back to the
   server at `/data-source/create`. Note that this is the same endpoint that the
   data source creation form POSTs to.
    - Unfortunately, since information is stored in the query string, the
      processing for this is done frontend.
      See `/server/polychart/main/templates/callback.tmpl` for more details.

4. The server receives this data source creation request, but this time,
   recognizes that this comes from the client after they have authorized with
   the service provider. This is known since the field `code` is in the body of
   this new request. The `code` is passed to the function `oauthCallback`, found
   in `/server/polychartQuery/oauth.py` and an HTTP request to the service
   provider for an OAuth 2.0 *Access Token*, and perhaps a *Refresh Token* as
   well. At this point, the data source has not been fully created.`
    - An *Access Token* is a code passed between Polychart and the service
      provider to indicate that we are authorized by the user.
    - A *Refresh Token* is another code which allows us to ask the service
      provider for more Access Tokens at any time. A Refresh Token cannot be
      used for data transactions. This entity should be secured and stored.

5. The service provider responds to the above HTTP request with an Access Token
   and, usually, a Refresh Token. The Refresh Token is stored in the data base,
   and at this point, the data source creation has been completed. The backend
   responds to the Dashboard Builder home with the appropriate success response.

There are a few other notes to the creation process. All OAuth 2.0 providers
require some sort of OAuth Client ID and OAuth Client Secret to be included in
the HTTP requests made during the authentication process. These credentials can
usually be obtained by registering for the equivalent of API keys at the service
provider.

Also, the redirect URL that is sent during the initial authentication step is
very important. This URL must be an `https` location, and must match the
redirect URL registered with the service provider, upon registering for the
client ID and client secret.

Querying an OAuth 2.0 Data Source
---------------------------------
Besides handling the creation of an OAuth 2.0 data source, the Polychart Query
Package must also deal with querying data from these service providers. The flow
of initializing a data source connection upon launching a dashboard and then
querying data for the creation of a chart is outlined here.

1. Everything begins when the user opens up a dashboard that is connected with
   an OAuth data source. Upon opening up this dashboard, the backend establishes
   a connection with the OAuth service provider, in the sense that the backend
   uses the stored Refresh Token to obtain a new Access Token for this session.
   Once a new Access Token is obtained, additional information such as query
   endpoints and user data is requested from the service provider and stored
   accordingly. At this point, the dashboard has loaded.
    - The client code also asks the backend to provide a list of tables to
      populate the data panel, but the details of this differ on a case-to-case
      basis; see the `listTables` method in each implementation for more detail.

2. When the user goes to create a chart, the frontend sends a query spec to the
   backend. This internal query spec is translated to a data query format
   required by the specific data source, and a request is made. These requests
   generally look like a GET request sent to a particular endpoint, containing
   both the Access Token obtained that session and the translated query.

3. The service provider responds to the request, and the data is processed,
   formatted and returned to the frontend.

Generally speaking, the process of obtaining data is straightforward, and akin
to any other data source. The major difference with OAuth data sources, and say,
a database, is that the concept of a "connection" is much more abstract; the
connection is represented almost entirely by a valid Access Token, as opposed to
a data source connection object. Of course, wrapping the implementation of the
data source connection well enough, it is possible to abstract away the details
to the end user.

Further References
------------------
For additional details, the [Google OAuth2 Web Server] [0] documentation is a
good introduction to the overall process.

[0]: https://developers.google.com/accounts/docs/OAuth2WebServer
