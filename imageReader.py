import torch
from torchvision import models, transforms
from PIL import Image

# Load a pre-trained ResNet model
model = models.resnet50(pretrained=True)
model.eval()  # Set the model to evaluation mode

# Load and preprocess an image
def classify_image(image_path):
    img = Image.open(image_path)
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img_tensor = preprocess(img).unsqueeze(0)  # Add batch dimension

    # Make prediction
    with torch.no_grad():
        outputs = model(img_tensor)
    
    # Get the predicted class
    _, predicted_class = torch.max(outputs, 1)
    return predicted_class.item()

# Example usage
image_path = "path/to/image.jpg"
class_id = classify_image(image_path)
print(f"Predicted class ID: {class_id}")
