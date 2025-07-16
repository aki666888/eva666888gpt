"""
Standalone OmniParser Server for UFO2 Integration

This script runs a FastAPI server that provides OmniParser functionality
without the Gradio UI, making it more efficient and reliable for UFO2 integration.
"""

import os
import sys
import base64
import io
from typing import Optional, Dict, Any, List
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from PIL import Image
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the omni directory to the path so we can import from it
omni_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "omni")
sys.path.append(omni_path)

try:
    # Import OmniParser utilities
    from util.utils import check_ocr_box, get_yolo_model, get_caption_model_processor, get_som_labeled_img
except ImportError:
    logger.error(f"Failed to import OmniParser utilities from {omni_path}")
    logger.error("Make sure the OmniParser code is available at ../omni")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(title="OmniParser API", description="Standalone OmniParser API for UFO2")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models (will be loaded on first use)
_MODELS = {
    'yolo': None,
    'caption': None
}

def initialize_models():
    """Lazy initialization of models"""
    try:
        if _MODELS['yolo'] is None:
            _MODELS['yolo'] = get_yolo_model(model_path=os.path.join(omni_path, 'weights/icon_detect/model.pt'))
            logger.info("YOLO model loaded successfully")
        
        if _MODELS['caption'] is None:
            _MODELS['caption'] = get_caption_model_processor(
                model_name="florence2", 
                model_name_or_path="microsoft/Florence-2-large"
            )
            logger.info("Caption model loaded successfully")
            
        return True
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        return False

class ProcessRequest(BaseModel):
    """Request model for processing an image"""
    image_base64: str
    box_threshold: float = 0.05
    iou_threshold: float = 0.1
    use_paddleocr: bool = True
    imgsz: int = 640

class ProcessResponse(BaseModel):
    """Response model for processing an image"""
    processed_image_base64: Optional[str] = None
    parsed_elements: List[str] = []
    error: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint to check if the server is running"""
    return {"status": "OmniParser API is running", "version": "1.0.0"}

@app.post("/process", response_model=ProcessResponse)
async def process_image(request: ProcessRequest):
    """Process an image through OmniParser pipeline"""
    try:
        # Initialize models if not loaded
        if not initialize_models():
            return ProcessResponse(error="Models failed to load")
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(request.image_base64)
            image_input = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return ProcessResponse(error=f"Invalid image data: {str(e)}")
        
        # Calculate dynamic drawing parameters
        box_overlay_ratio = image_input.size[0] / 3200
        draw_bbox_config = {
            'text_scale': 0.8 * box_overlay_ratio,
            'text_thickness': max(int(2 * box_overlay_ratio), 1),
            'text_padding': max(int(3 * box_overlay_ratio), 1),
            'thickness': max(int(3 * box_overlay_ratio), 1),
        }

        # Run OCR
        ocr_bbox_rslt, _ = check_ocr_box(
            image_input,
            display_img=False,
            output_bb_format='xyxy',
            goal_filtering=None,
            easyocr_args={'paragraph': False, 'text_threshold': 0.9},
            use_paddleocr=request.use_paddleocr
        )
        
        # Safely unpack OCR results
        text = ocr_bbox_rslt[0] if ocr_bbox_rslt else []
        ocr_bbox = ocr_bbox_rslt[1] if ocr_bbox_rslt else []
        
        # Process through full pipeline
        dino_labeled_img, _, parsed_content_list = get_som_labeled_img(
            image_input,
            _MODELS['yolo'],
            BOX_TRESHOLD=request.box_threshold,
            output_coord_in_ratio=True,
            ocr_bbox=ocr_bbox,
            draw_bbox_config=draw_bbox_config,
            caption_model_processor=_MODELS['caption'],
            ocr_text=text,
            iou_threshold=request.iou_threshold,
            imgsz=request.imgsz
        )
        
        # Format parsed elements
        parsed_elements = [f'element {i}: {v}' for i, v in enumerate(parsed_content_list)]
        
        logger.info("Processing completed successfully")
        return ProcessResponse(
            processed_image_base64=dino_labeled_img,
            parsed_elements=parsed_elements
        )
        
    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        return ProcessResponse(error=f"Error during processing: {str(e)}")

@app.post("/upload_and_process")
async def upload_and_process(
    file: UploadFile = File(...),
    box_threshold: float = Form(0.05),
    iou_threshold: float = Form(0.1),
    use_paddleocr: bool = Form(True),
    imgsz: int = Form(640)
):
    """Process an uploaded image through OmniParser pipeline"""
    try:
        # Read the uploaded file
        image_data = await file.read()
        image_input = Image.open(io.BytesIO(image_data))
        
        # Convert to base64
        buffered = io.BytesIO()
        image_input.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Create request object
        request = ProcessRequest(
            image_base64=img_base64,
            box_threshold=box_threshold,
            iou_threshold=iou_threshold,
            use_paddleocr=use_paddleocr,
            imgsz=imgsz
        )
        
        # Process the image
        return await process_image(request)
        
    except Exception as e:
        logger.error(f"Upload and process error: {e}", exc_info=True)
        return ProcessResponse(error=f"Error during upload and processing: {str(e)}")

if __name__ == "__main__":
    # Run the server
    port = 7860  # Use port 7860 as expected by UFO2
    logger.info(f"Starting OmniParser API server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
