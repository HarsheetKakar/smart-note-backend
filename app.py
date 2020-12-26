from datetime import timedelta
from flask import Flask, jsonify, request, url_for, render_template, redirect, flash
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
import os
from model.fin_file import Classifier
from flask_cors import CORS
# from base64 import b64encode
from login import JWT

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(BASEDIR, 'app.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'this is the key'

db = SQLAlchemy(app)

CORS(app)


def filter_dict(a: dict, escape_keys: list) -> dict:
    """Removes selected escape_keys from dict

    Arguments:
        a {dict} -- Dictionary to act on
        escape_keys {list} -- list of keys to remove

    Returns:
        dict -- resultant dictionary
    """
    return dict(filter(lambda key: key[0] not in escape_keys, a.items()))


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True,
                      nullable=False)
    password = db.Column(db.String(80), nullable=False)
    notes = db.relationship('Note', backref="user", lazy='dynamic')
    model = db.Column(db.LargeBinary)

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return password == self.password

    def get_dict(self):
        output = filter_dict(vars(self), escape_keys=[
                             '_sa_instance_state', "password", "notes", "model"])
        return output


jwt = JWT(secret_key=app.secret_key, UserTable=User)


class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'))
    model_idx = db.Column(db.Integer)

    def get_dict(self):
        return {
            'title': self.title,
            'content': self.content,
            "id": self.id
        }

# Views from here


@app.route('/login', methods=['POST'])
def login():
    email = request.json['email']

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "email not registered"}), 404

    if user.check_password(request.json['password']):
        token = jwt.get_token(user.id, timedelta(days=365))
        return jsonify({'idToken': token}), 200

    else:
        return jsonify({'error': "password is wrong"})


@app.route("/")
def index():
    return jsonify({'success': "welcome to index page"}), 200


class UserView(MethodView):
    def post(self):
        new_user = User(first_name=request.json['first_name'],
                        last_name=request.json['last_name'],
                        email=request.json['email'],
                        password=request.json['password'])
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": "user created"}), 201

    @jwt.login_required
    def get(self, current_user):
        return jsonify({'user': current_user.get_dict()}), 200


user_view = UserView.as_view('user_api')
app.add_url_rule('/user/',  view_func=user_view,
                 methods=['GET', 'POST'])


class NoteView(MethodView):
    @jwt.login_required
    def post(self, current_user):
        note = Note(title=request.json.get('title', None),
                    content=request.json['content'])
        current_user.notes.append(note)

        with Classifier(current_user) as model:
            index = model.add_document(note.content)

        note.model_idx = index

        db.session.commit()
        return jsonify({'success': "note created"}), 201

    @jwt.login_required
    def get(self, current_user):
        def filter_my_notes(item):
            userNotes = current_user.notes.filter_by(
                model_idx=item['idx']).all()
            print(userNotes)
            if(userNotes):
                return True
            else:
                return False
        title = request.args.get("title", None)
        keywords = request.args.get("keywords", None)
        if(title):
            notes = current_user.notes.filter_by(title=title).all()
            output = list(map(lambda x: x.get_dict(), notes))
            return jsonify({'notes': output})
        elif(keywords):
            with Classifier(current_user) as model:
                try:
                    docs = model.search_by_keywords(keywords)
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400
            result = {
                "myNotes": list(filter(filter_my_notes, docs)),
                "extra": docs
            }
            return jsonify(result)
        else:
            notes = current_user.notes.all()
            output = list(map(lambda x: x.get_dict(), notes))
            return jsonify({"notes": output})

    @jwt.login_required
    def delete(self, current_user):
        id = request.json['id']
        note = current_user.notes.filter_by(id=id).first()
        with Classifier(current_user) as model:
            model.delete_document(id)

        db.session.delete(note)
        db.session.commit()
        return jsonify({'success': "note deleted"}), 201


@app.route("/model/")
@jwt.login_required
def getModel(current_user):
    return "True" if(current_user.model) else "False", 200


note_view = NoteView.as_view('note_api')
app.add_url_rule('/note/', view_func=note_view,
                 methods=['GET', 'POST', "DELETE"])


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
