from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class DonationCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    aid_type: str = Field(min_length=1, max_length=64)
    ngo_id: int | None = None
    donor_id: int | None = None


class ProofOut(BaseModel):
    id: int
    file_path: str
    original_filename: str
    claimed_lat: float | None
    claimed_lng: float | None
    claimed_timestamp: datetime | None
    aid_type: str
    exif_json: str | None
    verification_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DonationOut(BaseModel):
    id: int
    tracking_id: str
    ngo_id: int
    donor_id: int
    ngo_name: str
    donor_name: str
    amount: Decimal
    aid_type: str
    status: str
    created_at: datetime
    proofs: list[ProofOut] = []

    model_config = {"from_attributes": True}
