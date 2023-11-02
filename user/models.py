from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
import uuid
from db import db
class User:
  def start_session(self,user):
      del user['password']
      session["logged_in"]=True
      session['user']=user
      return jsonify(user), 200


  def signup(self):
    # print("helloee")
    print(request.form)

    # Create the user object
    user = {
    #  "_id": "",
    #   "name": "",
    #   "email": "",
    #   "password": ""
      "_id": uuid.uuid4().hex,
      "name": request.form.get('name'),
      "email": request.form.get('email'),
      "password": request.form.get('password')
    }

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])

 
    
    if db.user_login.find_one({"email": user['email']}):
            return jsonify({"error": "Email address already used"}), 400
    
    if  db.user_login.insert_one(user):
        return self.start_session(user)
       

    # Check for existing email address
   
    return jsonify({"error":"Signup Failed"}), 400


  def signout(self):
      session.clear()
      return redirect('/')
  
  def login(self):
      user = db.user_login.find_one({
          "email": request.form.get('email')
      })
      if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']) :
          print("sucess login")
          return self.start_session(user)
      print("fail login")
      return jsonify({"error":"Invalid login credentials"}), 401