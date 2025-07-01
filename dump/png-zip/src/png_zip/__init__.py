from PIL import Image, ImageDraw, PngImagePlugin
import io
import json
import os
import base64

_TEST = None

class PngZip:
    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.metadata = {}
        self.current_width = 0
        self.current_height = 0
        self.composite_image = None
        self.mode = mode
        self.max_preview_size = (800, 600)  # Max dimensions for preview images

        if mode == 'r' and os.path.exists(filename):
            self.load()
        elif mode == 'w' and os.path.exists(filename):
            os.remove(filename)

    def __calculate_average_dimensions(self):
        total_width = total_height = num_images = 0
        for key in self.metadata:
            if "rect" not in self.metadata[key]:
                continue

            rect = self.metadata[key]['rect']
            # rect is stored as (x, y, width, height)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            total_width += width
            total_height += height
            num_images += 1

        if num_images == 0:
            return 0, 0  # Default to 0,0 if no images have been added

        avg_width = total_width / num_images
        avg_height = total_height / num_images
        return int(avg_width), int(avg_height)

    def __save_original_image(self, img, key_name):
        with io.BytesIO() as img_byte_arr:
            img.save(img_byte_arr, format=img.format)  # Save the image in its original format
            img_byte_arr.seek(0)  # Go to the start of the StringIO buffer
            encoded_img = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            self.metadata[key_name] = {
                'original_data': encoded_img,
                'original_format': img.format,
                'original_size': img.size
            }
    

    def add_image(self, image_path, key_name):
        with Image.open(image_path) as img:
            original_img = img.copy()
            original_img.load()
            original_format = img.format
            original_img.format = original_format
            img_size = img.size
            avg_width, avg_height = self.__calculate_average_dimensions()
            if not avg_width or not avg_height:
                avg_width, avg_height = img_size

            # Determine if the image is "too big"
            is_too_big = img.width > 1.5 * avg_width or img.height > 1.5 * avg_height

            if original_format != 'PNG' or is_too_big:
                # Adjust size to the average dimensions for previews
                max_preview_size = (avg_width, avg_height) if (avg_width and avg_height) else (800, 600)
                img.thumbnail(max_preview_size, Image.Resampling.LANCZOS)
                self._add_image(img, key_name, is_preview=True)
                self.__save_original_image(original_img, key_name)
            else:
                # Directly add the image if it is a PNG and within size limits
                self._add_image(img, key_name, is_preview=False)

    def _add_image(self, img, key_name, is_preview=False):
        img.load()
        # Determine new canvas size
        new_width = max(self.current_width, img.width)
        new_height = self.current_height + img.height + 20  # Extra space for caption

        # Create or resize the composite image
        new_composite_image = Image.new("RGBA", (new_width, new_height))
        if self.composite_image:
            new_composite_image.paste(self.composite_image, (0, 0))
        self.composite_image = new_composite_image
        self.current_width = new_width

        # Draw caption
        caption_img = Image.new("RGBA", (img.width, 20), (255, 255, 255))
        draw = ImageDraw.Draw(caption_img)
        draw.text((10, 5), key_name + (' (Preview)' if is_preview else ''), fill="black")

        # Paste the image and caption into the composite image
        self.composite_image.paste(img, (0, self.current_height))
        self.composite_image.paste(caption_img, (0, self.current_height + img.height))

        # Update metadata
        if key_name not in self.metadata:
            self.metadata[key_name] = {}

        self.metadata[key_name].update({
            "rect": (0, self.current_height, img.width, self.current_height + img.height),
            "caption": key_name,
            "is_preview": is_preview
        })

        # Update the total height
        self.current_height = new_height

    def __setitem__(self, key_name, image_path):
        self.add_image(image_path, key_name)

    def __getitem__(self, key_name):
        metadata = self.metadata.get(key_name)
        if metadata:
            # Check if original image data is stored in metadata
            if 'original_data' in metadata:
                # Decode the original image from base64
                original_format = metadata.get('original_format', 'PNG')
                
                original_data = base64.b64decode(metadata['original_data'])
                original_image = Image.open(io.BytesIO(original_data))
                #original_image = Image.open(buffer)
                original_image.format = original_format  # Optionally set the format if needed
                return original_image

            elif self.composite_image:
                # If no original data, return the cropped image from the composite
                rect = metadata["rect"]
                return self.composite_image.crop(rect)
        
        raise KeyError(f"Image with key {key_name} not found")

    def save(self):
        pnginfo = PngImagePlugin.PngInfo()
        metadata_str = json.dumps(self.metadata)
        pnginfo.add_text("metadata", metadata_str)
        assert self.composite_image
        self.composite_image.save(self.filename, "PNG", pnginfo=pnginfo)

    def load(self):
        with Image.open(self.filename) as img:
            metadata_str = img.info.get("metadata", "{}")
            self.metadata = json.loads(metadata_str)
            self.composite_image = img.copy()
            self.current_width, self.current_height = img.size

    def __enter__(self):
        self.load()  
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save() 
        if exc_type:
            print(f"An exception occurred: {exc_val}")
        return False  