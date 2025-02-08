import sys
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QWidget, QStyle
import win32gui
import win32con
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import accentcolordetect

SPOTIPY_CLIENT_ID = ''
SPOTIPY_CLIENT_SECRET = ''
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-read-playback-state user-modify-playback-state'
print(f"Starting taskbar progress bar: \nID:{SPOTIPY_CLIENT_ID}\nSECRET: {SPOTIPY_CLIENT_SECRET}")

class SpotifyClient:
    def __init__(self):
        self.sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                     client_secret=SPOTIPY_CLIENT_SECRET,
                                     redirect_uri=SPOTIPY_REDIRECT_URI,
                                     scope=SCOPE)
        self.sp = self.get_spotify_client()
    
    def get_spotify_client(self):
        try:
            token_info = self.sp_oauth.get_cached_token()
            if not token_info:
                auth_url = self.sp_oauth.get_authorize_url()
                print(f"Please navigate here to authorize: {auth_url}")
                response = input("Enter the URL you were redirected to: ")
                code = self.sp_oauth.parse_response_code(response)
                token_info = self.sp_oauth.get_access_token(code)
                print("Spotify authorization successful")
            else:
                print("Using cached token")
            return spotipy.Spotify(auth=token_info['access_token'])
        except spotipy.SpotifyException as e:
            print(f"Error obtaining Spotify client: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)

    def refresh_token(self):
        try:
            token_info = self.sp_oauth.get_cached_token()
            if not token_info or self.sp_oauth.is_token_expired(token_info):
                token_info = self.sp_oauth.refresh_access_token(token_info['refresh_token'])
                self.sp = spotipy.Spotify(auth=token_info['access_token'])
                print("Spotify token refreshed")
        except spotipy.SpotifyException as e:
            print(f"Error refreshing token: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def get_song_progress(self):
        try:
            self.refresh_token()
            current_playback = self.sp.current_playback()
            if current_playback:
                progress_ms = current_playback['progress_ms']
                duration_ms = current_playback['item']['duration_ms']
                is_playing = current_playback['is_playing']
                return progress_ms, duration_ms, is_playing
            return 0, 1, False
        except spotipy.SpotifyException as e:
            print(f"Error fetching song progress: {e}")
            return 0, 1, False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 0, 1, False

    def seek(self, position_ms):
        try:
            self.refresh_token()
            self.sp.seek_track(position_ms)
            print(f"Seeked to position: {position_ms} ms")
        except spotipy.SpotifyException as e:
            print(f"Error seeking track: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

class FetchThread(QThread):
    data_fetched = pyqtSignal(int, int, bool)

    def __init__(self, spotify_client):
        super().__init__()
        self.spotify_client = spotify_client

    def run(self):
        while True:
            try:
                progress_ms, duration_ms, is_playing = self.spotify_client.get_song_progress()
                self.data_fetched.emit(progress_ms, duration_ms, is_playing)
                self.msleep(300)
            except Exception as e:
                print(f"Error in fetch thread: {e}")
                self.data_fetched.emit(None, None, False)

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 1022, 1920, 22)

        self.progressBar = QSlider(Qt.Orientation.Horizontal)
        self.progressBar.setMaximum(10000)
        self.progressBar.setMaximumHeight(3)
        self.set_stylesheet()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.progressBar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        print("UI initialized successfully")

        try:
            self.spotify_client = SpotifyClient()
            print("Spotify client initialized")
        except Exception as e:
            print(f"Error initializing Spotify client: {e}")
            sys.exit(1)

        self.fetch_thread = FetchThread(self.spotify_client)
        self.fetch_thread.data_fetched.connect(self.update_song_progress)
        self.fetch_thread.start()
        print("Fetch thread started")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress_bar)
        self.timer.start(100)
        print("Timer started")

        self.progress_ms = 0
        self.duration_ms = 1
        self.is_playing = False

    def set_stylesheet(self):
        try:
            self.progressBar.setStyleSheet(f"""
               QSlider::groove:horizontal {{
                   background-color: transparent;
                   border: 0px solid #424242;
                   height: 8px;
                   border-top-right-radius: 4px;
                   border-bottom-right-radius: 4px;
               }}
               QSlider::sub-page:horizontal {{
                   background-color: {accentcolordetect.accent()[1]};
                   border: 0px solid #424242;
                   height: 8px;
                   border-top-right-radius: 4px;
                   border-bottom-right-radius: 4px;
               }}
               QSlider::handle:hover {{
                   background-color: {accentcolordetect.accent()[1]};
                   border: 4px solid rgb(0, 0, 0);
                   width: 8px;
                   margin-top: -4px;
                   margin-bottom: -4px;
                   border-radius: 8px;
               }}
            """)
            print("Stylesheet applied successfully")
        except Exception as e:
            print(f"Error setting stylesheet: {e}")

    def update_song_progress(self, progress_ms, duration_ms, is_playing):
        try:
            self.set_stylesheet()
            
            if progress_ms is not None and duration_ms is not None:

                self.progress_ms = progress_ms
                self.duration_ms = duration_ms
                self.is_playing = is_playing
                self.keep_on_top()
        except Exception as e:
            print(f"Error updating song progress: {e}")

    def update_progress_bar(self):
        try:
            if self.is_playing :
                self.progress_ms += 100
                if self.progress_ms > self.duration_ms:
                    self.progress_ms = self.duration_ms
                percentage = (self.progress_ms / self.duration_ms) * 100
                self.progressBar.setValue(int(percentage * 100))
        except Exception as e:
            print(f"Error updating progress bar: {e}")

    def keep_on_top(self):
        try:
            hwnd = int(self.winId())
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_NOOWNERZORDER)
        except Exception as e:
            print(f"Error keeping window on top: {e}")

app = QApplication(sys.argv)
demo = Window()
demo.show()
sys.exit(app.exec())
