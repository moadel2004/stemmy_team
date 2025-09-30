from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import asyncio
from typing import Optional, List, Dict
import logging

# Load .env early
try:
    from pathlib import Path
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent
    load_dotenv(BASE_DIR / ".env", override=False)
except Exception:
    # dotenv is optional; if not installed, env vars must be set by the shell
    BASE_DIR = Path(__file__).resolve().parent

# OpenAI SDK
from pydantic import BaseModel
from openai import OpenAI

# Add the Models directory to Python path (emotion recognizer)
sys.path.append(os.path.join(os.path.dirname(__file__), 'Models', 'ALL_models', 'YoloFace recognition'))

try:
    from FaceRecognitionYolo import FaceEmotionRecognizer
except ImportError as e:
    print(f"Warning: Could not import FaceRecognitionYolo: {e}")
    FaceEmotionRecognizer = None

# Topic classifier service
from topic_classifier import TopicClassifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="STEM Tutor Emotion + Topic API", version="1.2.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Global state =====
recognizer: Optional[FaceEmotionRecognizer] = None
current_emotion: Optional[str] = None
emotion_confidence: float = 0.0

topic_clf: Optional[TopicClassifier] = None
current_topic: Optional[str] = None
topic_confidence: float = 0.0

# ---- Emotion context map (shared) ----
EMOTION_CONTEXTS: Dict[str, Dict[str, List[str] or str]] = {
    "happy": {
        "context": "User appears happy and engaged. Great time for learning!",
        "suggestions": ["Ask about advanced topics", "Suggest challenging problems", "Encourage exploration"],
    },
    "sad": {
        "context": "User seems sad or frustrated. Offer encouragement and support.",
        "suggestions": ["Break down complex topics into smaller steps", "Provide positive reinforcement", "Suggest taking a break if needed"],
    },
    "angry": {
        "context": "User appears frustrated or angry. Approach with patience.",
        "suggestions": ["Acknowledge their frustration", "Offer alternative explanations", "Suggest simpler approaches"],
    },
    "surprised": {
        "context": "User seems surprised. They might have discovered something new!",
        "suggestions": ["Ask what surprised them", "Explain the concept in detail", "Connect to related topics"],
    },
    "fearful": {
        "context": "User appears anxious or fearful about the topic.",
        "suggestions": ["Provide reassurance", "Start with basics", "Offer step-by-step guidance"],
    },
    "disgusted": {
        "context": "User seems displeased with the current topic or approach.",
        "suggestions": ["Ask what they'd prefer to learn", "Try a different teaching method", "Find more engaging examples"],
    },
    "neutral": {
        "context": "User appears neutral and focused.",
        "suggestions": ["Continue with current approach", "Ask engaging questions", "Provide clear explanations"],
    },
}

def build_emotion_instruction(emotion: Optional[str], confidence: float) -> str:
    """
    يبني نصًا موجزًا يُحقن في system message يصف حالة الانفعال وكيفية التكيّف معها.
    """
    if not emotion:
        return (
            "No reliable emotion detected; assume a neutral, supportive tone. "
            "Keep explanations clear and encouraging."
        )
    emo_key = (emotion or "").strip().lower()
    info = EMOTION_CONTEXTS.get(emo_key, EMOTION_CONTEXTS["neutral"])
    ctx = info["context"]
    sugg = info["suggestions"]
    conf_pct = f"{int(round(confidence * 100))}%" if confidence and 0 <= confidence <= 1 else "n/a"
    return (
        f"Current user emotion: {emo_key} (confidence {conf_pct}). "
        f"Guidance: {ctx}. Adjust tone and strategy accordingly. "
        f"Tips: {', '.join(sugg[:3])}."
    )

def build_topic_instruction(topic_label: Optional[str], confidence: float) -> str:
    if not topic_label:
        return "No topic detected; infer topic from user message and keep explanations general."
    conf_pct = f"{int(round((confidence or 0.0) * 100))}%"
    return (
        f"Detected user topic intent: {topic_label} (confidence {conf_pct}). "
        f"Tailor the explanation using this topic and provide relevant, grade-appropriate examples."
    )

