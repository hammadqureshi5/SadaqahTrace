import { useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [amount, setAmount] = useState("5000");
  const [aidType, setAidType] = useState("food");
  const [trackingId, setTrackingId] = useState("");
  const [lookupId, setLookupId] = useState("");
  const [photo, setPhoto] = useState(null);
  const [proofAidType, setProofAidType] = useState("food");
  const [lat, setLat] = useState("24.8607");
  const [lng, setLng] = useState("67.0011");
  const [claimedAt, setClaimedAt] = useState("");
  const [donation, setDonation] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function parseResponse(res) {
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(body.detail || `Request failed (${res.status})`);
    }
    return body;
  }

  async function createDonation(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = await parseResponse(
        await fetch(`${API}/donations`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ amount: Number(amount), aid_type: aidType }),
        })
      );
      setDonation(body);
      setTrackingId(body.tracking_id);
      setLookupId(body.tracking_id);
      setProofAidType(body.aid_type);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function loadDonation(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = await parseResponse(await fetch(`${API}/donations/${lookupId.trim()}`));
      setDonation(body);
      setTrackingId(body.tracking_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function uploadProof(event) {
    event.preventDefault();
    if (!trackingId) {
      setError("Create or look up a donation first.");
      return;
    }
    if (!photo) {
      setError("Choose a proof photo.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const form = new FormData();
      form.append("photo", photo);
      form.append("aid_type", proofAidType);
      if (lat) form.append("claimed_lat", lat);
      if (lng) form.append("claimed_lng", lng);
      if (claimedAt) form.append("claimed_timestamp", claimedAt);
      const body = await parseResponse(
        await fetch(`${API}/donations/${trackingId}/proof`, {
          method: "POST",
          body: form,
        })
      );
      setDonation(body);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <h1>TrustTrack</h1>
        <p>Issue a tracking ID, then attach delivery proof. Verification checks come next.</p>
      </header>

      <section className="grid">
        <form className="card" onSubmit={createDonation}>
          <h2>1. Create donation</h2>
          <label htmlFor="amount">Amount (PKR)</label>
          <input
            id="amount"
            type="number"
            min="1"
            step="1"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
          <label htmlFor="aid">Aid type</label>
          <select id="aid" value={aidType} onChange={(e) => setAidType(e.target.value)}>
            <option value="food">Food</option>
            <option value="medical">Medical</option>
            <option value="shelter">Shelter</option>
            <option value="education">Education</option>
          </select>
          <button type="submit" disabled={busy}>
            Issue tracking ID
          </button>
        </form>

        <form className="card" onSubmit={loadDonation}>
          <h2>Look up donation</h2>
          <label htmlFor="lookup">Tracking ID</label>
          <input
            id="lookup"
            value={lookupId}
            onChange={(e) => setLookupId(e.target.value)}
            placeholder="TT-XXXXXXXX"
            required
          />
          <button type="submit" disabled={busy}>
            Load record
          </button>
        </form>

        <form className="card" onSubmit={uploadProof}>
          <h2>2. Upload proof</h2>
          <p className="muted">Attaches to {trackingId || "the selected tracking ID"}.</p>
          <label htmlFor="photo">Photo</label>
          <input
            id="photo"
            type="file"
            accept="image/*"
            onChange={(e) => setPhoto(e.target.files?.[0] || null)}
          />
          <label htmlFor="proofAid">Claimed aid type</label>
          <select
            id="proofAid"
            value={proofAidType}
            onChange={(e) => setProofAidType(e.target.value)}
          >
            <option value="food">Food</option>
            <option value="medical">Medical</option>
            <option value="shelter">Shelter</option>
            <option value="education">Education</option>
          </select>
          <label htmlFor="lat">Claimed latitude</label>
          <input id="lat" value={lat} onChange={(e) => setLat(e.target.value)} />
          <label htmlFor="lng">Claimed longitude</label>
          <input id="lng" value={lng} onChange={(e) => setLng(e.target.value)} />
          <label htmlFor="when">Claimed timestamp</label>
          <input
            id="when"
            type="datetime-local"
            value={claimedAt}
            onChange={(e) => setClaimedAt(e.target.value)}
          />
          <button type="submit" disabled={busy}>
            Upload proof
          </button>
        </form>

        <section className="card record">
          <h2>Stored record</h2>
          {error ? <p className="error">{error}</p> : null}
          {!donation ? (
            <p className="muted">Create or look up a donation to see its tracking ID and proofs.</p>
          ) : (
            <>
              <dl className="meta">
                <dt>Tracking ID</dt>
                <dd>{donation.tracking_id}</dd>
                <dt>NGO</dt>
                <dd>{donation.ngo_name}</dd>
                <dt>Donor</dt>
                <dd>{donation.donor_name}</dd>
                <dt>Amount</dt>
                <dd>{donation.amount} PKR</dd>
                <dt>Aid type</dt>
                <dd>{donation.aid_type}</dd>
                <dt>Status</dt>
                <dd>{donation.status}</dd>
              </dl>
              {(donation.proofs || []).map((proof) => (
                <div className="proof" key={proof.id}>
                  <h3>Proof #{proof.id}</h3>
                  <dl className="meta">
                    <dt>File</dt>
                    <dd>{proof.original_filename}</dd>
                    <dt>Stored path</dt>
                    <dd>{proof.file_path}</dd>
                    <dt>GPS</dt>
                    <dd>
                      {proof.claimed_lat ?? "—"}, {proof.claimed_lng ?? "—"}
                    </dd>
                    <dt>Timestamp</dt>
                    <dd>{proof.claimed_timestamp || "—"}</dd>
                    <dt>Aid type</dt>
                    <dd>{proof.aid_type}</dd>
                    <dt>Verification</dt>
                    <dd>{proof.verification_status}</dd>
                  </dl>
                </div>
              ))}
            </>
          )}
        </section>
      </section>
    </main>
  );
}

export default App;
