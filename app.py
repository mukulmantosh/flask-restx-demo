from flask import request, Flask
from flask_restx import Resource, Api, fields, Namespace
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

basedir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(40), nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.now())


# Do not forget to create tables in db
with app.app_context():
    db.create_all()

api = Api(app, version="1.0", title='Book API', description='A simple Book API')

ns = api.namespace('books', description='Book related operations')

book_model = api.model('Book', {
    'title': fields.String(required=True, description='The book title'),
    'author': fields.String(required=True, description='The book author'),
})


@ns.route('/')
class Books(Resource):
    @ns.expect(book_model, validate=True)
    @ns.marshal_with(book_model, code=201)
    def post(self):
        """ Add a new book """
        data = request.json
        new_book = Book(title=data['title'], author=data['author'])
        db.session.add(new_book)
        db.session.commit()
        return new_book, 201


@ns.route('/<int:id>')  # passing id in the url
class BookResource(Resource):
    @ns.marshal_with(book_model)  # Transform the output according to book_model
    def get(self, id):
        """ Fetch a book by its id """
        book = Book.query.get_or_404(id)
        return book

    @ns.expect(book_model)  # Expects the input to have the format of book_model
    @ns.marshal_with(book_model)
    def put(self, id):
        """ Update a book """
        book = Book.query.get_or_404(id)
        data = request.json  # Get the updated data
        book.title = data['title']  # Updating title
        book.author = data['author']  # Updating author
        db.session.commit()
        return book

    @ns.response(204, 'Book deleted')
    def delete(self, id):
        """ Delete a book """
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        return {'message': 'Book has been deleted.'}, 204
