import os
import smtplib
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

# -----------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class GmailDatabase(db.Model):
    __tablename__ = "Gmail messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(25), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.message}')"


class SiteDatabase(db.Model):
    __tablename__ = "local messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.message}')"


db.create_all()


# -----------------------------------
def get_from_db():
    return SiteDatabase.query.all()


def sendmail(msg):
    """sends a mail for a specific person """
    my_email = os.environ.get('my_email')
    my_pass = os.environ.get('my_pass')
    receiver = os.environ.get('receiver')
    connection = smtplib.SMTP("smtp.gmail.com")
    connection.starttls()
    connection.login(user=my_email, password=my_pass)
    connection.sendmail(
        from_addr=my_email,
        to_addrs=receiver,
        msg=f"Subject: hello Trap , \n\n this is an automated message from : {msg['name']} \n "
            f"email: {msg['email']}\n msg: {msg['message']}"

    )
    connection.close()


def write_to_db(msg):
    if success:
        data = SiteDatabase(name=msg['name'], email=msg['email'], message=msg['message'])
        db.session.add(data)
        db.session.commit()
    else:
        data = GmailDatabase(name=msg['name'], email=msg['email'], message=msg['message'])
        db.session.add(data)
        db.session.commit()


success = False


@app.route('/')
def home():
    global success
    success = False
    return render_template('index.html', msg_sent=success)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    global success
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'email': request.form['email'],
            'message': request.form['message'],
        }
        if success:
            write_to_db(data)
            return render_template("index.html", msg_sent=True)

        sendmail(data)
        write_to_db(data)
        event = True
        success = event

        return render_template("index.html", msg_sent=event)

    else:
        return render_template("index.html")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
