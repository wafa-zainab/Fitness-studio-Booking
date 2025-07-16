import unittest
from app import app, db
from models import FitnessClass

class BookingTestCase(unittest.TestCase):
    def setUp(self):
        # Set up test client and application context
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Create tables
        db.create_all()

        # Add a test class with 1 slot
        self.test_class = FitnessClass(
            name="TestClass",
            datetime_ist="2025-08-01 12:00",
            instructor="TestInstructor",
            available_slots=1
        )
        db.session.add(self.test_class)
        db.session.commit()

    def tearDown(self):
        # Clean up the database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_successful_booking(self):
        """Should return 201 on successful booking"""
        response = self.app.post("/book", json={
            "class_id": self.test_class.id,
            "client_name": "John",
            "client_email": "john@example.com"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("Booking successful", response.get_json()["message"])

    def test_overbooking(self):
        """Should return 400 if no slots are available"""
        # First booking (success)
        self.test_successful_booking()

        # Second booking (should fail)
        response = self.app.post("/book", json={
            "class_id": self.test_class.id,
            "client_name": "Jane",
            "client_email": "jane@example.com"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("No slots available", response.get_json()["error"])

    def test_missing_fields(self):
        """Should return 400 if required fields are missing"""
        response = self.app.post("/book", json={
            "class_id": self.test_class.id,
            "client_email": "missingname@example.com"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.get_json()["error"])

    def test_invalid_class_id(self):
        """Should return 404 if class_id does not exist"""
        response = self.app.post("/book", json={
            "class_id": 999,
            "client_name": "Ghost",
            "client_email": "ghost@example.com"
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn("Class not found", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
