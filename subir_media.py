import os
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name = "dkcrrnukk",
    api_key    = "292822167939573",
    api_secret = "zYshL6BSpG72iS4xLUny9Hk_4jU"
)

media_dir = "media"
subidos = 0
errores = 0

for root, dirs, files in os.walk(media_dir):
    for filename in files:
        filepath = os.path.join(root, filename)
        # Mantener la ruta relativa como public_id
        public_id = filepath.replace("\\", "/").replace("media/", "")
        try:
            cloudinary.uploader.upload(
                filepath,
                public_id=public_id,
                resource_type="auto",
                use_filename=True,
                unique_filename=False,
                overwrite=True
            )
            print(f"✓ {filepath}")
            subidos += 1
        except Exception as e:
            print(f"✗ {filepath} — {e}")
            errores += 1

print(f"\nListo! Subidos: {subidos} | Errores: {errores}")