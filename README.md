Env setup:
1. Install NodeJs: https://nodejs.org/en/download/package-manager
2. Run command: npm install -g gulp-cli
3. Download base project files from: https://drive.google.com/drive/folders/153wBTMztsTrdUjRDN3iJr5B9NdfQRId9?usp=sharing (overwrite them with files from the repository)
4. While in the root dir of the project run: npm install
5. run: cd src and then gulp serve
6. each time you change something and want to see the changes, run: gulp build

FastApi setup(in cmd):
1. cd (destination to the folder app)\backend
2. python -m venv venv
3. venv\Scripts\activate or on mac/linux source venv/bin/activate
4. uvicorn main:app --reload
