import os
import ollama
import pandas as pd
from fpdf import FPDF
from PIL import Image
import re

# Directory containing the images
image_dir = r"C:\Users\Administrator\Documents\llama3_2_vision\fence_uc\all_frames_one_shot"
output_folder = r"C:\Users\Administrator\Documents\llama3_2_vision\fence_uc\src"
os.makedirs(output_folder, exist_ok=True)

# List to store results for CSV
all_results = []

# Function to ask questions and get responses
def ask_questions(image_path):
    questions = [
        "Q1: answer Yes/No, Is there a person in the image?",
        "Q2: answer Yes/No,Does the person near the fence? YES/NO",
        "Q3: answer Yes/No, Is the person interested in the fence? YES/NO",
        "Q4: answer Yes/No, Can you recognize weapon or objects to cut the fence? YES/NO",
        "Q5: answer Yes/No, Is there a person walking near bushes or trees and trying to hide close to the fence?",
        "Q6: answer Yes/No, Is there an animal or anything other than a person touching the fence?",
        "Q7: answer Yes/No, Is there a person/car/bike moving towards the fence? ",
        "Q8: answer Yes/No, Are there any objects present that could be used to breach or cut the fence (such as blanket/scissors/hacksaw/Rope/cutters/crowbar etc.)?",
        "Q9: answer Yes/No, Is there a car or bike stopping near the fence?",
        "Q10: answer Yes/No, Is there a person laying down or crouching near the fence?",
        "Q11: answer Yes/No, Did a person stop near the fence?",
        "Q12: answer Yes/No, Is there a person trying to penetrate through the fence? for example by jumping over the fence, running, cutting the fence, going under it etc.",
    ]

    response_content = []

    for question in questions:
        print(f"Processing image: {image_path} - Question: {question}")
        try:
            response = ollama.chat(
                model="llama3.2-vision",
                messages=[{
                    "role": "user",
                    "content": question,
                    "images": [image_path]
                }]
            )
            print(f"Ollama Response: {response}")
            content = response["message"]["content"]

            match = re.search(r'\b(Yes|No)\b', content, re.IGNORECASE)
            if match:
                content = match.group(1)
            else:
                content = "No clear Yes/No response"

            if content:
                response_content.append((question, content))
            else:
                print(f"Warning: Empty response content for question: {question}")
        except Exception as e:
            print(f"Error processing question: {question} - {e}")

        print(f"Finished: {image_path} - Question: {question}")

    return response_content

# Create the PDF
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def add_image_with_table(self, image_path, responses):
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
            self.multi_cell(0, 10, f"Answer: {content}")
            self.ln(5)

# Initialize PDF
pdf = PDF()

# Process all images in the directory
image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    responses = ask_questions(image_path)
    pdf.add_image_with_table(image_path, responses)

    # Save results for CSV
    image_results = [image_file]
    for _, content in responses:
        image_results.append(1 if content.lower() == "yes" else 0)
    all_results.append(image_results)

# Save PDF to file
pdf_output_path = os.path.join(output_folder, "ollama_analysis_results_all_frames_11B_Q4.pdf")
pdf.output(pdf_output_path)
print(f"PDF generated and saved to: {pdf_output_path}")

# Save CSV
csv_output_path = os.path.join(output_folder, "ollama_analysis_results_all_frames_11B_Q4.csv")
columns = ["Image Name", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10", "Q11", "Q12"]
df = pd.DataFrame(all_results, columns=columns)
df.to_csv(csv_output_path, index=False)
print(f"Database saved to: {csv_output_path}")