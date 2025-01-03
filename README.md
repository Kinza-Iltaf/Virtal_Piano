# Virtal_Piano
An interactive virtual piano that allows users to play music through hand gestures.

# Virtual Piano Project 🎹

## Overview
This project is a **Virtual Piano** application that uses:
- **OpenCV** for webcam input and video processing.
- **Mediapipe** for hand tracking and detecting finger positions.
- **Pygame** for sound playback.

The application allows users to play piano notes by moving their fingers over designated key regions on the screen.

## Features
- **Dynamic Gradient Background:** Creates an immersive and visually appealing interface.
- **Hand Tracking:** Tracks fingertip positions using Mediapipe's hand landmarks.
- **Sound Playback:** Plays corresponding piano notes when a fingertip hovers over a key region.
- **Custom Key Layout:** Supports both black and white piano keys with distinct styles.
- **Interactive Visuals:** Highlights the currently pressed key and fingertip movements.

## Requirements
Before running the project, ensure you have the following installed:
- Python 3.x
- OpenCV (`pip install opencv-python`)
- Mediapipe (`pip install mediapipe`)
- Pygame (`pip install pygame`)
- NumPy (`pip install numpy`)

## How to Run
1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/your-username/virtual-piano.git
