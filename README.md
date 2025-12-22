# DB_project

- backend is fastapi
- frontend is Svelte + TS + Tailwind CSS

# To run backend
before running backend get into your .venv then run `pip install -r requirements.txt`
run `docker compose down -v` in `/backend`
then run `docker compose up -d`
finally run your fastapi 
for api docs `localhost:8000/docs`

# To run frontend
1. install node.js
2. use `npm install` in `/frontend`
3. use `npm run dev`
4. then you can see the web page in `127.0.0.1:5173` (maybe I forgot)

# For frontend dev
1. always edit in `frontend` branch
2. atomic commit
3. you may want to use AI to generate your commit message
4. always make sure your branch can work then merge it in github (pull request)
5. **DO NOT** merge your branch into `main` in your local
