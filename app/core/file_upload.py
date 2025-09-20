"""
File upload utilities for handling profile pictures and other file uploads
"""

import os
import uuid
import aiofiles
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile
from PIL import Image
import requests
from urllib.parse import urlparse

# Configuration
UPLOAD_DIR = "public/user-profile"
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB in bytes
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg"}

def ensure_upload_directory():
    """Ensure the upload directory exists"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image file
    Checks: file size, file extension, content type
    """
    # Check content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PNG and JPEG files are allowed. Got: {file.content_type}"
        )

    # Check file extension
    file_ext = os.path.splitext(file.filename.lower())[1] if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension. Only {', '.join(ALLOWED_EXTENSIONS)} are allowed. Got: {file_ext}"
        )

def validate_file_size(file_content: bytes) -> None:
    """Validate file size"""
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB. Got: {len(file_content) // (1024*1024)}MB"
        )

def validate_image_content(file_content: bytes) -> None:
    """Validate that the file content is actually a valid image"""
    try:
        # Try to open and verify the image
        from io import BytesIO
        image = Image.open(BytesIO(file_content))
        image.verify()  # This will raise an exception if the image is corrupted
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. The file appears to be corrupted or is not a valid image."
        )

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving the extension"""
    file_ext = os.path.splitext(original_filename.lower())[1] if original_filename else ".jpg"
    unique_name = str(uuid.uuid4())
    return f"{unique_name}{file_ext}"

async def save_uploaded_file(file: UploadFile) -> str:
    """
    Save uploaded file to the user profile directory
    Returns the relative file path
    """
    # Validate file
    validate_image_file(file)

    # Read file content
    file_content = await file.read()

    # Validate file size and content
    validate_file_size(file_content)
    validate_image_content(file_content)

    # Ensure upload directory exists
    ensure_upload_directory()

    # Generate unique filename
    filename = generate_unique_filename(file.filename or "image.jpg")
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)

    # Return relative path for storing in database
    return f"/{UPLOAD_DIR}/{filename}"

def validate_external_url(url: str) -> bool:
    """Validate external image URL"""
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme in ['http', 'https']:
            return False
        if not parsed_url.netloc:
            return False
        return True
    except:
        return False

async def validate_external_image_url(url: str) -> None:
    """
    Validate external image URL by checking if it's accessible and is an image
    """
    if not validate_external_url(url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL format. URL must start with http:// or https://"
        )

    try:
        # Make a HEAD request to check content type without downloading the full image
        response = requests.head(url, timeout=10, allow_redirects=True)

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to access the image URL. Status code: {response.status_code}"
            )

        content_type = response.headers.get('content-type', '').lower()
        if not any(allowed_type in content_type for allowed_type in ALLOWED_CONTENT_TYPES):
            raise HTTPException(
                status_code=400,
                detail=f"URL does not point to a valid image. Content type: {content_type}"
            )

        # Check content length if available
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Image at URL is too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )

    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to validate image URL: {str(e)}"
        )

def delete_profile_image(image_path: str) -> None:
    """Delete a profile image file"""
    if image_path and image_path.startswith('/public/user-profile/'):
        # Remove leading slash to get relative path
        file_path = image_path[1:] if image_path.startswith('/') else image_path
        full_path = os.path.join(os.getcwd(), file_path)

        try:
            if os.path.exists(full_path):
                os.remove(full_path)
        except OSError:
            # Ignore errors when deleting files (file might not exist, permission issues, etc.)
            pass

async def process_profile_picture(
    file: Optional[UploadFile] = None,
    external_url: Optional[str] = None,
    use_default: bool = True
) -> Optional[str]:
    """
    Process profile picture from either uploaded file or external URL
    Returns the avatar path/URL to store in database
    """
    if file and external_url:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both file upload and external URL. Choose one option."
        )

    if file:
        # Handle file upload
        return await save_uploaded_file(file)

    elif external_url:
        # Handle external URL
        await validate_external_image_url(external_url)
        return external_url

    elif use_default:
        # Return default avatar if no file or URL provided
        return "/public/user-profile/default.png"

    return None