import os
import ollama
import pandas as pd
from PIL import Image
from fpdf import FPDF

image_folder = r"C:\Users\Administrator\Documents\llama3_2_vision\fence_uc\all_frames_one_shot"
pdf_output_path = r"C:\Users\Administrator\Documents\ollama_analysis_results_llama_3_2_fp16.pdf"
csv_output_path = r"C:\Users\Administrator\Documents\ollama_analysis_results_llama_3_2_fp16.csv"

results = []
questions = [
    "Is there a person in the image? YES/NO",
    "Does the person near the fence? YES/NO",
    "Is the person interested in the fence? YES/NO",
    "Can you recognize weapon or objects to cut the fence? YES/NO",
]

def get_ollama_response(image_path, prompt):
    try:
        response = ollama.chat(
            model="llama3.2-vision:11b-instruct-fp16",  # Updated model
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [image_path]
            }]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"Error getting Ollama response: {e}")
        return "Error retrieving response"

image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
image_files = image_files[:20]  # Limit to 20 images

class PDF(FPDF):
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
        self.multi_cell(0, 10, f"Image: {os.path.basename(image_path)}")
        self.ln(5)
        self.set_font("Arial", "", 10)
        for question, answer in responses:
            self.set_font("Arial", "B", 10)
            self.multi_cell(0, 10, f"Question: {question}")
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 10, f"Answer: {answer}")
            self.ln(5)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)

for image_file in image_files:
    image_path = os.path.join(image_folder, image_file)
    responses_for_image = []

    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        continue

    print(f"Processing image: {image_file}") #print current image.

    for question in questions:
        print(f"  Question: {question}") #print current question.
        answer = get_ollama_response(image_path, question)
        print(f"  Answer: {answer}") #print current answer.
        responses_for_image.append((question, answer))
        results.append([image_file, question, answer])

    pdf.add_image_with_table(image_path, responses_for_image)

pdf.output(pdf_output_path)
print(f"PDF generated and saved to: {pdf_output_path}")

df = pd.DataFrame(results, columns=["Image File", "Question", "Answer"])
df.to_csv(csv_output_path, index=False)
print(f"CSV saved to: {csv_output_path}")