# ---- OpenAI client (sync) ----
_openai_client = None
def get_openai_client():
    global _openai_client
    api_key = os.getenv("OPENAI_API_KEY")  # loaded from .env or environment
    base_url = os.getenv("OPENAI_BASE_URL")  # optional, for proxies/self-hosted
    org_id = os.getenv("OPENAI_ORG_ID") or os.getenv("OPENAI_ORGANIZATION")
    project = os.getenv("OPENAI_PROJECT")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set. Put it in a .env file or environment.")
    if _openai_client is None:
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        if org_id:
            kwargs["organization"] = org_id
        if project:
            kwargs["project"] = project
        _openai_client = OpenAI(**kwargs)
    return _openai_client

# ---- Schemas ----
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []  # [{role:"user"|"assistant"|"system", content:"..."}]
    model: Optional[str] = "gpt-4o-mini"
    temperature: float = 0.5
    # Emotion injection
    use_emotion: bool = True
    emotion_override: Optional[str] = None
    emotion_confidence_override: Optional[float] = None
    # Topic injection
    use_topic: bool = True
    topic_override: Optional[str] = None
    topic_confidence_override: Optional[float] = None

class ChatResponse(BaseModel):
    reply: str

class TopicClassifyRequest(BaseModel):
    text: str
    top_k: int = 3

class TopicClassifyResponse(BaseModel):
    label: Optional[str]
    confidence: float
    top: List[Dict[str, float]]
    model_loaded: bool

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    global recognizer, topic_clf
    # Emotion model
    try:
        if FaceEmotionRecognizer:
            recognizer = FaceEmotionRecognizer(
                image_size=640,
                confidence_threshold=0.3,
                iou_threshold=0.45,
                max_detections=5,
                smoothing_window=3
            )
            logger.info("Emotion recognition model loaded successfully")
        else:
            logger.warning("FaceRecognitionYolo not available - emotion detection disabled")
    except Exception as e:
        logger.error(f"Failed to initialize emotion recognition model: {e}")
        recognizer = None

    # Topic classifier
    try:
        topic_dir = BASE_DIR / "Models" / "ALL_models" / "Topic_class_classifier"
        global topic_clf
        topic_clf = TopicClassifier.from_dir(topic_dir)
        logger.info(f"Topic classifier loaded from: {topic_dir}")
    except Exception as e:
        topic_clf = None
        logger.warning(f"Topic classifier not available: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "emotion_model_loaded": recognizer is not None,
        "topic_model_loaded": topic_clf is not None,
        "current_emotion": current_emotion,
        "emotion_confidence": emotion_confidence,
        "current_topic": current_topic,
        "topic_confidence": topic_confidence,
    }

@app.post("/recognize_emotion")
async def recognize_emotion(image: UploadFile = File(...)):
    """Recognize emotion from uploaded image."""
    global current_emotion, emotion_confidence
    
    if not recognizer:
        raise HTTPException(
            status_code=503, 
            detail="Emotion recognition model not available"
        )
    
    try:
        # Read image data
        image_data = await image.read()
        
        # Predict emotion
        emotion, confidence = recognizer.predict_with_confidence(image_data)
        
        # Update global state
        current_emotion = emotion
        emotion_confidence = confidence
        
        # Determine if face was detected
        detections = 1 if confidence > getattr(recognizer, "confidence_threshold", 0.3) else 0
        
        return {
            "status": "success",
            "emotion": emotion,
            "confidence": confidence,
            "detections": detections,
            "message": f"Detected emotion: {emotion} with {confidence:.2f} confidence"
        }
        
    except Exception as e:
        logger.error(f"Emotion recognition error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Emotion recognition failed: {str(e)}"
        )

