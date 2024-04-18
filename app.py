#!/usr/bin/env python3

import os
import sys
import subprocess
import datetime

from flask import Flask, render_template, request, redirect, url_for, make_response

import pymongo
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv(override=True)  

app = Flask(__name__)

try:
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    cxn.admin.command("ping")  
    print(" * Connected to MongoDB!")
except ConnectionFailure as e:
    print(" * MongoDB connection error:", e)  
    sys.exit(1)  

@app.route("/")
def home():
    hotels = db.hotels.find()
    return render_template("index.html", hotels=hotels)

@app.route("/book/<hotel_id>")
def book(hotel_id):
    hotel = db.hotels.find_one({"_id": ObjectId(hotel_id)})
    return render_template("book.html", hotel=hotel)

@app.route("/check_in/<hotel_id>", methods=["POST"])
def check_in(hotel_id):
    name = request.form["name"]
    email = request.form["email"]
    check_in_date = datetime.datetime.strptime(request.form["check_in_date"], "%Y-%m-%d")
    check_out_date = datetime.datetime.strptime(request.form["check_out_date"], "%Y-%m-%d")

    booking_data = {
        "name": name,
        "email": email,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "hotel_id": ObjectId(hotel_id),
        "status": "checked_in"
    }

    db.bookings.insert_one(booking_data)

    return redirect(url_for("booking_details", hotel_id=hotel_id))

@app.route("/check_out/<booking_id>")
def check_out(booking_id):
    db.bookings.update_one({"_id": ObjectId(booking_id)}, {"$set": {"status": "checked_out"}})
    return redirect(url_for("booking_details", booking_id=booking_id))

@app.route("/change_reservation/<booking_id>", methods=["POST"])
def change_reservation(booking_id):
    check_in_date = datetime.datetime.strptime(request.form["check_in_date"], "%Y-%m-%d")
    check_out_date = datetime.datetime.strptime(request.form["check_out_date"], "%Y-%m-%d")

    db.bookings.update_one({"_id": ObjectId(booking_id)}, {"$set": {"check_in_date": check_in_date, "check_out_date": check_out_date}})
    return redirect(url_for("booking_details", booking_id=booking_id))

@app.route("/booking_details/<booking_id>")
def booking_details(booking_id):
    booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
    return render_template("booking_details.html", booking=booking)

@app.route("/cancel_booking/<booking_id>")
def cancel_booking(booking_id):
    db.bookings.delete_one({"_id": ObjectId(booking_id)})
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
