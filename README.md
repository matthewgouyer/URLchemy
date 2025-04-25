temp read me

.env version control note:
If you’re sharing your code with other developers, then you may want to show in your repository what their .env files should look like. In that case, you can add .env_sample to your version control system. In .env_sample, you can store the keys with placeholder values. To help yourself and your fellow developers, don’t forget to write instructions in your README.md file on how to rename .env_sample and store the correct values in the file.

# .env

ENV_NAME="Devolopment"
BASE_URL="given uvicorn address"
DB_URL="sqlite:///data/urls.db"