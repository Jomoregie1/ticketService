from register import signup


@signup.route("/")
def home():
    return "Hello, Home!"
