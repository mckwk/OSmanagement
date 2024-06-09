Frontend setup:
1. Install NodeJs: https://nodejs.org/en/download/package-manager
2. Run command: npm install -g gulp-cli
3. While in the root dir of the project run: npm install
4. run: cd src and then gulp serve
5. each time you change something and want to see the changes, run: gulp build

Backend setup(in cmd):
1. cd (destination to the folder app)\backend
2. python -m venv venv
3. venv\Scripts\activate or on mac/linux source venv/bin/activate
4. pip install -r requirements.txt
5. uvicorn main:app --reload
