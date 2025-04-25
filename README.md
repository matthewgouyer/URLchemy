temp read me

run the following command to start the server

uvicorn shortener_app.main:app --reload


.env version control note:
make an .env file in the root of the project and add the following variables

# .env

ENV_NAME="Development"
BASE_URL="given uvicorn address"
DB_URL="sqlite:///data/urls.db"