from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

router = APIRouter()

# PDF file paths - check multiple possible filenames
pdfs_dir = os.path.join(os.path.dirname(__file__), "..", "pdfs")

def find_pdf(filename_options):
    """Find PDF file from list of possible names"""
    for name in filename_options:
        path = os.path.join(pdfs_dir, name)
        if os.path.exists(path):
            return path
    return None

BROCHURE_PDF = find_pdf([
    "SPARS_Brochure.pdf",
    "SPARS-Brochure.pdf",
    "SPARS-Product-Brochure.pdf"
])

PRODUCT_PROFILE_PDF = find_pdf([
    "SPARS_Profile.pdf",
    "SPARS-Product-Profile.pdf",
    "SPARS-ProductProfile.pdf"
])

@router.get("/brochure")
async def download_brochure():
    """Download brochure PDF"""
    if not BROCHURE_PDF or not os.path.exists(BROCHURE_PDF):
        raise HTTPException(status_code=404, detail="Brochure PDF not found")
    
    return FileResponse(
        BROCHURE_PDF,
        media_type="application/pdf",
        filename="SPARS-Brochure.pdf"
    )

@router.get("/product-profile")
async def download_product_profile():
    """Download product profile PDF"""
    if not PRODUCT_PROFILE_PDF or not os.path.exists(PRODUCT_PROFILE_PDF):
        raise HTTPException(status_code=404, detail="Product Profile PDF not found")
    
    return FileResponse(
        PRODUCT_PROFILE_PDF,
        media_type="application/pdf",
        filename="SPARS-Product-Profile.pdf"
    )

