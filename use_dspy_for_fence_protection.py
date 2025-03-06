import dspy
import ollama

class OllamaChatLM(dspy.LM):
    def __init__(self, model="llama3.2-vision"):
        super().__init__(model=model)
        self.model = model

    def __call__(self, prompt, image_path=None, **kwargs):
        messages = [{"role": "user", "content": prompt}]
        if image_path:
            messages[0]["images"] = [image_path]

        try:
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Error: {e}"

# --- Define the Signature for Fence Monitoring ---
class AdvancedFenceMonitoring(dspy.Signature):
    """Given a surveillance image, detect human presence, proximity to the fence, and suspicious behavior."""

    image_path = dspy.InputField(desc="Path to the surveillance image of the fence.")

    human_detected = dspy.OutputField(desc="True if a human is detected near the fence.")
    proximity = dspy.OutputField(desc="Distance of detected human to the fence in meters (estimate).")
    suspicious_behavior = dspy.OutputField(desc="True if suspicious behavior is detected (e.g., observing fence closely, touching, climbing, cutting).")
    behavior_description = dspy.OutputField(desc="Brief description of the human's behavior.")
    confidence = dspy.OutputField(desc="Confidence score (0 to 1) for the detection and behavior analysis.")

# --- Module that handles the image-based analysis ---
class FenceProtectionModule(dspy.Module):
    def __init__(self, lm):
        super().__init__()
        self.lm = lm

    def forward(self, image_path):
        prompt = (
            "Analyze the given image for security purposes. "
            "1. Detect if any human is present near the fence. "
            "2. Estimate the proximity of the human to the fence in meters. "
            "3. Identify any suspicious behavior such as observing the fence closely, touching, climbing, or cutting. "
            "4. Provide a brief description of the detected behavior. "
            "5. Provide a confidence score (0 to 1) for your analysis."
        )

        response = self.lm(prompt, image_path=image_path)

        # --- Parse the response into structured fields (simple parser example) ---
        fields = {
            'human_detected': 'False',
            'proximity': 'Unknown',
            'suspicious_behavior': 'False',
            'behavior_description': 'No suspicious behavior detected.',
            'confidence': '0.0'
        }

        for line in response.split('\n'):
            line = line.strip()
            if "human detected" in line.lower():
                fields['human_detected'] = 'True' if 'yes' in line.lower() else 'False'
            elif "proximity" in line.lower():
                fields['proximity'] = line.split(':')[-1].strip()
            elif "suspicious behavior" in line.lower():
                fields['suspicious_behavior'] = 'True' if 'yes' in line.lower() else 'False'
            elif "description" in line.lower():
                fields['behavior_description'] = line.split(':')[-1].strip()
            elif "confidence" in line.lower():
                fields['confidence'] = line.split(':')[-1].strip()

        return AdvancedFenceMonitoring(
            image_path=image_path,
            human_detected=fields['human_detected'],
            proximity=fields['proximity'],
            suspicious_behavior=fields['suspicious_behavior'],
            behavior_description=fields['behavior_description'],
            confidence=fields['confidence']
        )

# --- Usage ---
lm = OllamaChatLM()

fence_module = FenceProtectionModule(lm)

image_path = r"C:\Users\Administrator\Documents\llama3_2_vision\fence_uc\all_frames_one_shot\frame_20250301_130222_749118.jpg"

result = fence_module.forward(image_path)

# --- Print the result nicely ---
print(f"\n📊 Fence Monitoring Analysis:")
print(f"Image Path: {result.image_path}")
print(f"Human Detected: {result.human_detected}")
print(f"Proximity to Fence: {result.proximity}")
print(f"Suspicious Behavior: {result.suspicious_behavior}")
print(f"Behavior Description: {result.behavior_description}")
print(f"Confidence Score: {result.confidence}")
