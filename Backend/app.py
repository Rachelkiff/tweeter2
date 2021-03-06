import mariadb
from flask import Flask, request, Response
import json
import dbcreds
from flask_cors import CORS
import random
import string
import datetime

app = Flask(__name__)
CORS(app)
def generateToken():
  letters = string.ascii_letters
  result_str = ''.join(random.choice(letters)for i in range (40))
  return result_str

# Users Endpoint
@app.route("/api/users", methods =["GET", "POST", "PATCH", "DELETE"])
def usersendpoint():
    if request.method == "GET":
      conn = None
      cursor = None
      users = None
      userId = request.args.get("userId")
      rows = None
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
        if(rows):
          user = {
            "userId": row[0],
            "email": row[3],
            "username": row[1],
            "bio": row[4],
            "birthday": row[5]
          }           
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
          cursor.execute("INSERT INTO user_session(login_token, userId) VALUES (?,?)", [generateToken(), userId,])
          conn.commit()
          rows = cursor.rowcount
          user = {
            "username": user_username,
            "password": user_password,
            "email": user_email,
            "bio": user_bio,
            "birthday": user_birthday
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
          return Response(json.dumps(user, default=str), mimetype="text/html", status=201)
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
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchone()
        if user_username != "" and user_username != None:
           cursor.execute("UPDATE user SET username=? WHERE id=?", [user_username, user[0],])
        if user_password != "" and user_password != None:
            cursor.execute("UPDATE user SET password=? WHERE id=?", [user_password, user[0],])
        if user_email != "" and user_email != None:
            cursor.execute("UPDATE user SET email=? WHERE id=?", [user_email, user[0],])
        if user_bio != "" and user_bio != None:
            cursor.execute("UPDATE user SET bio=? WHERE id=?", [user_bio, user[0],])    
        if user_birthday != "" and user_birthday != None:
            cursor.execute("UPDATE user SET birthday=? WHERE id=?", [user_birthday, user[0],])
        conn.commit()
        rows = cursor.rowcount
        cursor.execute("SELECT * FROM user WHERE id=?", [user[0],])
        user = cursor.fetchone()
      except Exception as error:
        print("Something went wrong(This is LAZY!): ")
        print(error)     
      finally:
        if(conn != None):
         conn.close()
        if(conn != None):
         conn.rollback()
         conn.close()
        if(rows == 1):
          user = {
            "userId": user[0],
            "username": user_username,
            "password": user_password,
            "email": user_email,
            "bio": user_bio,
            "birthday": user_birthday
          }
          return Response("Updated Success!", mimetype="text/html", status=200)
        else:
          return Response("There was an error!", mimetype="text/html", status=500)  
    elif request.method == "DELETE":
      conn = None
      cursor = None 
      user_password = request.json.get("password")
      user_loginToken = request.json.get("loginToken")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchone()
        print(user)
        cursor.execute("DELETE FROM user WHERE id=? AND password=?", [user[0], user_password,])
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
          return Response("Delete Success!", mimetype="text/html", status=204)
        else:
          return Response("Login token or password not valid!", mimetype="text/html", status=500)     

#Login Endpoint
@app.route("/api/login", methods =["POST", "DELETE"])      
def loginendpoint():  
    if request.method == "POST": 
      conn = None
      cursor = None 
      user_password = request.json.get("password")
      user_email = request.json.get("email")
      rows = None
      user = None
      user_id = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE password=? AND email=? (password, email)", [user_password, user_email,])
        user = cursor.fetchall()
        print(user)
        rows = cursor.rowcount
        if(rows == 1):
          cursor.execute("INSERT INTO user_session(login_token, userId) VALUES (?,?)", [generateToken, userId,])
          conn.commit()
          rows = cursor.rowcount
          user = cursor.fetchall()
          user = {
            "userId": user[0],
            "username": user_username,
            "password": user_password,
            "email": user_email,
            "bio": user_bio,
            "birthday": user_birthday,
            "login_token": login_token
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
          return Response("User login successfull!", mimetype="text/html", status=201)
        else:
          return Response("Information entered is not valid!", mimetype="text/html", status=500) 
    elif request.method == "DELETE":
      conn = None
      cursor = None 
      user = None
      user_loginToken = request.json.get("loginToken")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_session WHERE login_token=?", [user_loginToken,])
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
          return Response("Delete Success!", mimetype="text/html", status=204)
        else:
          return Response("Login token invalid!", mimetype="text/html", status=500) 

#Follow Endpoint
@app.route("/api/follow", methods =["GET","POST", "DELETE"])  
def followendpoint():  
    if request.method == "GET":
      conn = None
      cursor = None
      users = None
      userId = request.args.get("userId")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        if userId != None:
          cursor.execute("SELECT user.id, user.email, user.username, user.bio, user.birthday FROM user INNER JOIN follow ON user.id = follow.follow_id WHERE follow.follow_id =?", [userId,])
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
        if(users != None or users == []):
          for user in users:
            user = {
            "userId": user[0],
            "username": user_username[2],
            "email": user_email[1],
            "bio": user_bio[3],
            "birthday": user_birthday[4],
          }
            user.append[users]
          return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
        else:
          return Response("UserId does not exist.", mimetype="text/html", status=500) 
    if request.method == "POST": 
      conn = None
      cursor = None 
      user_loginToken = request.json.get("loginToken")
      follow_id = request.json.get("follow_id")
      rows = None
      user_id = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT userId FROM user u INNER JOIN user_session us ON u.userId=us.userId WHERE loginToken=?", [user_logintoken,])
        user_id = cursor.fetchall()[0][0]
        rows = cursor.rowcount
        if(rows == 1):
          cursor.execute("INSERT INTO follow(userId, followId) VALUES (?,?)", [user_id, follow_id,])
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
          return Response("User follow successfull!", mimetype="text/html", status=201)
        else:
          return Response("There was an error!", mimetype="text/html", status=500) 
    elif request.method == "DELETE":
      conn = None
      cursor = None 
      user = None
      user_loginToken = request.json.get("loginToken")
      follow_id = request.json.get("follow_id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_session WHERE login_token=?", [user_loginToken,])
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
          return Response("Delete Success!", mimetype="text/html", status=204)
        else:
          return Response("Login token invalid!", mimetype="text/html", status=500) 

#Followers Endpoint
@app.route("/api/followers", methods =["GET"])  
def followersendpoint():  
    if request.method == "GET":
      conn = None
      cursor = None
      users = None
      user_id = request.args.get("user_id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        if userId != None:
          cursor.execute("SELECT user.id, user.email, user.username, user.bio, user.birthday FROM user INNER JOIN follow ON user.id = follow.follow_id WHERE follow.follow_id =?", [userId,])
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
        if(users != None or users == []):
          for user in users:
            user = {
            "userId": user[0],
            "username": user_username[2],
            "email": user_email[1],
            "bio": user_bio[3],
            "birthday": user_birthday[4],
          }
            user.append[users]
          return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
        else:
          return Response("UserId does not exist.", mimetype="text/html", status=500)  

#Tweet Endpoint
@app.route("/api/tweet", methods =["GET", "POST", "PATCH", "DELETE"])
def tweetendpoint():
    if request.method == "GET":
      conn = None
      cursor = None
      users = None
      user_id = request.json.get("user_id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        if userId != "" and userId != None:
          cursor.execute("SELECT * FROM user WHERE id = ?", [user_id,])
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
       user_loginToken = request.json.get("loginToken")
       tweet_content = request.json.get("content")
       created_at = datetime.date.today()
       rows = None
       try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchone()
        print(user)
        cursor.execute("INSERT INTO tweet(user_id, content, created_at) VALUES (?,?,?)", [user[0], tweet_content, created_at])
        conn.commit()
        rows = cursor.rowcount
        tweetId = cursor.lastrowId        
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
          user = {
            "tweetId": tweetId,
            "userId": user[0][0],
            "content": tweet_content,
            "createdAt": created_at,
          }
          return Response("Tweet was created successfully!", mimetype="text/html", status=201)
        else:
          return Response("Login Token is not valid!", mimetype="text/html", status=500)
    elif request.method == "PATCH":
       conn = None
       cursor = None 
       user_loginToken = request.json.get("loginToken")
       tweet_content = request.json.get("content")
       tweetId = request.json.get("tweet_id")
       rows = None
       try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchall()
        cursor.execute("UPDATE tweet SET content=? WHERE id=? AND user_id=?" , [tweet_content, user[0], ])
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
          user = {
            "tweetId": tweetId,
            "content": tweet_content,
           }
          return Response("Tweet was updated successfully!", mimetype="text/html", status=200)
        else:
          return Response("Login Token is not valid!", mimetype="text/html", status=500)
    elif request.method == "Delete":
       conn = None
       cursor = None 
       user_loginToken = request.json.get("loginToken")
       tweetId = request.json.get("tweet_id")
       rows = None
       try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchone()
        cursor.execute("DELETE FROM tweet WHERE id=? AND userId=?", [tweet_id, user[0],])
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
          user = {
            "tweetId": tweetId,
            "content": tweet_content,
           }
          return Response("Deleted successfully!", mimetype="text/html", status=204)
        else:
          return Response("Login Token is not valid!", mimetype="text/html", status=500)


#Comment Endpoint
@app.route("/api/comment", methods =["GET", "POST", "PATCH", "DELETE"])
def commentendpoint():
    if request.method == "GET":
      conn = None
      cursor = None
      users = None
      tweet_id = request.args.get("tweet_id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        if tweet_id != "" and tweet_id != None:
          cursor.execute("SELECT * FROM comment c INNER JOIN tweet t ON c.tweetId = t.id")
        else:
          cursor.execute("SELECT * FROM comment c INNER JOIN tweet t ON c.tweetId = t.id WHERE tweetId=?", [tweet_id,])
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
         if(users != None or users == []):
           for user in users:
            user = {
            "commentId": comment_id[0],
            "tweetId": tweet_id[2],
            "userId": user_id[1],
            "content": tweet_content[3],
            "createdAt": created_at[4],
            "username": user_username[6]
          }
            user.append[users]
            return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
        else:
            return Response("Tweet id does not exist!", mimetype="text/html", status=500)  
    elif request.method == "POST":
      conn = None
      cursor = None
      users = None
      user_loginToken = request.json.get("loginToken")
      tweetId = request.json.get("tweet_id")
      tweet_content = request.json.get("tweet_content")
      rows = None   
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT userId FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchall()
        if user != None:
          cursor.execute("INSERT INTO comment(tweetId, userId, content) VALUES(?,?,?)", [tweet_id, user[0], content,])
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
          return Response("Comment commented!", mimetype="text/html", status=204)
        else:
          return Response("There is an error!", mimetype="text/html", status=500)
    elif request.method == "PATCH":
      conn = None
      cursor = None
      users = None
      user_loginToken = request.json.get("loginToken")
      commentId = request.json.get("comment_id")
      comment_content = request.json.get("comment_content")
      rows = None   
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT userId FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchall()
        cursor.execute("UPDATE comment SET content=? WHERE id=? AND userId=?", [comment_content, comment_id, user[0],])
        conn.commit()
        rows = cursor.rowcount
        cursor.execute("SELECT c. *, u.username FROM user u INNER JOIN comment c ON u.id = c.userId WHERE c.id=?",[comment_id,])
        user = cursor.fetchall()
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
          user = {
            "commentId": comment_id,
            "tweetId": user[0][4],
            "userId": user[0][3],
            "username":user[0][0],
            "content": comment_content,
            "createdAt": created_at
           }
          return Response("New comment created!", mimetype="text/html", status=200)
        else:
          return Response("There is an error!", mimetype="text/html", status=500) 
    elif request.method == "Delete":
       conn = None
       cursor = None 
       user_loginToken = request.json.get("loginToken")
       commentId = request.json.get("comment_id")
       rows = None
       try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchone()
        cursor.execute("DELETE FROM comment WHERE id=? AND userId=?", [comment_id, user[0],])
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
          return Response("Deleted successfully!", mimetype="text/html", status=204)
        else:
          return Response("There is an error!", mimetype="text/html", status=500)

#Tweet Likes Endpoint
@app.route("/api/tweetlikes", methods =["GET", "POST", "DELETE"])
def tweetlikesendpoint():
    if request.method == "GET":
      conn = None
      cursor = None
      users = None
      tweet_id = request.args.get("tweet_id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        users = cursor.fetchall()
        print(user)
        if user != None:
          cursor.execute("INSERT into tweet_like(tweetId, userId) VALUES(?,?)", [tweet_id, user[0],])
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
          if(users != None or users == []):
           for user in users:
            user = {
            "tweetId": tweet_id[0],
            "userId": user_id[1],
            "username": user_username[2]
            }
            user.append[users]
            return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
        else:
            return Response("Tweet id does not exist!", mimetype="text/html", status=500) 
    if request.method == "POST": 
      conn = None
      cursor = None
      users = None
      tweetId = None
      createdAt = None
      user_loginToken = request.json.get("loginToken")
      tweet_id = request.json.get("tweet_id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.executecursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchall()
        print(user)
        if user != None:
          cursor.execute("INSERT into tweet_like(tweetId, userId) VALUES(?,?)", [tweet_id, user[0],])
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
            return Response(json.dumps("tweet_like", default=str), mimetype="application/json", status=200)
        else:
            return Response("Tweet id does not exist!", mimetype="text/html", status=500)  
    elif request.method == "Delete":
       conn = None
       cursor = None 
       user_loginToken = request.json.get("loginToken")
       tweetId = request.json.get("tweet_id")
       rows = None
       try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchone()
        cursor.execute("DELETE FROM tweet_like WHERE tweetId=? AND userId=?", [TWEET_id, user[0],])
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
          return Response("Deleted successfully!", mimetype="text/html", status=204)
        else:
          return Response("There is an error!", mimetype="text/html", status=500)

#Comment Likes Endpoint
@app.route("/api/commentlikes", methods =["GET", "POST", "DELETE"])
def commentlikesendpoint():
    if request.method == "GET":
      conn = None
      cursor = None
      users = None
      comment_id = request.args.get("comment_id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        if commentId != None and commentId != "":
         cursor.execute("SELECT c.comment, c.userId, u.username FROM comment_like c INNER JOIN user u ON u.id = c.user WHERE c.commentId=?", [comment_id,])
         users = cursor.fetchall()
         print(user)
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
          if(users != None or users == []):
           for user in users:
            user = {
            "commentId": comment_id[0],
            "userId": user_id[1],
            "username": user_username[2]
            }
            user.append[users]
            return Response(json.dumps(users, default=str), mimetype="application/json", status=200)
        else:
            return Response("Comment liked!", mimetype="text/html", status=500)
    if request.method == "POST": 
      conn = None
      cursor = None
      users = None
      user_loginToken = request.json.get("loginToken")
      comment_id = request.json.get("comment_id")
      rows = None
      try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.executecursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchall()
        print(user)
        if user != None:
          cursor.execute("INSERT into comment_like(commentId, userId) VALUES(?,?)", [comment_id, user[0],])
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
        if(users != None):
            return Response(json.dumps("comment_like", default=str), mimetype="application/json", status=200)
        else:
            return Response("There was an error!", mimetype="text/html", status=500)  
    elif request.method == "Delete":
       conn = None
       cursor = None 
       user_loginToken = request.json.get("loginToken")
       commentId = request.json.get("comment_id")
       rows = None
       try:
        conn = mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database,)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_session WHERE login_token=?", [user_loginToken,])
        user = cursor.fetchone()
        cursor.execute("DELETE FROM comment_like WHERE commentId=? AND userId=?", [comment_id, user[0],])
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
          return Response("Deleted successfully!", mimetype="text/html", status=204)
        else:
          return Response("There is an error!", mimetype="text/html", status=500)        








    

         


         




         
