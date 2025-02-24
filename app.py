from flask import Flask, render_template, url_for, redirect, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-here"

# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:miolecraft123@localhost/Rentals"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/rentals"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
migrate=Migrate(app, db)


class Owner(db.Model):
    __tablename__ = "owners"
    id: Mapped[int] = mapped_column(primary_key=True)  
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    sketches = relationship("Sketch", backref="owner", lazy=True)  

class Sketch(db.Model):
    __tablename__ = "sketches"
    id: Mapped[int] = mapped_column(primary_key=True) 
    name: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"), nullable=False)  
    rentals = relationship("Rental", backref="sketch", lazy=True)  

class Rental(db.Model):
    __tablename__ = "rentals"
    id: Mapped[int] = mapped_column(primary_key=True)  
    sketch_id: Mapped[int] = mapped_column(Integer, ForeignKey("sketches.id"), nullable=False)  
    renter_name: Mapped[str] = mapped_column(nullable=False)
    rental_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        owner_name = request.form["owner_name"]
        sketch_name = request.form["sketch_name"]
        
        
        owner = Owner.query.filter_by(name=owner_name).first()
        if not owner:
            owner = Owner(name=owner_name)
            db.session.add(owner)
            db.session.commit()  
        
        new_sketch = Sketch(name=sketch_name, owner_id=owner.id)  
        db.session.add(new_sketch)
        db.session.commit()  
        
        flash("Sketch and owner added successfully!", "success")
        return redirect(url_for("home"))
    return render_template("home.html")

@app.route("/rent", methods=["GET", "POST"])
def rent_sketch():
    sketches = Sketch.query.all()
    if request.method == "POST":
        if not sketches:
            flash("No sketches available. Please add a sketch first.", "warning")
            return redirect(url_for("home"))
        sketch_id = int(request.form["sketch_id"])  
        renter_name = request.form["renter_name"]
        sketch = Sketch.query.get(sketch_id)
        if not sketch:
            flash("Sketch not found!", "danger")
            return redirect(url_for("rent_sketch"))
        new_rental = Rental(sketch_id=sketch_id, renter_name=renter_name)  
        db.session.add(new_rental)
        db.session.commit()  
        flash("Sketch rented successfully!", "success")
        return redirect(url_for("rent_sketch"))
    return render_template("rent.html", sketches=sketches)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)