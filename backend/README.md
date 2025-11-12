# To Start PostgreSQL with Docker
This `docker-compose.yml` file sets up a PostgreSQL database
You should add a `.env` file in the same directory with the following content:

```
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database_name
```
Replace `your_username`, `your_password`, and `your_database_name` with your desired PostgreSQL credentials.

To start the PostgreSQL service, run the following command in the terminal:

```bash
docker-compose up -d
```

to get into the postgres container, run:

```bash
docker exec -it my_postgres_db psql -U your_username -d your_database_name
```

# To start the backend server

## virtual environment
Create a virtual environment and activate it:

```bash
python -m venv DB_env
source DB_env/bin/activate # On Windows use `DB_env\Scripts\activate`
```
## Install dependencies
Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

## Start the server
Run the FastAPI server using Uvicorn:
```bash
uvicorn app.main:app --reload
```
The server will be accessible at `http://127.0.0.1:8000`

