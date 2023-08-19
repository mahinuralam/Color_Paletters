# Color_Palettes

This is a Color Palettes creating project. Create using FastApi. For authentication JWT and OAuth2 is being used here.

## Installation

To run this project locally following things need to be installed.

1. Python
2. Pip

## Follow these steps to set up the project:

1. Clone the repository:

```
git clone https://github.com/mahinuralam/Color_Paletters.git
```

2. Navigate to the project directory:

```
cd Color_Paletters
```

3. Install the dependencies:

```
pip install -r requirement.txt
```

Color_Paletters

- By default, the server will start on port 8000. You can access the APIs at http://localhost:8000/docs with Swagger.

## API Routes

The following routes are available in the API:

- POST /register - Provide user credentials to register.
- GET /login - Provide user name and password to loginto the system (Store the access token to varify).
- POST /paletters - Create paletters. (Requires the access token to varify)
- GET /paletters - Get all color paletters.
- POST /paletters/{paletter_id}/favorite - Add favorite. (Requires the access token to varify)

Please refer to the source code and documentation for more details on the API routes and request/response formats.
