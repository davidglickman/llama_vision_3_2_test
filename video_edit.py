import cv2
import os

# Path to the video file
video_path = r'C:\Users\glick\OneDrive\Desktop\fence database\VID_20250227_082517.mp4'
output_path = r'C:\Users\glick\OneDrive\Desktop\fence database\VID_20250227_082517_cut.mp4'

# Open the video file
cap = cv2.VideoCapture(video_path)

# Get video properties
# Directory containing the video files
video_dir = r'C:\Users\glick\OneDrive\Desktop\fence database'
output_dir = r'C:\Users\glick\OneDrive\Desktop\fence database\videos_for_daphna'

# Loop through all files in the directory
for filename in os.listdir(video_dir):
    if filename.endswith('.mp4'):
        video3_path = os.path.join(video_dir, filename)
        output_path = os.path.join(output_dir, filename.replace('.mp4', '_cut.mp4'))

        # Open the video file
        cap = cv2.VideoCapture(video3_path)

        # Get video pro7perties28
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Create a VideoWriter object to save the new video
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Display the frame number on the video
            cv2.putText(frame, f'Frame: {frame_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Video', frame)

            # Write the frame to the output video
            out.write(frame)

            # Wait for 1 ms and check if the user pressed the 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_count += 1

        # Release the video capture and writer objects
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Ask the user for the frame number to stop
        stop_frame = int(input(f"Enter the frame number to stop the new video for {filename}: "))

        # Re-open the video file and create a new VideoWriter object
        cap = cv2.VideoCapture(video_path)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame_count > stop_frame:
                break

            # Write the frame to the output video
            out.write(frame)
            frame_count += 1

        # Release the video capture and writer objects
        cap.release()
        out.release()
        cv2.destroyAllWindows()
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# Create a VideoWriter object to save the new video
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Display the frame number on the video
    cv2.putText(frame, f'Frame: {frame_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Video', frame)

    # Write the frame to the output video
    out.write(frame)

    # Wait for 1 ms and check if the user pressed the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_count += 1

# Release the video capture and writer objects
cap.release()
out.release()
cv2.destroyAllWindows()

# Ask the user for the frame number to stop
stop_frame = int(input("Enter the frame number to stop the new video: "))

# Re-open the video file and create a new VideoWriter object
cap = cv2.VideoCapture(video_path)
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame_count > stop_frame:
        break

    # Write the frame to the output video
    out.write(frame)
    frame_count += 1

# Release the video capture and writer objects
cap.release()
out.release()
cv2.destroyAllWindows()