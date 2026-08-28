from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Ngo(Base):
    __tablename__ = "ngos"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    donations: Mapped[list["Donation"]] = relationship(back_populates="ngo")


class Donor(Base):
    __tablename__ = "donors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    donations: Mapped[list["Donation"]] = relationship(back_populates="donor")


class Donation(Base):
    __tablename__ = "donations"

    id: Mapped[int] = mapped_column(primary_key=True)
    tracking_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    ngo_id: Mapped[int] = mapped_column(ForeignKey("ngos.id"), nullable=False)
    donor_id: Mapped[int] = mapped_column(ForeignKey("donors.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    aid_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="created", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ngo: Mapped[Ngo] = relationship(back_populates="donations")
    donor: Mapped[Donor] = relationship(back_populates="donations")
    proofs: Mapped[list["ProofUpload"]] = relationship(back_populates="donation")


class ProofUpload(Base):
    __tablename__ = "proof_uploads"

    id: Mapped[int] = mapped_column(primary_key=True)
    donation_id: Mapped[int] = mapped_column(ForeignKey("donations.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    claimed_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    claimed_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    claimed_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    aid_type: Mapped[str] = mapped_column(String(64), nullable=False)
    exif_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    donation: Mapped[Donation] = relationship(back_populates="proofs")
