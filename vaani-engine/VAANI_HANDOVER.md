# VAANI_HANDOVER

## Project Status: 🏁 COMPLETED
**Topic**: Sovereign Voice Replacement (Gurukul - Vaani Sovereignty Sprint)
**Primary Objective**: 100% removal of External Cloud TTS dependencies.

## Key Changes Summary
1.  **Decommissioned**: Google TTS (gTTS) and external API dependencies.
2.  **Deployed**: Standalone `vaani-engine` service using Coqui XTTS v2.
3.  **Integrated**: Gurukul Backend Proxy + Frontend UI updates.

## Repository Contents (`vaani-engine`)
- `main.py`: FastAPI production service.
- `voice_samples/`: Contains the "Vaani Teacher" reference profile.
- `audio_samples/`: Generated proofs and history.
- `local_voice_test.py`: CLI testing tool.
- `VAANI_DEPLOYMENT_GUIDE.md`: Full setup instructions.
- `PERFORMANCE_REPORT.md`: Latency and RTF metrics.
- `INTEGRATION_PROOF.md`: Verification logs and UI updates.

## Technical Handover
- **Port**: 8008
- **Endpoint**: `/vaani/speak`
- **Identity**: The voice identity is defined by `voice_samples/reference.wav`. To change the voice, simply replace this file with a 10-second high-quality WAV of the new target voice.

---
*Transferred to BHIV Sovereign Infrastructure.*
