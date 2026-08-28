from sqlalchemy.orm import Session

from app.models import Donor, Ngo


def seed_defaults(db: Session) -> None:
    if db.query(Ngo).first() is None:
        db.add(Ngo(name="Alkhidmat Demo NGO"))
    if db.query(Donor).first() is None:
        db.add(Donor(name="Demo Donor"))
    db.commit()
