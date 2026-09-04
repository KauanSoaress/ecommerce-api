import cloudinary.uploader
from fastapi import UploadFile
from src.core import cloudinary_config
from fastapi import HTTPException, status

ALLOWED_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp"
}


async def upload_image(file: UploadFile) -> str: 
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image."
        )
    
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="File type not allowed. Allowed types: PNG, JPEG, WEBP."
        )
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="products",
            overwrite=False,
            resource_type="image",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading image: {str(e)}"
        )

    return result['secure_url'], result['public_id']


async def update_image(file: UploadFile, old_image_public_id: str) -> tuple[str, str]:
    await delete_image(old_image_public_id)
    return await upload_image(file)


async def delete_image(image_public_id: str) -> None:
    try:
        cloudinary.uploader.destroy(
            image_public_id,
            resource_type="image"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image: {str(e)}"
        )
