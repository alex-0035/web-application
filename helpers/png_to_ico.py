from PIL import Image

def convert_to_favicon(image_path, output_path):
    try:
        # Open the image using Pillow
        img = Image.open(image_path)

        # Ensure the image is in the correct size (32x32 pixels)
        img = img.resize((32, 32))

        # Save the image as an ICO file
        img.save(output_path, format="ICO")

        print(f"Image converted to favicon.ico and saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    image_path = "../static/icon.png"
    output_path = "../static/favicon.ico"

    convert_to_favicon(image_path, output_path)
