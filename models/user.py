import bcrypt
from database.mongodb import users_collection


def create_user(name, email, password):

    existing_user = users_collection.find_one(
        {
            "email": email
        }
    )


    if existing_user:
        return False


    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )


    user = {

        "name": name,

        "email": email,

        "password": hashed_password

    }


    users_collection.insert_one(user)


    return True



def verify_user(email, password):

    user = users_collection.find_one({
        "email": email
    })

    print("Entered Email:", email)
    print("User Found:", user)

    if not user:
        return None

    print("Stored Password:", user["password"])
    print("Type:", type(user["password"]))

    if bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"]
    ):
        print("Password Matched")
        return user

    print("Password Not Matched")
    return None