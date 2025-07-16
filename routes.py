from flask import Blueprint, request, jsonify
from models import db, FitnessClass, Booking
from utils import convert_ist_to_timezone
from sqlalchemy import func
import logging

bp = Blueprint('routes', __name__)
log = logging.getLogger(__name__)

def seed_classes():
    if not FitnessClass.query.first():
        for name, dt, inst in [
            ("Yoga", "2025-07-20 10:00", "Alice"),
            ("Zumba", "2025-07-21 17:00", "Bob"),
            ("HIIT", "2025-07-22 08:00", "Carol")
        ]:
            db.session.add(FitnessClass(
                name=name,
                datetime_ist=dt,
                instructor=inst,
                available_slots=5
            ))
        db.session.commit()
        log.info("Seeded fitness classes.")

@bp.route('/classes', methods=['GET'])
def get_classes():
    tz = request.args.get("timezone", "Asia/Kolkata")
    email = request.args.get("email", "").strip().lower()

    classes = FitnessClass.query.order_by(FitnessClass.datetime_ist).all()

    data = [dict(
        id=c.id,
        name=c.name,
        datetime=convert_ist_to_timezone(c.datetime_ist, tz),
        instructor=c.instructor,
        available_slots=c.available_slots,
        already_booked=False
    ) for c in classes]

    if email:
        booked = Booking.query.with_entities(Booking.class_id).filter(
            func.lower(Booking.client_email) == email
        ).all()
        booked_ids = {b.class_id for b in booked}
        for entry in data:
            if entry["id"] in booked_ids:
                entry["already_booked"] = True

    return jsonify(data), 200

@bp.route('/book', methods=['POST'])
def book_class():
    data = request.get_json()
    for field in ("class_id", "client_name", "client_email"):
        if not data.get(field):
            return jsonify({"error": "Missing required fields"}), 400

    try:
        cid = int(data["class_id"])
    except ValueError:
        return jsonify({"error": "Invalid class ID"}), 400

    c = FitnessClass.query.get(cid)
    if not c or c.available_slots <= 0:
        return jsonify({"error": "No slots available or class not found"}), 400

    email = data["client_email"].strip().lower()
    if Booking.query.filter(func.lower(Booking.client_email) == email, Booking.class_id == cid).first():
        return jsonify({"error": "Already booked this class"}), 400

    booking = Booking(class_id=cid, client_name=data["client_name"].strip(), client_email=email)
    c.available_slots -= 1
    db.session.add(booking)
    db.session.commit()

    return jsonify({"message": "Booking successful", "booking_id": booking.id}), 201

@bp.route('/cancel', methods=['POST'])
def cancel_booking():
    data = request.get_json()
    cid = data.get("class_id")
    email = data.get("client_email", "").strip().lower()

    if not cid or not email:
        return jsonify({"error": "Missing class_id or email"}), 400

    booking = Booking.query.filter_by(class_id=cid).filter(
        func.lower(Booking.client_email) == email
    ).first()

    if not booking:
        return jsonify({"error": "No booking found"}), 404

    booking.fitness_class.available_slots += 1
    db.session.delete(booking)
    db.session.commit()

    return jsonify({"message": "Booking cancelled"}), 200

@bp.route('/bookings', methods=['GET'])
def get_bookings():
    email = request.args.get("email", "").strip().lower()
    tz = request.args.get("timezone", "Asia/Kolkata")

    if not email:
        return jsonify({"error": "Email required"}), 400

    bs = Booking.query.filter(func.lower(Booking.client_email) == email).all()

    return jsonify([{
        "booking_id": b.id,
        "class_id": b.class_id,
        "class_name": b.fitness_class.name,
        "datetime": convert_ist_to_timezone(b.fitness_class.datetime_ist, tz),
        "client_name": b.client_name
    } for b in bs]), 200
