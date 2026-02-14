"""
HyperStudio FastAPI Backend
REST API for neurodivergent-first avatar video generation
Built with ❤️ by BROski♾ for the Hyperfocus Zone
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime
import logging
import asyncio

# Supabase
from supabase import create_client, Client

# Local imports (adjust paths as needed)
# from api.config import settings, setup_directories, validate_config
# from core.video_generator import HyperStudioVideoGenerator

logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="HyperStudio API",
    description="Neurodivergent-first AI avatar video generation platform",
    version="1.0.0-mvp",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== REQUEST/RESPONSE MODELS =====

class VideoGenerationRequest(BaseModel):
    """Request to generate tutorial video"""
    avatar_id: str = Field(
        default="broski_default",
        description="Avatar character ID"
    )
    script: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Tutorial script text"
    )
    voice_id: str = Field(
        default="en-GB-RyanNeural",
        description="Azure TTS voice ID"
    )
    voice_style: Optional[str] = Field(
        default=None,
        description="Voice style: cheerful, excited, friendly, empathetic"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID (from auth)"
    )


class VideoGenerationResponse(BaseModel):
    """Response after queueing video generation"""
    video_id: str
    status: str
    message: str
    estimated_time_seconds: int


class VideoStatusResponse(BaseModel):
    """Video generation job status"""
    video_id: str
    status: str  # queued, processing, completed, failed
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None


class AvatarInfo(BaseModel):
    """Avatar character information"""
    avatar_id: str
    name: str
    description: Optional[str]
    image_url: str
    tags: List[str] = []


class VoiceInfo(BaseModel):
    """Voice option information"""
    voice_id: str
    name: str
    language: str
    locale: str
    gender: Optional[str]
    accent: Optional[str]
    description: Optional[str]


# ===== DEPENDENCIES =====

def get_supabase() -> Client:
    """Get Supabase client"""
    # Load from environment
    import os
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise HTTPException(
            status_code=500,
            detail="Supabase configuration missing"
        )
    
    return create_client(supabase_url, supabase_key)


def get_video_generator():
    """Get video generator instance (singleton pattern)"""
    import os
    
    # This would be initialized once at startup
    # For now, returning config for generator
    return {
        "wav2lip_model_path": os.getenv("WAV2LIP_MODEL_PATH", "models/wav2lip_gan.pth"),
        "azure_speech_key": os.getenv("AZURE_SPEECH_KEY"),
        "azure_speech_region": os.getenv("AZURE_SPEECH_REGION", "uksouth"),
        "device": "cuda",
        "quality": "Enhanced"
    }


# ===== API ENDPOINTS =====

@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "HyperStudio",
        "version": "1.0.0-mvp",
        "status": "online",
        "message": "Built for neurodivergent creators! 💪",
        "docs": "/docs"
    }


@app.post("/v1/videos/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase)
):
    """
    Generate new tutorial video
    
    Process:
    1. Create job record in database (status: queued)
    2. Add to background task queue
    3. Return job ID immediately
    4. Process video in background
    5. Update status when complete
    """
    
    # Generate unique video ID
    video_id = str(uuid.uuid4())
    
    # Validate avatar exists
    avatar_check = supabase.table("avatars").select("*").eq(
        "avatar_id", request.avatar_id
    ).execute()
    
    if not avatar_check.data:
        raise HTTPException(
            status_code=404,
            detail=f"Avatar '{request.avatar_id}' not found"
        )
    
    # Create job record
    try:
        supabase.table("video_jobs").insert({
            "video_id": video_id,
            "user_id": request.user_id,
            "avatar_id": request.avatar_id,
            "script": request.script,
            "voice_id": request.voice_id,
            "status": "queued"
        }).execute()
    except Exception as e:
        logger.error(f"Failed to create job record: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create video job"
        )
    
    # Add to background task queue
    background_tasks.add_task(
        process_video_generation,
        video_id=video_id,
        avatar_id=request.avatar_id,
        script=request.script,
        voice_id=request.voice_id,
        voice_style=request.voice_style,
        supabase=supabase
    )
    
    # Estimate processing time (rough calculation)
    # ~30 seconds per minute of audio
    words = len(request.script.split())
    estimated_audio_minutes = words / 150  # Average speaking speed
    estimated_time = int(estimated_audio_minutes * 30)
    
    return VideoGenerationResponse(
        video_id=video_id,
        status="queued",
        message="Video generation started! Check status at /v1/videos/{video_id}/status",
        estimated_time_seconds=max(30, estimated_time)
    )


@app.get("/v1/videos/{video_id}/status", response_model=VideoStatusResponse)
async def get_video_status(
    video_id: str,
    supabase: Client = Depends(get_supabase)
):
    """
    Get video generation job status
    
    Status values:
    - queued: Job created, waiting to process
    - processing: Currently generating video
    - completed: Video ready! URL available
    - failed: Error occurred, check error_message
    """
    
    try:
        result = supabase.table("video_jobs").select("*").eq(
            "video_id", video_id
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Video job '{video_id}' not found"
            )
        
        job = result.data[0]
        
        return VideoStatusResponse(
            video_id=job["video_id"],
            status=job["status"],
            video_url=job.get("video_url"),
            thumbnail_url=job.get("thumbnail_url"),
            duration_seconds=job.get("duration_seconds"),
            error_message=job.get("error_message"),
            created_at=job["created_at"],
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at"),
            processing_time_seconds=job.get("processing_time_seconds")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve job status"
        )


@app.get("/v1/avatars", response_model=List[AvatarInfo])
async def list_avatars(
    supabase: Client = Depends(get_supabase)
):
    """List available avatar characters"""
    
    try:
        result = supabase.table("avatars").select("*").execute()
        
        return [
            AvatarInfo(
                avatar_id=avatar["avatar_id"],
                name=avatar["name"],
                description=avatar.get("description"),
                image_url=avatar["image_url"],
                tags=avatar.get("tags", [])
            )
            for avatar in result.data
        ]
        
    except Exception as e:
        logger.error(f"Failed to list avatars: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve avatars"
        )


@app.get("/v1/voices", response_model=List[VoiceInfo])
async def list_voices(
    language: Optional[str] = None,
    supabase: Client = Depends(get_supabase)
):
    """
    List available TTS voices
    
    Optional filter by language:
    - language=Welsh
    - language=English
    """
    
    try:
        query = supabase.table("voices").select("*")
        
        if language:
            query = query.eq("language", language)
        
        result = query.execute()
        
        return [
            VoiceInfo(
                voice_id=voice["voice_id"],
                name=voice["name"],
                language=voice["language"],
                locale=voice["locale"],
                gender=voice.get("gender"),
                accent=voice.get("accent"),
                description=voice.get("description")
            )
            for voice in result.data
        ]
        
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve voices"
        )


@app.delete("/v1/videos/{video_id}")
async def delete_video(
    video_id: str,
    supabase: Client = Depends(get_supabase)
):
    """Delete video and cleanup storage"""
    
    try:
        # Get video job
        result = supabase.table("video_jobs").select("*").eq(
            "video_id", video_id
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Video '{video_id}' not found"
            )
        
        job = result.data[0]
        
        # Delete from storage if completed
        if job["status"] == "completed" and job.get("video_url"):
            # Extract filename from URL
            filename = f"{video_id}.mp4"
            try:
                supabase.storage.from_("videos").remove([filename])
            except:
                pass  # Ignore storage errors
        
        # Delete job record
        supabase.table("video_jobs").delete().eq(
            "video_id", video_id
        ).execute()
        
        return {"message": "Video deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete video: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete video"
        )


# ===== BACKGROUND TASK PROCESSOR =====

async def process_video_generation(
    video_id: str,
    avatar_id: str,
    script: str,
    voice_id: str,
    voice_style: Optional[str],
    supabase: Client
):
    """
    Background task to process video generation
    
    This runs asynchronously after API returns response!
    Updates database as it progresses.
    """
    
    import os
    import time
    from pathlib import Path
    
    start_time = time.time()
    
    try:
        # Update status to processing
        supabase.table("video_jobs").update({
            "status": "processing",
            "started_at": datetime.now().isoformat()
        }).eq("video_id", video_id).execute()
        
        logger.info(f"🎬 Processing video {video_id}...")
        
        # Initialize video generator
        # from core.video_generator import HyperStudioVideoGenerator
        # (Import at function level to avoid circular dependencies)
        
        # For now, simulating video generation
        # In production, this would call the actual generator
        
        # Paths
        avatar_path = f"avatars/{avatar_id}.png"
        output_path = f"/tmp/{video_id}.mp4"
        
        # Generate video (placeholder - replace with actual generator)
        await asyncio.sleep(5)  # Simulate processing time
        
        # In production, use:
        # generator = HyperStudioVideoGenerator(...)
        # metadata = await generator.generate_tutorial_video(
        #     avatar_image_path=avatar_path,
        #     script_text=script,
        #     output_path=output_path,
        #     voice_id=voice_id,
        #     voice_style=voice_style
        # )
        
        # Upload to Supabase Storage
        logger.info(f"📤 Uploading video {video_id} to storage...")
        
        with open(output_path, "rb") as f:
            supabase.storage.from_("videos").upload(
                path=f"{video_id}.mp4",
                file=f,
                file_options={"content-type": "video/mp4"}
            )
        
        # Get public URL
        video_url = supabase.storage.from_("videos").get_public_url(
            f"{video_id}.mp4"
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update job as completed
        supabase.table("video_jobs").update({
            "status": "completed",
            "video_url": video_url,
            "duration_seconds": 30,  # metadata["duration_seconds"],
            "processing_time_seconds": processing_time,
            "completed_at": datetime.now().isoformat()
        }).eq("video_id", video_id).execute()
        
        logger.info(f"✅ Video {video_id} completed in {processing_time:.1f}s")
        
        # Cleanup temp file
        Path(output_path).unlink(missing_ok=True)
        
    except Exception as e:
        logger.error(f"❌ Video {video_id} failed: {e}")
        
        # Update job as failed
        supabase.table("video_jobs").update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": datetime.now().isoformat()
        }).eq("video_id", video_id).execute()


# ===== STARTUP/SHUTDOWN =====

@app.on_event("startup")
async def startup_event():
    """Run on API startup"""
    logger.info("🚀 HyperStudio API starting...")
    
    # Setup directories
    # setup_directories()
    
    # Validate configuration
    # errors = validate_config()
    # if errors:
    #     logger.error("Configuration errors:")
    #     for error in errors:
    #         logger.error(f"  - {error}")
    #     raise Exception("Invalid configuration")
    
    logger.info("✅ HyperStudio API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on API shutdown"""
    logger.info("👋 HyperStudio API shutting down...")


# ===== DEV/DEBUG ENDPOINTS =====

@app.get("/v1/debug/jobs")
async def debug_list_jobs(
    status: Optional[str] = None,
    limit: int = 10,
    supabase: Client = Depends(get_supabase)
):
    """Debug: List recent video jobs"""
    
    query = supabase.table("video_jobs").select("*")
    
    if status:
        query = query.eq("status", status)
    
    result = query.order("created_at", desc=True).limit(limit).execute()
    
    return result.data


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
