1. **/register** - First thing a new users should do is to register itself into the Database
2. **/login** - Prove it can login with the right user/pass

Create the database:
1. Cd to finance, `sqlite3 finance.db` then:
2. `CREATE TABLE users (id INTEGER PRIMARY KEY, name VARCHAR (1, 255), email VARCHAR (1, 255));`