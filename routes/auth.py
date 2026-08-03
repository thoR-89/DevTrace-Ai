from flask import Blueprint, request, render_template, redirect, session, url_for

from models.user import create_user, verify_user


auth = Blueprint(
    "auth",
    __name__
)



@auth.route("/register", methods=["GET","POST"])
def register():

    if request.method=="POST":

        name=request.form["name"]

        email=request.form["email"]

        password=request.form["password"]


        result=create_user(
            name,
            email,
            password
        )


        if result:

            return redirect(
                url_for("auth.login")
            )


        return "User already exists"


    return render_template(
        "register.html"
    )





@auth.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":


        email=request.form["email"]

        password=request.form["password"]



        user=verify_user(
            email,
            password
        )



        if user:

            session["user"]=user["email"]

            session["name"]=user["name"]


            return redirect(
                "/dashboard"
            )


        return "Invalid Login"



    return render_template(
        "login.html"
    )





@auth.route("/logout")
def logout():

    session.clear()

    return redirect("/")