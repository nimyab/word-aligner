from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from contextlib import asynccontextmanager

from word_aligner import WordAligner

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable for model storage
aligner_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global aligner_instance

    # Load model at startup
    logger.info("🚀 Loading WordAligner model...")
    try:
        aligner_instance = WordAligner()
        logger.info("✅ WordAligner model successfully loaded!")
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        raise

    yield

    logger.info("🔄 Shutting down service...")


# Create FastAPI application
app = FastAPI(
    title="Word Aligner Service",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API data models
class AlignmentRequest(BaseModel):
    st: str = Field(..., description="Source text", min_length=1)
    tt: str = Field(..., description="Target text", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "st": "McGregor's fiancee Dee Devlin got in touch after media reports about McGregor's infidelities",
                "tt": "Невеста МакГрегора Ди Девлин вышла на связь после сообщений в СМИ о изменах МакГрегора",
            }
        }


class AlignmentResponseItem(BaseModel):
    sw: str = Field(..., description="Word from source text")
    tw: str = Field(..., description="Word from target text")
    si: tuple[int, int] = Field(
        ..., description="Word positions in source text (start, end)"
    )
    ti: tuple[int, int] = Field(
        ..., description="Word positions in target text (start, end)"
    )


class AlignmentResponse(BaseModel):
    a: List[AlignmentResponseItem] = Field(
        ..., description="List of word alignments"
    )
    st: str = Field(..., description="Source text")
    tt: str = Field(..., description="Target text")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error description")
    detail: Optional[str] = Field(None, description="Error details")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check service health"""
    global aligner_instance

    if aligner_instance is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return HealthResponse(
        status="healthy", message="Service is running normally, model is loaded"
    )


@app.post("/align", response_model=AlignmentResponse)
async def align_words(request: AlignmentRequest):
    """
    Align words between source and target text

    - **source_text**: Source text for alignment
    - **target_text**: Target text for alignment

    Returns a list of alignments with word positions in both texts.
    """
    global aligner_instance

    if aligner_instance is None:
        raise HTTPException(
            status_code=503, detail="Model not loaded. Please try again later."
        )

    try:
        # Get alignments
        alignments = aligner_instance.get_word_alignment(
            request.st, request.tt
        )

        # Convert result to API format
        alignment_items = [
            AlignmentResponseItem(
                sw=alignment.src_word,
                tw=alignment.target_word,
                si=alignment.src_indexes,
                ti=alignment.target_indexes,
            )
            for alignment in alignments
        ]

        response = AlignmentResponse(
            a=alignment_items,
            st=request.st,
            tt=request.tt,
        )

        return response
    
    except ValueError as e:
        logger.error(f"Source text: {request.st}")
        logger.error(f"Target text: {request.tt}")
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Source text: {request.st}")
        logger.error(f"Target text: {request.tt}")
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500, detail=str(e)
        )


# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"error": exc.detail, "status_code": exc.status_code}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