@app.get("/current_emotion")
async def get_current_emotion():
    """Get the current detected emotion."""
    return {
        "emotion": current_emotion,
        "confidence": emotion_confidence,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.post("/reset_emotion")
async def reset_emotion():
    """Reset the current emotion state."""
    global current_emotion, emotion_confidence
    current_emotion = None
    emotion_confidence = 0.0
    return {"status": "success", "message": "Emotion state reset"}

@app.get("/emotion_context")
async def get_emotion_context():
    """Get emotion-based context for the chatbot."""
    if not current_emotion:
        return {
            "has_emotion": False,
            "context": "No emotion detected. User appears neutral.",
            "suggestions": []
        }
    context_info = EMOTION_CONTEXTS.get(current_emotion.lower(), EMOTION_CONTEXTS["neutral"])
    return {
        "has_emotion": True,
        "emotion": current_emotion,
        "confidence": emotion_confidence,
        "context": context_info["context"],
        "suggestions": context_info["suggestions"]
    }

# ---- Topic classifier endpoint (اختياري للتجربة) ----
@app.post("/api/classify_topic", response_model=TopicClassifyResponse)
def classify_topic(payload: TopicClassifyRequest):
    global current_topic, topic_confidence
    if not topic_clf:
        return TopicClassifyResponse(label=None, confidence=0.0, top=[], model_loaded=False)
    try:
        label, conf = topic_clf.predict(payload.text)
        top = topic_clf.top_k(payload.text, max(1, payload.top_k))
        current_topic = label
        topic_confidence = conf
        return TopicClassifyResponse(label=label, confidence=conf, top=top, model_loaded=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic classify error: {e}")

# ---- OpenAI chat endpoint (injects emotion + topic) ----
@app.post("/api/chat_openai", response_model=ChatResponse)
def chat_openai_endpoint(payload: ChatRequest):
    """
    يرسل رسالة المستخدم إلى OpenAI ويحقن تلقائيًا:
      - سياق الانفعال (من /recognize_emotion أو من overrides)
      - الموضوع المكتشف (بتشغيل مصنّف الموضوع على الرسالة أو باستخدام overrides)
    """
    client = get_openai_client()

    # Build dynamic system prompt
    system_persona = "You are a helpful STEM tutor called STEMMY."
    sys_messages: List[Dict[str, str]] = [{"role": "system", "content": system_persona}]

    # Inject emotion
    if payload.use_emotion:
        emo = payload.emotion_override if payload.emotion_override is not None else current_emotion
        conf = (
            payload.emotion_confidence_override
            if payload.emotion_confidence_override is not None
            else (emotion_confidence or 0.0)
        )
        sys_messages.append({
            "role": "system",
            "content": "Adapt your tone and teaching strategy based on the following emotion signal. "
                       + build_emotion_instruction(emo, conf),
        })

    # Inject topic (auto-run classifier if available)
    if payload.use_topic:
        if payload.topic_override is not None:
            topic_lbl = payload.topic_override
            topic_conf = payload.topic_confidence_override or 0.0
        else:
            # صنّف رسالة المستخدم لو الموديل متاح
            try:
                if topic_clf:
                    topic_lbl, topic_conf = topic_clf.predict(payload.message)
                    # تحديث الحالة العامة (اختياري)
                    global current_topic, topic_confidence
                    current_topic, topic_confidence = topic_lbl, topic_conf
                else:
                    topic_lbl, topic_conf = current_topic, topic_confidence
            except Exception:
                topic_lbl, topic_conf = current_topic, topic_confidence

        sys_messages.append({
            "role": "system",
            "content": build_topic_instruction(topic_lbl, topic_conf),
        })

    # Build messages: system(s) + history + current user message
    messages: List[Dict[str, str]] = []
    messages.extend(sys_messages)

    for m in payload.history:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role not in ("user", "assistant", "system"):
            role = "user"
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": payload.message})

    try:
        resp = client.chat.completions.create(
            model=payload.model or "gpt-4o-mini",
            temperature=payload.temperature,
            messages=messages,
        )
        text = resp.choices[0].message.content if resp.choices else ""
        return ChatResponse(reply=text or "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

# Debug endpoint (لا يكشف المفتاح)
@app.get("/api/openai_status")
def openai_status():
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    base_url = os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
    project_set = bool(os.getenv("OPENAI_PROJECT"))
    return {"has_key": has_key, "base_url": base_url, "project_set": project_set}

if __name__ == "__main__":
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )