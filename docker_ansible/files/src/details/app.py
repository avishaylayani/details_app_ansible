import os
from flask import Flask, render_template, redirect, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, validators
from flask_wtf import FlaskForm

# Fetch environment variables
dbuser = os.getenv("POSTGRES_USER")
dbpass = os.getenv("POSTGRES_PASSWORD")
dbhost = os.getenv('DBHOST')
dbname = os.getenv('DBNAME')
skey = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = skey
app.config["SQLALCHEMY_DATABASE_URI"] = f'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Contacts(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f'<Contact {self.email}>'

class ConnectionForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ConnectionForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        new_contact = Contacts(name=name, email=email)
        try:
            db.session.add(new_contact)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
    # Fetch all contacts for rendering in the template
    contacts = Contacts.query.all()
    return render_template('index.html', form=form, contacts=contacts)

# @app.route('/contacts', methods=['GET'])
# def get_contacts():
#     try:
#         contacts = Contacts.query.with_entities(Contacts.id, Contacts.name, Contacts.email).all()
#         result = [{'id': c.id, 'name': c.name, 'email': c.email} for c in contacts]
#         return jsonify(result), 200
#     except Exception as e:
#         return jsonify({"error": "Failed to fetch contacts"}), 500
    
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_contact(id):
    try:
        contact = Contacts.query.get(id)
        if contact is None:
            return jsonify({"error": "Contact not found"}), 404
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"message": "Contact deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete contact"}), 500

# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=8000)


