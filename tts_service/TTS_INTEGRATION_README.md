# 🔊 Gurukul TTS Integration

## Overview

This document describes the complete Text-to-Speech (TTS) integration for the Gurukul application, enabling automatic speech synthesis for AI-generated content.

## 🏗️ Architecture

### Backend Components

1. **TTS Service** (`Backend/tts_service/tts.py`)
   - FastAPI service running on port 8007
   - Uses pyttsx3 for text-to-speech conversion
   - Generates MP3 audio files with unique UUIDs
   - Provides REST API for TTS generation and audio retrieval

2. **Subject Generation Integration** (`Backend/subject_generation/app.py`)
   - Automatic TTS generation for lesson content
   - Integration with TTS service via HTTP requests
   - Enhanced lesson endpoints with TTS support

### Frontend Components

1. **TTS Service** (`new frontend/src/services/ttsService.js`)
   - Singleton service for TTS operations
   - Audio caching and queue management
   - Auto-play functionality for AI responses

2. **TTS Hooks** (`new frontend/src/hooks/useTTS.js`)
   - `useTTS()` - General TTS functionality
   - `useAutoPlayTTS()` - Auto-play for AI responses
   - `useJupiterTTS()` - Jupiter model specific integration

3. **Component Integration**
   - `AvatarChatInterface.jsx` - Auto-play for avatar responses
   - `Subjects.jsx` - Auto-play for lesson content

## 🚀 Setup and Installation

### 1. Backend Setup

```bash
# Install TTS dependencies
pip install pyttsx3 fastapi uvicorn

# The TTS service is automatically started with other services
cd Backend
./start_all_services.bat
```

### 2. Service Configuration

The TTS service runs on **port 8007** and is included in the centralized startup script.

**Service URLs:**
- TTS Service: `http://localhost:8007`
- Health Check: `http://localhost:8007/api/health`
- Generate TTS: `POST http://localhost:8007/api/generate`
- Get Audio: `GET http://localhost:8007/api/audio/{filename}`

### 3. Frontend Integration

The frontend automatically connects to the TTS service. No additional configuration required.

## 🎯 Features

### Auto-Play TTS
- **Avatar Chat Interface**: Automatically speaks AI responses
- **Subject Explorer**: Speaks lesson content when generated
- **Welcome Messages**: Speaks avatar introductions
- **Page Transitions**: Speaks contextual messages

### TTS Controls
- **Auto-play**: Enabled by default for AI responses
- **Volume Control**: Configurable volume levels
- **Queue Management**: Sequential playback for multiple texts
- **Caching**: Avoids regenerating identical content

### Error Handling
- **Service Health Checks**: Automatic service availability detection
- **Graceful Degradation**: Silent failure for TTS errors
- **Retry Logic**: Automatic retry for failed generations

## 🔧 API Endpoints

### TTS Service Endpoints

#### Generate TTS
```http
POST /api/generate
Content-Type: multipart/form-data

text: "Your text to convert to speech"
```

**Response:**
```json
{
  "status": "success",
  "message": "Audio generated successfully",
  "audio_url": "/api/audio/uuid.mp3",
  "filename": "uuid.mp3",
  "file_size": 12345,
  "text_length": 50
}
```

#### Get Audio File
```http
GET /api/audio/{filename}
```

Returns the MP3 audio file.

#### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "TTS",
  "tts_engine": "pyttsx3",
  "voices_available": 2,
  "output_directory": "tts_outputs",
  "audio_files_count": 150
}
```

## 🧪 Testing

### Run Integration Tests
```bash
cd Backend/tts_service
python test_tts_integration.py
```

### Manual Testing
1. Start all services: `Backend/start_all_services.bat`
2. Start frontend: `cd "new frontend" && npm start`
3. Open browser to `http://localhost:3000`
4. Test auto-play in:
   - Avatar chat interface (click avatar to chat)
   - Subject Explorer (generate lesson content)

## 🎛️ Configuration

### TTS Service Settings
- **Port**: 8007 (configured in `tts.py`)
- **Voice**: Automatically selects female voice if available
- **Speech Rate**: 180 words per minute
- **Volume**: 0.9 (90%)
- **Output Format**: MP3

### Frontend Settings
- **Auto-play**: Enabled by default
- **Volume**: 0.8 (80%)
- **Delay**: 500-800ms before auto-play
- **Cache**: Enabled for performance

## 🔍 Troubleshooting

### Common Issues

1. **TTS Service Not Starting**
   ```bash
   # Check if pyttsx3 is installed
   pip install pyttsx3
   
   # Check port availability
   netstat -an | findstr :8007
   ```

2. **No Audio Output**
   - Check system audio settings
   - Verify browser audio permissions
   - Check TTS service health endpoint

3. **Auto-play Not Working**
   - Check browser autoplay policies
   - Verify TTS service connectivity
   - Check console for error messages

### Debug Mode
Enable debug logging in browser console:
```javascript
// In browser console
localStorage.setItem('tts_debug', 'true');
```

## 📝 Usage Examples

### Frontend Usage

```javascript
import { useTTS, useAutoPlayTTS, useJupiterTTS } from '../hooks/useTTS';

// Basic TTS usage
const { playTTS, isPlaying, serviceHealthy } = useTTS();
await playTTS("Hello, this is a test message");

// Auto-play for AI responses
const { serviceHealthy } = useAutoPlayTTS(aiResponse);

// Jupiter model integration
const { handleJupiterResponse } = useJupiterTTS();
await handleJupiterResponse(jupiterModelOutput);
```

### Backend Usage

```python
# Direct TTS service call
import requests

response = requests.post(
    "http://localhost:8007/api/generate",
    data={"text": "Your text here"}
)

if response.status_code == 200:
    result = response.json()
    audio_url = f"http://localhost:8007{result['audio_url']}"
```

## 🔮 Future Enhancements

- **Voice Selection**: Multiple voice options
- **Speed Control**: Adjustable speech rate
- **Language Support**: Multi-language TTS
- **SSML Support**: Advanced speech markup
- **Streaming TTS**: Real-time audio generation
- **Voice Cloning**: Custom voice models

## 📞 Support

For issues or questions about TTS integration:
1. Check the troubleshooting section above
2. Run the integration test script
3. Check service logs in the terminal windows
4. Verify all services are running via health endpoints
