# STEM Tutor with Emotion Recognition

This project integrates emotion recognition capabilities with a STEM tutoring chatbot, allowing the AI to adapt its responses based on the user's emotional state.

## Features

- **Real-time Emotion Detection**: Uses YOLO-based face emotion recognition
- **Emotion-Aware Responses**: Chatbot adapts responses based on detected emotions
- **Camera Integration**: Toggle camera on/off for emotion detection
- **Web Interface**: Modern React-based frontend with real-time updates
- **RESTful API**: FastAPI backend with comprehensive endpoints

## Architecture

```
Frontend (React) ←→ Backend API (FastAPI) ←→ Emotion Model (YOLO)
     ↓                      ↓                      ↓
  Camera Feed          Emotion Context        Face Detection
  User Interface       State Management       Emotion Classification
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install fastapi uvicorn python-multipart opencv-python ultralytics torch numpy

# Or use the startup script to check dependencies
python start_backend.py
```

### 2. Start the Backend Server

```bash
# Option 1: Use the startup script (recommended)
python start_backend.py

# Option 2: Start manually
python backend_api.py
```

The server will start on `http://localhost:8000`

### 3. Open the Frontend

Open `Chatbot-UI/main.html` in your web browser.

## API Endpoints

- `GET /health` - Server health check
- `POST /recognize_emotion` - Upload image for emotion detection
- `GET /current_emotion` - Get current detected emotion
- `GET /emotion_context` - Get emotion-based context for chatbot
- `POST /reset_emotion` - Reset emotion state

## Usage

1. **Start the Backend**: Run `python start_backend.py`
2. **Open Frontend**: Open `Chatbot-UI/main.html` in browser
3. **Enable Camera**: Click the camera icon to start emotion detection
4. **Chat**: The chatbot will adapt responses based on your emotional state

## Emotion-Aware Features

The chatbot recognizes these emotions and adapts accordingly:

- **Happy** 😊: Encourages advanced learning and exploration
- **Sad** 💙: Offers support and breaks down complex topics
- **Angry** 🤝: Approaches with patience and alternative explanations
- **Surprised** 🤯: Explains concepts in detail and connects topics
- **Fearful** 💪: Provides reassurance and step-by-step guidance
- **Disgusted** 🔄: Suggests different approaches and engaging examples
- **Neutral** 😐: Continues with standard helpful responses

## Technical Details

### Backend (FastAPI)
- **Model**: YOLO-based emotion recognition
- **Optimization**: GPU support, FP16 precision, temporal smoothing
- **Performance**: Configurable image size, confidence thresholds
- **CORS**: Enabled for frontend integration

### Frontend (React)
- **Real-time Updates**: Emotion detection every 3 seconds
- **Camera Integration**: WebRTC for video capture
- **State Management**: Emotion context and server status
- **Responsive UI**: Modern design with emotion indicators

### Model Performance
- **Input Size**: 640x640 (configurable)
- **Confidence Threshold**: 0.3 (configurable)
- **Detection Rate**: ~3 FPS (optimized for real-time)
- **Accuracy**: Depends on model training data

## Troubleshooting

### Camera Issues
- Ensure camera permissions are granted
- Check if camera is being used by another application
- Try different camera indices (0, 1, 2)

### Server Issues
- Verify all dependencies are installed
- Check if port 8000 is available
- Ensure model file `best.pt` exists in correct location

### Model Issues
- Verify YOLO model file is present
- Check GPU availability for better performance
- Monitor console for error messages

## Development

### Adding New Emotions
1. Update emotion contexts in `backend_api.py`
2. Add emotion cases in `script.js` `generateAIResponse()`
3. Test with different facial expressions

### Customizing Responses
- Modify `emotion_contexts` in `backend_api.py`
- Update `generateAIResponse()` in `script.js`
- Add new response patterns based on emotion

## File Structure

```
STEM_TUTOR_project/
├── backend_api.py              # FastAPI backend server
├── start_backend.py            # Startup script with dependency check
├── Models/
│   └── ALL_models/
│       └── YoloFace recognition/
│           ├── FaceRecognitionYolo.py  # Emotion recognition model
│           └── best.pt                 # Trained YOLO weights
└── Chatbot-UI/
    ├── main.html               # Main frontend page
    ├── script.js              # React frontend with emotion integration
    └── styles.css             # Styling including emotion displays
```

## License

This project is part of the STEM Tutor educational platform.
