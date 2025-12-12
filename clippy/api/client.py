from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QSettings
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json

class GreetingClient(QObject):
    # Signal emitted when a new greeting is fetched and ready
    greeting_ready = pyqtSignal(str)

    def __init__(self, api_url="http://127.0.0.1:8080/v1/chat/completions"):
        super().__init__()
        self.api_url = api_url
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self._on_request_finished)
        self.settings = QSettings("Clippy", "PetManager")
        
        self._cached_greeting = None
        self._is_loading = False
        self._partial_response = ""
        
        # Start by fetching one greeting so it's ready
        self.fetch_next()

    def fetch_next(self):
        """Triggers a network request to fetch the next greeting."""
        if self._is_loading:
            return

        self._is_loading = True
        request = QNetworkRequest(QUrl(self.api_url))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        request.setRawHeader(b"Authorization", b"Bearer anythingshoulddo")

        default_prompt = "You are Clippy. You are helpful, annoying, and observant. Generate a short, one-sentence greeting or observation for a programmer."
        system_prompt = self.settings.value("system_prompt", default_prompt)

        payload = {
            "model": "any-model-should-work",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Say something."}
            ],
            "stream": True
        }
        
        json_payload = json.dumps(payload).encode('utf-8')
        self.manager.post(request, json_payload)

    def _on_request_finished(self, reply: QNetworkReply):
        self._is_loading = False
        
        if reply.error() != QNetworkReply.NetworkError.NoError:
            print(f"Error fetching greeting: {reply.errorString()}")
            reply.deleteLater()
            return

        # Handle SSE stream response
        # Since QNetworkAccessManager.finished signal emits when the whole request is done,
        # and we are not using readyRead for real-time streaming here (for simplicity),
        # we will process the entire accumulated buffer.
        # Note: Ideally for long streams we should connect to reply.readyRead(), 
        # but for short greetings this is acceptable.
        
        data = reply.readAll().data()
        try:
            decoded_data = data.decode('utf-8')
        except UnicodeDecodeError:
            print("Error decoding response")
            reply.deleteLater()
            return

        full_message = ""
        
        for line in decoded_data.split('\n'):
            line = line.strip()
            if line.startswith("data:"):
                data_str = line[5:].strip()
                if not data_str or data_str == "[DONE]":
                    continue
                try:
                    payload = json.loads(data_str)
                    delta = payload.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        full_message += delta
                except json.JSONDecodeError:
                    continue

        reply.deleteLater()

        if full_message:
            self._cached_greeting = full_message.strip()
            self.greeting_ready.emit(self._cached_greeting)

    def get_greeting(self):
        """
        Returns the cached greeting if available.
        If a greeting is returned, it triggers a fetch for the next one.
        Returns None if no greeting is available.
        """
        if self._cached_greeting:
            msg = self._cached_greeting
            self._cached_greeting = None
            # Fetch the next one in the background
            self.fetch_next()
            return msg
        
        # If we don't have one, trigger a fetch if not already loading
        if not self._is_loading:
            self.fetch_next()
        return None
