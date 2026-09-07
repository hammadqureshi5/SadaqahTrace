# TrustTrack universal app template

One Expo + React Native codebase for Android, iOS, and web.

## Included flows

- Donor home and tracking
- Donation details and plain-language timeline
- Privacy-aware delivery evidence
- Verified NGO directory
- NGO field capture placeholder
- Trust-score breakdown and Q&A entry points

## Run

```bash
npm install
npm run start
```

Press `a` for Android, `i` for iOS, or `w` for web.

The sample records are local mock data. Replace the records in `src/data.ts` with calls to the FastAPI endpoints defined in the TrustTrack architecture document.
