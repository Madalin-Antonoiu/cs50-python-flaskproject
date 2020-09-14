1. On Desktop, right click and Open with Vs Code, have **VS Code run as admin**
2. In VS Code terminal, type: 

    `
    mkdir flaskproject && cd flaskproject && code .`  

    Then, in the new tab, open terminal and:
    
    `py -m venv venv && cd venv/Scripts/ && . activate && pip install flask && pip install pylint && cd .. && cd .. && mkdir app && cd app && echo > app.py
    `
    

3. Write bare minimum Flask inside _app.py_:

    ```python
    from flask import Flask

    app = Flask(__name__)

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"
    ```

4. From within app folder :

    `export FLASK_APP=app.py && export FLASK_ENV=development&& && flask run`  


  
## Explanation
- `mkdir flaskproject && cd flaskproject && code .` - create directory, cd to it and open new vs code tab into this folder

- `py -m venv venv && cd venv/Scripts/ && . activate` - activate the venv

- `pip install flask && pip install pylint && cd .. && cd .. && mkdir app && cd app && echo > app.py` - install flask and pylint, go to root directory, create app directory, create app. py file inside app dir

## Getting back to the project:
`cd venv/Scripts/ && . activate && cd .. && cd .. && cd app && export FLASK_APP=app.py && export FLASK_ENV=development && flask run
`

https://dev.to/lukeinthecloud/python-auto-reload-using-flask-ci6




### SQL commands:
"C:\sqlite" has been added to environment path so i can use globally sqlite3 command.
You can also use SQLite Studio if you want a GUI.

Being inside of register folder, run sqlite3 data.db
1. SELECT * from registrants; - Read all the entries and iaplay them
2. INSERT INTO registrants (name, email) VALUES ('Bob','bob@sqlite3.com'); - adding new values to the registrants table i created




#### Extra infor :
- templates folder should always be inside app folder
