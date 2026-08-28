import secrets
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.database import get_db
from app.models import Donation, Donor, Ngo, ProofUpload
from app.schemas import DonationCreate, DonationOut

router = APIRouter(prefix="/donations", tags=["donations"])


def _parse_claimed_timestamp(value: str | None) -> datetime | None:
    if not value or not value.strip():
        return None
    raw = value.strip()
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="claimed_timestamp must be ISO-8601")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _new_tracking_id(db: Session) -> str:
    for _ in range(12):
        token = f"TT-{secrets.token_hex(4).upper()}"
        if db.query(Donation).filter(Donation.tracking_id == token).first() is None:
            return token
    raise HTTPException(status_code=500, detail="Could not allocate tracking ID")


def _to_out(donation: Donation) -> DonationOut:
    return DonationOut(
        id=donation.id,
        tracking_id=donation.tracking_id,
        ngo_id=donation.ngo_id,
        donor_id=donation.donor_id,
        ngo_name=donation.ngo.name,
        donor_name=donation.donor.name,
        amount=donation.amount,
        aid_type=donation.aid_type,
        status=donation.status,
        created_at=donation.created_at,
        proofs=donation.proofs,
    )


@router.post("", response_model=DonationOut)
def create_donation(payload: DonationCreate, db: Session = Depends(get_db)):
    ngo = db.get(Ngo, payload.ngo_id) if payload.ngo_id else db.query(Ngo).order_by(Ngo.id).first()
    donor = (
        db.get(Donor, payload.donor_id)
        if payload.donor_id
        else db.query(Donor).order_by(Donor.id).first()
    )
    if ngo is None or donor is None:
        raise HTTPException(status_code=400, detail="Seed NGO and donor records are missing")

    donation = Donation(
        tracking_id=_new_tracking_id(db),
        ngo_id=ngo.id,
        donor_id=donor.id,
        amount=payload.amount,
        aid_type=payload.aid_type.strip(),
        status="created",
    )
    db.add(donation)
    db.commit()
    db.refresh(donation)
    donation = (
        db.query(Donation)
        .options(joinedload(Donation.ngo), joinedload(Donation.donor), joinedload(Donation.proofs))
        .filter(Donation.id == donation.id)
        .one()
    )
    return _to_out(donation)


@router.get("/{tracking_id}", response_model=DonationOut)
def get_donation(tracking_id: str, db: Session = Depends(get_db)):
    donation = (
        db.query(Donation)
        .options(joinedload(Donation.ngo), joinedload(Donation.donor), joinedload(Donation.proofs))
        .filter(Donation.tracking_id == tracking_id.upper())
        .first()
    )
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")
    return _to_out(donation)


@router.post("/{tracking_id}/proof", response_model=DonationOut)
async def upload_proof(
    tracking_id: str,
    photo: UploadFile = File(...),
    aid_type: str = Form(...),
    claimed_lat: float | None = Form(default=None),
    claimed_lng: float | None = Form(default=None),
    claimed_timestamp: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    donation = (
        db.query(Donation)
        .options(joinedload(Donation.ngo), joinedload(Donation.donor), joinedload(Donation.proofs))
        .filter(Donation.tracking_id == tracking_id.upper())
        .first()
    )
    if donation is None:
        raise HTTPException(status_code=404, detail="Donation not found")

    parsed_ts = _parse_claimed_timestamp(claimed_timestamp)

    if not photo.content_type or not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Proof must be an image file")

    suffix = Path(photo.filename or "proof.jpg").suffix or ".jpg"
    stored_name = f"{donation.tracking_id}-{secrets.token_hex(6)}{suffix.lower()}"
    dest = settings.upload_path / stored_name
    contents = await photo.read()
    dest.write_bytes(contents)

    proof = ProofUpload(
        donation_id=donation.id,
        file_path=str(dest.relative_to(settings.upload_path.parent)),
        original_filename=photo.filename or stored_name,
        claimed_lat=claimed_lat,
        claimed_lng=claimed_lng,
        claimed_timestamp=parsed_ts,
        aid_type=aid_type.strip(),
        exif_json=None,
        verification_status="pending",
    )
    donation.status = "proof_uploaded"
    db.add(proof)
    db.commit()

    donation = (
        db.query(Donation)
        .options(joinedload(Donation.ngo), joinedload(Donation.donor), joinedload(Donation.proofs))
        .filter(Donation.id == donation.id)
        .one()
    )
    return _to_out(donation)
