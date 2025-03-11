import os
import ollama
import pandas as pd
from fpdf import FPDF
from PIL import Image
import re

# Directory containing the images and output folder
image_dir = r"C:\Users\Administrator\Documents\llama3_2_vision\fence_uc\obvious_frames"
output_folder = r"C:\Users\Administrator\Documents\llama3_2_vision\fence_uc\src"
os.makedirs(output_folder, exist_ok=True)

# List to store results for CSV
all_results = []

# Function to ask questions and get responses from the algorithm
def ask_questions(image_path):
    # Single multi-line prompt combining all aspects
    questions = [
       """Examine the provided image thoroughly for any signs of a fence breach or anomaly. Look for the following:
        Fence Breach: Are there any people near the fence that appear to be attempting to cross, cut, or otherwise interact with it suspiciously?
        Object/Tool Inspection: Do you see any objects or tools (such as scissors, rope, crowbar, hacksaw, etc.) that could be used to breach the fence?
        Movement Analysis: Is there any movement of people, vehicles, or bikes moving toward the fence that may indicate an imminent breach?
        Hidden Intrusion Check: Are there any individuals hiding near bushes, trees, or other cover adjacent to the fence?
        Anomaly Detection: Do you notice any other unusual behaviors or anomalies in the scene that might signal a security threat?
        If any suspicious activity is detected in any of these aspects, respond with 'alert'; otherwise, respond with 'all clear'."""
    ]
    
    response_content = []
    
    for question in questions:
        print(f"Processing image: {image_path} - Question: {question}")
        try:
            response = ollama.chat(
                model="llama3.2-vision",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a fence penetration and anomaly detection system. "
                            "Analyze the provided image and answer only with 'alert' if any suspicious "
                            "activity or potential breach is detected, or 'all clear' if nothing suspicious is seen."
                        )
                    },
                    {
                        "role": "user",
                        "content": question,
                        "images": [image_path]
                    }
                ]
            )
            print(f"Ollama Response: {response}")
            content = response["message"]["content"]

            # Look for alert or all clear, or yes/no response
            match = re.search(r'\b(alert|all clear|Yes|No)\b', content, re.IGNORECASE)
            if match:
                content = match.group(1)
            else:
                content = "No clear response"

            response_content.append((question, content))
        except Exception as e:
            print(f"Error processing question: {question} - {e}")
        print(f"Finished processing {image_path}")
    
    return response_content

# Create the PDF class
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def add_image_with_table(self, image_path, responses, user_response):
        self.add_page()

        img = Image.open(image_path)
        img_width, img_height = img.size
        max_width, max_height = 190, 150
        scale = min(max_width / img_width, max_height / img_height, 1)
        img_width, img_height = int(img_width * scale), int(img_height * scale)
        self.image(image_path, x=10, y=self.get_y(), w=img_width, h=img_height)
        self.ln(img_height + 5)

        self.set_font("Arial", "I", 10)
        self.multi_cell(0, 10, f"Image URL: {image_path}")
        self.ln(5)

        self.set_font("Arial", "", 10)
        for question, content in responses:
            self.set_font("Arial", "B", 10)
            self.multi_cell(0, 10, f"Question: {question}")
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 10, f"Algorithm Answer: {content}")
            self.ln(5)
        # Add user response at the end
        self.set_font("Arial", "B", 10)
        self.multi_cell(0, 10, f"User Response: {user_response}")
        self.ln(5)

# Initialize PDF
pdf = PDF()

# Get list of image files
image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# For detection percentage calculation
total_images = 0
matching_count = 0

# Process each image
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    
    # Get algorithm response
    responses = ask_questions(image_path)
    
    # Display the image to the user
    img = Image.open(image_path)
    img.show()  # This will open the image in the default image viewer
    user_input = input(f"Do you see an alert in {image_file}? (Y for Yes / N for No): ")
    user_response = "alert" if user_input.strip().lower() == "y" else "all clear"
    
    # Add the image, algorithm responses, and user response to the PDF
    pdf.add_image_with_table(image_path, responses, user_response)
    
    # Save results for CSV
    # We assume a single overall algorithm response from the multi-line prompt (using the first response)
    if responses:
        alg_response = responses[0][1].strip().lower()
    else:
        alg_response = "no response"
    
    # Convert responses to binary: alert -> 1, all clear -> 0
    alg_binary = 1 if alg_response in ["alert", "yes"] else 0
    user_binary = 1 if user_response in ["alert", "yes"] else 0
    image_results = [image_file, alg_binary, user_binary]
    all_results.append(image_results)
    
    total_images += 1
    if alg_binary == user_binary:
        matching_count += 1

# Save PDF to file
pdf_output_path = os.path.join(output_folder, "ollama_analysis_results_obvious_frames_11B_Q4.pdf")
pdf.output(pdf_output_path)
print(f"PDF generated and saved to: {pdf_output_path}")

# Save CSV with updated columns
csv_output_path = os.path.join(output_folder, "ollama_analysis_results_obvious_frames_11B_Q4.csv")
columns = ["Image Name", "Algorithm Response", "User Response"]
df = pd.DataFrame(all_results, columns=columns)
df.to_csv(csv_output_path, index=False)
print(f"CSV saved to: {csv_output_path}")

# Calculate detection percentage (accuracy)
if total_images > 0:
    detection_percentage = (matching_count / total_images) * 100
    print(f"Detection Percentage (Accuracy): {detection_percentage:.2f}%")
else:
    print("No images processed.")
