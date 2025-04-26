temp read me

intial setup:

1. Clone the repo.

2. Create a virtual environment in the root of the project.
   ```bash
   python -m venv .venv

3. Activate the virtual environment.
On Windows:
.venv\Scripts\activate
On macOS/Linux:
source .venv/bin/activate

4. Install the dependencies.
pip install -r requirements.txt

   
5. Run the following command to start the server:

uvicorn backend.main:app --reload

fast api docs has backend commands for testing

.env version control note:
make an .env file in the root of the project and add the following variables

# .env

ENV_NAME="Development"
BASE_URL="given uvicorn address"
DB_URL="sqlite:///data/urls.db"