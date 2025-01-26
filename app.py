from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "b'G \x01\x9fk\x8e\xc7\x16Q\xc0\xa2\xc4\xe7\x1e\r\x06\xb3\xdf\xbe\xb9\x97\x9d=\xf4"

# PostgreSQL connection string
db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
if not db_uri:
    raise ValueError("No SQLALCHEMY_DATABASE_URI found in environment variables.")
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Added for database migrations

# Define Reservation model for your form data
class ReservationForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    order_food = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reservation_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<ReservationForm {self.name}, Food: {self.order_food}, Quantity: {self.quantity}>'

# Define ReservationDetails model
class ReservationDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    order_occasion = db.Column(db.String(200), nullable=False)
    number_of_invited_guests = db.Column(db.Integer, nullable=False)
    reservation_start_time = db.Column(db.DateTime, nullable=False)
    reservation_end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ReservationDetails {self.name}, Guests: {self.number_of_invited_guests}>'

# Define Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Define Customer Comment model
class CustomerComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Optional: for customer name
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CustomerComment {self.name}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['POST'])
def reserve():
    try:
        # Form data from the reservation form
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        order_food = request.form['order_food']
        quantity = int(request.form['quantity'])
        reservation_time_str = request.form['reservation_time']
        order_occasion = request.form.get('order_occasion', 'N/A')  # Optional field for the occasion
        number_of_invited_guests = int(request.form.get('number_of_invited_guests', 0))  # Default to 0 if not provided
        reservation_start_time_str = request.form.get('reservation_start_time', reservation_time_str)
        reservation_end_time_str = request.form.get('reservation_end_time', reservation_time_str)

        # Parse datetime fields
        try:
            reservation_time = datetime.strptime(reservation_time_str, '%Y-%m-%dT%H:%M')
            reservation_start_time = datetime.strptime(reservation_start_time_str, '%Y-%m-%dT%H:%M')
            reservation_end_time = datetime.strptime(reservation_end_time_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid reservation time format. Please try again.', 'error')
            return redirect(url_for('index'))

        # Create new reservation entry for the ReservationForm model
        new_reservation = ReservationForm(
            name=name,
            email=email,
            phone=phone,
            order_food=order_food,
            quantity=quantity,
            reservation_time=reservation_time
        )

        # Create new reservation entry for the ReservationDetails model
        new_reservation_details = ReservationDetails(
            name=name,
            email=email,
            phone=phone,
            order_occasion=order_occasion,
            number_of_invited_guests=number_of_invited_guests,
            reservation_start_time=reservation_start_time,
            reservation_end_time=reservation_end_time
        )

        # Save both entries to the database
        db.session.add(new_reservation)
        db.session.add(new_reservation_details)
        db.session.commit()

        flash('Reservation created successfully!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        logging.error(f"Error during reservation: {str(e)}")
        db.session.rollback()
        flash('There was an error with your reservation. Please try again.', 'error')
        return redirect(url_for('index'))




@app.route('/contact', methods=['POST'])
def contact():
    try:
        name = request.form['name']
        email = request.form['email']
        message_content = request.form['message']

        if not name or not email or not message_content:
            flash('All fields must be filled out.', 'error')
            return redirect(url_for('index'))

        new_message = Message(name=name, email=email, message=message_content)
        db.session.add(new_message)
        db.session.commit()

        flash('Message sent successfully!', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        logging.error(f"Error during contact message: {str(e)}")
        db.session.rollback()
        flash(f'There was an issue with your message: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        name = request.form.get('name', 'Anonymous')  # Default to "Anonymous" if name isn't provided
        comment = request.form['comment']

        if not comment.strip():
            flash('Comment cannot be empty!', 'error')
            return redirect(url_for('comments'))

        # Save the comment to the database
        new_comment = CustomerComment(name=name, comment=comment)
        try:
            db.session.add(new_comment)
            db.session.commit()
            flash('Thank you for your feedback!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving your comment: {str(e)}', 'error')

    # Fetch all comments from the database
    all_comments = CustomerComment.query.order_by(CustomerComment.created_at.desc()).all()
    return render_template('comments.html', comments=all_comments)

# Create the database tables if they don't exist yet
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=8001)
