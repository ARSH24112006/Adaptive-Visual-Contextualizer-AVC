# **Adaptive Visual Contextualizer (AVC)**





## **AI for Impact: 5-Day Sprint Submission**



Adaptive Visual Contextualizer is a specialized accessibility utility designed to interpret "visual-only" data. While traditional screen readers are great at reading text, they struggle with complex UI layouts, unlabelled buttons, and data visualizations. AVC uses a locally-hosted Vision-Language Model (VLM) to provide natural language narrations of these elements on demand.



### **Quick Start Guide**



##### **To get the assistant running on your machine immediately, follow these steps:**



##### **1. Local Installation (Recommended):**



This method ensures the global hotkey listener and Windows PowerShell audio bridge have direct hardware access.



```powershell

\# Clone the repository

git clone https://github.com/ARSH24112006/Adaptive-Visual-Contextualizer-AVC.git

cd Screen-AI-Assistant



\# Setup virtual environment

python -m venv venv

.\\venv\\Scripts\\activate



\# Install optimized CPU-only dependencies

pip install -r requirements.txt

```



##### **2. Running the Utility:**



Launch the script: python main.py



Wait for the terminal to say "Brain loaded!" (The first run will download the model weights.After that the application runs completely offline).



Double-tap CAPS LOCK to capture your screen.



The AI will beep, think for a moment, and then narrate the screen content through your speakers.



Press ESC to exit.



##### **3.Technical Architecture:**



###### **a) Model \& Quantization**

I used the SmolVLM-256M-Instruct model because of its high reasoning capability despite its small size. To meet the "CPU-only" requirement of the challenge:



**Dynamic 8-bit Quantization**: I implemented torch.quantization.quantize\_dynamic to compress the model layers. This reduced RAM usage and significantly improved inference speed on standard laptops.



**Offline Processing:** The app is configured to run entirely offline once the initial weights are cached, ensuring user privacy.



###### **b) Threaded Execution**



To prevent the application from freezing during AI inference, I used a multi-threaded approach:



**Thread 1:** Listens for the global pynput hotkey.



**Thread 2:** Handles the mss screen capture and VLM processing.



**Thread 3:** Executes a subprocess to call the Windows PowerShell System.Speech bridge, allowing for non-blocking audio feedback.



##### **4.Docker Support**

For users who want an isolated environment, the project is fully Dockerized.



###### **a) Build the image:**



```powershell

docker build -t screen-ai-assistant .

```

###### **b) Run the container:**



```powershell

docker run -it screen-ai-assistant

```



##### **5.Challenges \& Solutions:**



###### **a) The evdev Error:**

Linux containers require additional packages to access input devices. The Dockerfile installs the necessary system libraries to allow pynput to compile correctly.

###### 

###### **b) Audio Deadlocks:**

Standard Python TTS libraries often block the main execution thread. I bypassed this by piping text directly to the native Windows PowerShell speech engine, which is much more stable for a real-time utility.



###### **c) Repository Bloat:**

During development, large model artifacts accidentally entered the Git history. I used a strict .gitignore and history cleaning to keep the final submission lightweight and focused.



##### **6.Tech Stack:**



**a) Language:** Python 3.10



**b) AI Framework:** HuggingFace Transformers, PyTorch



**c) Vision:** PIL (Pillow), MSS (Multiple Screen Shot)



**d) Automation:** Pynput (Global Hotkey Control)



**e) Ops:** Docker, PowerShell Scripting



##### **7.License:**



This project is submitted for the AI for Impact Challenge and is open for community improvement.
