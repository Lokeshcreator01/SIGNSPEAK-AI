import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.video import Video
from kivy.uix.popup import Popup
from kivy.clock import Clock
import sounddevice as sd
import requests
import threading
import os
import json

kivy.require('2.1.0')

class ASLApp(App):
    def build(self):
        self.is_recording = False
        self.samplerate = 16000
        self.duration = 3  # seconds (can be adjusted)
        self.filename = "recorded.wav"

        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Top buttons
        self.button_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        self.start_button = Button(text="🎙️ Start Listening")
        self.stop_button = Button(text="🛑 Stop Listening")

        self.start_button.bind(on_press=self.start_recording)
        self.stop_button.bind(on_press=self.stop_recording)

        self.button_layout.add_widget(self.start_button)
        self.button_layout.add_widget(self.stop_button)
        self.layout.add_widget(self.button_layout)

        # Result label
        self.result_label = Label(text="Prediction: ", size_hint=(1, 0.2), font_size=18)
        self.layout.add_widget(self.result_label)

        return self.layout

    def start_recording(self, instance):
        self.is_recording = True
        threading.Thread(target=self.record_audio).start()

    def stop_recording(self, instance):
        self.is_recording = False

    def record_audio(self):
        print("Recording started...")
        samplerate = self.samplerate
        blocksize = 1024  # Size of each chunk (you can adjust this)
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            # Send the audio chunk to the server for processing
            self.send_audio_chunk(indata)

        with sd.InputStream(callback=audio_callback, channels=1, samplerate=samplerate, blocksize=blocksize):
            print("Recording... Press 'Stop Listening' to stop.")
            while self.is_recording:
                sd.sleep(1000)  # Sleep for 1 second before processing the next chunk

    def send_audio_chunk(self, chunk):
        try:
            # Send the audio chunk to the server for prediction
            response = requests.post(
                "http://192.168.139.194:5000/predict",  # Replace with your server IP
                files={'audio': chunk}
            )
            
            if response.status_code == 200:
                data = response.json()
                asl_gloss = data['asl_gloss']
                video_file = data['gesture_video']
                self.update_result(asl_gloss)
                self.play_video(video_file)
            else:
                self.update_result("Error from server.")
        except requests.exceptions.RequestException as e:
            self.update_result(f"Network error: {str(e)}")
        except Exception as e:
            self.update_result(f"Exception: {str(e)}")

    def update_result(self, text):
        Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', f"Prediction: {text}"))

    def play_video(self, video_file):
        video_path = os.path.join("gesture_videos", video_file)
        if not os.path.exists(video_path):
            print(f"Video not found: {video_path}")
            self.update_result("Video file not found.")
            return

        video = Video(source=video_path, state='play')
        popup = Popup(title="ASL Gesture", content=video, size_hint=(None, None), size=(640, 480))
        popup.open()

if __name__ == '__main__':
    ASLApp().run()
