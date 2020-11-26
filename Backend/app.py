import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import random
import string

app = Flask(__name__)
CORS(app)
def generateToken():
  letters = string.ascli_letters
  result_str = '',join(random.choice(letters)for i in range (40))
  return result_str
@app.route("/api/users", methods =["GET", "POST", "PATCH", "DELETE"])
def users():
    if request.method == "GET":
      conn = None
      cursor = None 
      users = None 
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        if userId != "" and userId != None:
          cursor.execute("SELECT * FROM user WHERE id = ?", [userId,])
        else:
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
            return Response("UserId does not exist.", mimetype="text/html", status=500) 
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
        if(rows == 1):
          userId = cursor.lastrowId
          cursor.execute("INSERT INTO user(login_token, userId) VALUES (?,?)", [result_string, userId,])
          conn.commit()
          rows = cursor.rowcount
          user = {
            "username": username,
            "password": password,
            "email": email,
            "bio": bio,
            "birthday": birthday
          }          
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
      user_username = request.json.get("username")
      user_password = request.json.get("password")
      user_email = request.json.get("email")
      user_bio = request.json.get("bio")
      user_birthday = request.json.get("birthday")
      user_loginToken = request.json.get("loginToken")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT userId FROM user_session WHERE loginToken=?", [user_loginToken,])
        user = cursor.fetchone()
        if user_username != "" and user_username != None:
           cursor.execute("UPDATE user SET username=? WHERE userId=?", [user_username, user[0],])
        if user_password != "" and user_password != None:
            cursor.execute("UPDATE user SET password=? WHERE userId=?", [user_password, user[0],])
        if user_email != "" and user_email != None:
            cursor.execute("UPDATE user SET email=? WHERE userId=?", [user_email, user[0],])
        if user_bio != "" and user_bio != None:
            cursor.execute("UPDATE user SET bio=? WHERE userId=?", [user_bio, user[0],])    
        if user_birthday != "" and user_birthday != None:
            cursor.execute("UPDATE user SET birthday=? WHERE userId=?", [user_birthday, user[0],])
        conn.commit()
        rows = cursor.rowcount
        user = {
            "username": username,
            "password": password,
            "email": email,
            "bio": bio,
            "birthday": birthday
          }          
        cursor.execute


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
          return Response("There was an error!", mimetype="text/html", status=500)  
    elif request.method == "DELETE":
      conn = None
      cursor = None 
      userId = request.json.get("id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE id=?", [userId,])   
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


         
