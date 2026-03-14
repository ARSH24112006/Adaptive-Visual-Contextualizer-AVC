import time
import os
import subprocess
import threading
import torch
import re
from pynput import keyboard
from mss import mss
from PIL import Image
from transformers import AutoProcessor, Idefics3ForConditionalGeneration


os.environ['TRANSFORMERS_OFFLINE'] = '1'
torch.set_num_threads(4)


# SPEECH
def speak_now(text):
    """Uses Windows PowerShell to speak. This is thread-safe and won't lock up."""
    print(f"Talking: {text}")
    # Escape single quotes for PowerShell
    clean_text = text.replace("'", "")
    ps_command = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{clean_text}")'

    # Run speech in background so it doesn't freeze the AI
    def _run():
        subprocess.run(["powershell", "-Command", ps_command], capture_output=True)

    threading.Thread(target=_run).start()


# INITIALIZE AI BRAIN
print("Loading model...")
MODEL_ID = "HuggingFaceTB/SmolVLM-256M-Instruct"
processor = AutoProcessor.from_pretrained(MODEL_ID, local_files_only=True)
model = Idefics3ForConditionalGeneration.from_pretrained(
    MODEL_ID, torch_dtype=torch.float32, local_files_only=True
).to("cpu")
model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)

is_processing = False


@torch.inference_mode()
def get_ai_description(image_path):
    img = Image.open(image_path).convert("RGB")
    img.thumbnail((768, 768))
    messages = [{"role": "user", "content": [
        {"type": "image"},
        {"type": "text", "text": "You are a helpful screen-reading assistant. "
                "Look at this image and start your response by the description of the page and the pictures "
                "Describe the most important information first, such as the main title, primary data or the graphs"
                " and then the graphical information that can be interpreted from the graph(if graph present) "
                "and the overall purpose of the screen. Keep it to 4-5 logical sentences."}
    ]}]
    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=prompt, images=[img], return_tensors="pt").to("cpu")

    generated_ids = model.generate(
        **inputs,
        max_new_tokens=75,
        do_sample=False,
        use_cache=True,
        repetition_penalty=1.5,
        no_repeat_ngram_size=3,
        pad_token_id=processor.tokenizer.eos_token_id
    )
    result = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    clean_text = result.split("Assistant:")[-1].strip()

    if not clean_text.lower().startswith("this page"):
        clean_text = "This page contains " + clean_text

    # Polish sentence endings
    match = list(re.finditer(r'[.!?]', clean_text))
    if match:
        clean_text = clean_text[:match[-1].start() + 1]
    return clean_text


def capture_focused_window():
    global is_processing
    try:
        # Beep for feedback
        # This sends a single 1000Hz beep for 300 milliseconds
        os.system('powershell -Command "[console]::Beep(1000, 300)"')

        with mss() as sct:
            mon = sct.monitors[1]

            bbox = {"top": mon["top"] + 80, "left": mon["left"], "width": mon["width"], "height": mon["height"] - 140}
            sct_img = sct.grab(bbox)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img.save("current_capture.png")

            speak_now("Thinking.")
            description = get_ai_description("current_capture.png")
            print(f"AI Result: {description}")
            speak_now(description)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        is_processing = False


# HOTKEY
last_press_time = 0
caps_pressed = False


def on_press(key):
    global last_press_time, caps_pressed, is_processing
    if key == keyboard.Key.esc: os._exit(0)
    if key == keyboard.Key.caps_lock and not caps_pressed:
        caps_pressed = True
        if time.time() - last_press_time < 0.5:
            if not is_processing:
                is_processing = True
                threading.Thread(target=capture_focused_window, daemon=True).start()
            last_press_time = 0
        else:
            last_press_time = time.time()


def on_release(key):
    global caps_pressed
    if key == keyboard.Key.caps_lock: caps_pressed = False


if __name__ == "__main__":
    print("Brain loaded! Double-tap CAPS LOCK.")
    speak_now("System active.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()