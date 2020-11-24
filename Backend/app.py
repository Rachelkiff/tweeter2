import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
@app.route("/api/users", methods =["GET", "POST", "PATCH", "DELETE"])
def users():
    if request.method == "GET":
      conn = None
      cursor = None 
      users = None 
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
      except Exception as error:
        print("Something went wrong(This is LAZY!): ")
        print(error)   
      finally:
        if(cursor != None):
         cursor.close()
        if(conn != None):
         conn.rollback()
         conn.close()
        if(users != None):
            return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
        else:
            return Response("Something went wrong.", mimetype="text/html", status=500) 
    elif request.method == "POST": 
      conn = None
      cursor = None 
      user_username = request.json.get("username")
      user_password = request.json.get("password")
      user_email = request.json.get("email")
      user_bio = request.json.get("bio")
      user_birthday = request.json.get("birthday")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user(username, password, email, bio, birthday) VALUES (?, ?, ?, ?, ?)", [user_username, user_password, user_email, user_bio, user_birthday,])
        conn.commit()
        rows = cursor.rowcount
      except Exception as error:
        print("Something went wrong(This is LAZY!): ")
        print(error)   
      finally:
       if(cursor != None):
         cursor.close()
       if(conn != None):
         conn.rollback()
         conn.close()
       if(rows == 1):
          return Response("User creation successfull!", mimetype="text/html", status=201)
       else:
          return Response("Username or email already exists!", mimetype="text/html", status=500) 
    elif request.method == "PATCH":
      conn = None
      cursor = None 
      login_token = request.json.get("login_token")
      user_bio = request.json.get("bio")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        if login_token != "" and login_token != None:
           cursor.execute("UPDATE user SET login_token=? WHERE id=?", [login_token, user_id,])
        if user_bio != "" and user_bio != None:
            cursor.execute("UPDATE user SET bio=? WHERE id=?", [user_bio, user_id,])     
        conn.commit()
        rows = cursor.rowcount
      except Exception as error:
        print("Something went wrong(This is LAZY!): ")
        print(error)     
      finally:
       if(cursor != None):
         cursor.close()
       if(conn != None):
         conn.rollback()
         conn.close()
       if(rows == 1):
          return Response("Updated Success!", mimetype="text/html", status=200)
       else:
          return return Response("There was an error!", mimetype="text/html", status=500)  
    elif request.method == "DELETE":
      conn = None
      cursor = None 
      user_id = request.json.get("id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE id=?", [user_id,])   
        conn.commit()
        rows = cursor.rowcount
      except Exception as error:
        print("Something went wrong(This is LAZY!): ")
        print(error)     
      finally:
       if(cursor != None):
         cursor.close()
       if(conn != None):
         conn.rollback()
         conn.close()
       if(rows == 1):
          return Response("Delete Success", mimetype="text/html", status=204)
       else:
          return Response("Delete Failed!", mimetype="text/html", status=500)      


         
