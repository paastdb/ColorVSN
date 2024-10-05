import cv2
from moviepy.editor import VideoFileClip

def apply_night_vision(frame):
    # Apply brightness and contrast effect
    brightness_contrast = brightness_contrast_effect(frame)
    
    # Apply infrared effect
    infrared = infared_effect(brightness_contrast)
    
    # Apply colormap effect
    colormap = apply_colormap(infrared)
    
    
    return colormap

def brightness_contrast_effect(frame):
    contrast = 2.0  # Contrast control (0 to 127)
    brightness = 0.0  # Brightness control (0-100)

    # Call addWeighted function. Use beta = 0 to effectively only operate on one image
    out = cv2.addWeighted(frame, contrast, frame, 0, brightness)
    
    return out

def infared_effect(frame):
    cimg = frame
    plt_image = cv2.cvtColor(cimg, cv2.COLOR_BGR2RGB)
    
    inv_cimg = ~cimg.copy()
    inv_cimg[:, :, 1] = 0
    inv_cimg[:, :, 2] = 0
    
    plt_image = cv2.cvtColor(inv_cimg, cv2.COLOR_BGR2RGB)
    
    inv_hsv = cv2.cvtColor(inv_cimg, cv2.COLOR_BGR2HSV)
    img_hsv = cv2.cvtColor(cimg, cv2.COLOR_BGR2HSV)

    dst = cv2.addWeighted(inv_hsv[:, :, 0] , .9, img_hsv[:, :, 0] , .9, 0)
    img_hsv[:, :, 0] = dst
    hue_cimg = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)

    plt_image = hue_cimg
    
    plt_image = cv2.cvtColor(hue_cimg, cv2.COLOR_BGR2RGB)
    frame = plt_image

    return frame

def apply_colormap(frame):
    # Read the input image
    input_image = frame
    autumn = cv2.COLORMAP_AUTUMN
    bone = cv2.COLORMAP_BONE 
    jet = cv2.COLORMAP_JET
    winter = cv2.COLORMAP_WINTER 
    rainbow = cv2.COLORMAP_RAINBOW
    ocean = cv2.COLORMAP_OCEAN 
    summer = cv2.COLORMAP_SUMMER 
    spring = cv2.COLORMAP_SPRING
    cool = cv2.COLORMAP_COOL 
    hsv = cv2.COLORMAP_HSV 
    pink = cv2.COLORMAP_PINK 
    hot = cv2.COLORMAP_HOT 
    parula = cv2.COLORMAP_PARULA 
    magma = cv2.COLORMAP_MAGMA 
    inferno = cv2.COLORMAP_INFERNO 
    plasma = cv2.COLORMAP_PLASMA 
    viridis = cv2.COLORMAP_VIRIDIS 
    cividis = cv2.COLORMAP_CIVIDIS 
    twilight = cv2.COLORMAP_TWILIGHT 
    twilightShift = cv2.COLORMAP_TWILIGHT_SHIFTED 
    turbo = cv2.COLORMAP_TURBO 
    deepgreen = cv2.COLORMAP_DEEPGREEN

    # Apply the specified colormap
    colormap_image = cv2.applyColorMap(input_image, deepgreen)
    frame = colormap_image
    
    return frame

def main():
    # Open video file
    input_video_path = 'input_video.mp4'
    cap = cv2.VideoCapture(input_video_path)
    
    # Check if video file opened successfully
    if not cap.isOpened():
        print("Error: Unable to open video file")
        return

    # Get input video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    codec = cv2.VideoWriter_fourcc(*'mp4v')

    # Define codec and create VideoWriter object
    out = cv2.VideoWriter('output_video.mp4', codec, fps, (width, height))

    # Process each frame
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Apply night vision effect to the frame
        processed_frame = apply_night_vision(frame)

        # Write the processed frame to output video
        out.write(processed_frame)

        # Display the processed frame
        cv2.imshow('Night Vision', processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    # Merge processed video with original audio using moviepy
    original_clip = VideoFileClip(input_video_path)
    processed_clip = VideoFileClip('Future-1-output.mp4')
    final_clip = processed_clip.set_audio(original_clip.audio)
    final_clip.write_videofile('Future-1-final.mp4', codec='libx264', audio_codec='aac')

if __name__ == "__main__":
    main()
