import os
import ollama
from fpdf import FPDF
from PIL import Image
import pandas as pd

# Path to the folder with images
image_folder = r'images'
output_folder = r'output'
os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

#set model and models location:
model='llava-phi3'
os.environ["OLLAMA_MODELS"] = "/efs/data/algorithms/models/ollama_models"

# List to store results for database
results = []
# questions = [
#     "Here is a content moderation policy: 

# 4. Alert if you recognize weapons or dangerous elements (knife, gun etc), 
# 6. Alert if someone walks not on routes or pavements or roads (suspected zones), 

#FENCE:
# 1. Alert when human walks near bushes or trees and trying to hide close to the fence, 
# 2. Send message if animal or anything which is not human touches the fence (for false alarm reduction), 
# 3. Alert if human or car or bike is moving towards and getting closer to the gate or fence, 
# 5. Alert if you recognize objects for fence penetration or cut such as blanket or scissors,
# 7. Alert if cars or bikes stop near fence or gate, 
# 8. Alert if you recognize human that lay down or crouch near the fence, 
# 9. Alert if someone stop near the gate or fence, 
# 10. Alert if someone trying to penetrate through the gate or fence by jumping, running, cutting the fence, laying under etc. 

# Does the text/image violate the policy? If so, explain which rule is broken."
# ]

descriptor = \
    [""" 
        You are an image analyser. You detect anomalies and/or dangerous situations in the provided image based on the policies below.
        Answer in an ordered manner with "Yes"/"No" per question, using the same numbering as in the questions. 
        
        1. Is there a person that appears to be hiding?
        2. Are there weapons or dangerous elements (knife, gun, rifle etc.) in the image?
        3. Does the scene appear to be dangerous/abnormal?
        4. Is there a person walking in unapproved/restricted/unnatural zones rather than authorized standard paths such as sidewalks or roads? 
        5. Are there any fences/gates/borders in the image? If the answer is yes, answer the following questions (referring to the fence/gate/border as "fence"), if not continue to 6.:
            5.1. Is a person walking near bushes or trees and trying to hide close to a fence?
            5.2. Is an animal or anything other than a person touching the fence?
            5.3. Is a person/car/bike moving towards the fence? 
            5.4. Are there any objects present that could be used to breach or cut a fence (such as blanket/scissors/hacksaw/Rope/cutters/crowbar etc.)?
            5.5. Is there a car or bike stopping near the fence?
            5.6. Is there a person laying down or crunching near the fence?
            5.7. Is there a person lingering around fence?
            5.8. Is there a person trying to penetrate through the fence by jumping, running, cutting the fence, laying under it etc.?
        
        6.  Were any of the answers to the above questions positive? 
    """]
    
# Function to ask questions and get responses using llava-phi3 model
def ask_questions_llava(image_path):
    questions = [descriptor]   
    
    response_content = []

    # Loop through the questions
    for question in questions:
        print(f"Processing image: {image_path} - Question: {question}")  # Print image and question for monitoring
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': question,
                'images': [image_path]
            }]
        )
        # Get the content of the response
        content = response['message']['content']
        response_content.append((question, content))
        print(f"Finished: {image_path} - Question: {question}")  # Confirm when done

    return response_content

class CustomPDF(FPDF):
    def add_image_with_table(self, image_path, responses):
        self.add_page()
        self.image(image_path, x=10, y=8, w=100)
        self.set_xy(10, 110)
        self.set_font("Arial", size=12)
        for question, content in responses:
            self.multi_cell(0, 10, f"Q: {question}\nA: {content}\n")

# Initialize PDF
pdf = CustomPDF()

# Process each image
for image_filename in os.listdir(image_folder):
    image_path = os.path.join(image_folder, image_filename)
    if os.path.isfile(image_path) and image_path.lower().endswith(('.jpg', '.jpeg', '.png')):  # Only process image files
        responses = ask_questions_llava(image_path)
        pdf.add_image_with_table(image_path, responses)
        
        # Save results for the database
        for question, content in responses:
            results.append([image_path, question, content])

# Save PDF to file
pdf_output_path = os.path.join(output_folder, "llava_analysis_results.pdf")
pdf.output(pdf_output_path)
print(f"PDF generated and saved to: {pdf_output_path}")

# Save database to CSV
csv_output_path = os.path.join(output_folder, f"{model}_analysis_results_v2.csv")
df = pd.DataFrame(results, columns=["Image URL", "Question", "Content"])
df.to_csv(csv_output_path, index=False)
print(f"Database saved to: {csv_output_path}")
