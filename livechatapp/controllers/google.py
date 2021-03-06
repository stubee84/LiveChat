from google.cloud import storage, speech, texttospeech
from google.resumable_media.requests import ResumableUpload
import google.auth.transport.requests as tr_requests

from .redis import redisController
from typing import Tuple
from logging import error
from asgiref.sync import async_to_sync
from .utils import logger

import json, requests, google.auth, threading, queue, channels.layers, ffmpeg, base64, sys

class google_text_to_speech:
    def __init__(self):
        self.text_client: texttospeech.TextToSpeechAsyncClient = texttospeech.TextToSpeechAsyncClient()
        self.channel_layer = channels.layers.get_channel_layer()
    
    async def transcribe_text(self, text: str) -> Tuple[bytes, error]:
        synthesize_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
                language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = await self.text_client.synthesize_speech(input=synthesize_input, voice=voice, audio_config=audio_config)

        try:
            process = (
                ffmpeg
                .input('pipe:', format='mp3', acodec='mp3')
                .output('pipe:', format='mulaw', acodec='pcm_mulaw', ac=1, ar='8k')
                .run_async(pipe_stdin=True, pipe_stdout=True)
            )

            out, err = process.communicate(input=response.audio_content)
        except ffmpeg.Error as e:
            logger.error(e.stderr, file=sys.stderr)
            return bytes(0)

        return out, err

    async def begin_audio_stream(self, streamSid: str, in_bytes: bytes):
        msg = {
            "event": "media",
            "streamSid": streamSid,
            "media": {
                "payload": base64.b64encode(in_bytes).decode("ascii"),
            }
        }

        await self.channel_layer.group_send(streamSid, {
            "type": "chat_message",
            "message": json.dumps(msg)
        }) 


class google_transcribe_speech:
    def __init__(self):
        self.storage_client: storage.Client = None
        self.speech_client: speech.SpeechClient = None
        self.stream_queue: queue.Queue = None
        self.stream_finished: bool = False
        self.transport: tr_requests.AuthorizedSession = None
        # self.bucket_name: str = os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET_NAME")
        # self.upload_url: str = u'https://www.googleapis.com/upload/storage/v1/b/{bucket}/o?uploadType=resumable'.format(bucket=self.bucket_name)
        self.wr_scope: str = u'https://www.googleapis.com/auth/devstorage.read_write'

    async def connect(self, **kwargs):
        '''
            params: destination - for connection to Google Cloud Storage use `storage`, for Google Cloud Speech use `speech`
        '''
        try:
            if kwargs['destination'].lower() == "storage":
                self.storage_client = storage.Client()
                credentials, _ = google.auth.default(scopes=(self.wr_scope,))
                self.transport = tr_requests.AuthorizedSession(credentials)
            elif kwargs['destination'].lower() == "speech":
                self.speech_client = speech.SpeechClient()
        except KeyError as e:
            logger.error(e)
            return
        
    async def start_transcriptions_stream(self, call_sid: str):
        from_number = redisController.get(key=call_sid)
        await self.connect(destination="speech")
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MULAW,
            sample_rate_hertz=8000,
            language_code="en-US",
        )
        streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

        self.stream_queue = queue.Queue()
        thread = threading.Thread(target=self.send_to_google, args=(streaming_config,from_number,))
        thread.start()
    
    async def end_stream(self):
        self.stream_finished = True

    #method to add audio chunk to queue
    async def add_req_to_queue(self, chunk: str):
        self.stream_queue.put(speech.StreamingRecognizeRequest(audio_content=bytes(chunk)))

    #generator to get chunk of data from queue
    def get_req_from_queue(self):
        while not self.stream_finished:
            yield self.stream_queue.get()

    #run in its own thread space
    def send_to_google(self, streaming_config: speech.StreamingRecognitionConfig, from_number: str):
        channel_layer = channels.layers.get_channel_layer()
        #start the streaming recognition and block, using the queue, until data becomes available
        for response in self.speech_client.streaming_recognize(config=streaming_config, requests=self.get_req_from_queue(),):
            self.print_transcription_response(response, channel_layer, from_number)
            if self.stream_finished:
                return
        
    def print_transcription_response(self, response, channel_layer, from_number: str):
        if not response.results:
            return
        
        result = response.results[0]
        if not result.alternatives:
            return
        
        transcription = result.alternatives[0].transcript
        async_to_sync(channel_layer.group_send)(f"chat_{from_number}", {
            "type": "chat_message",
            'stream': True,
            "message": f'{transcription}'
        })

    def download_audio_and_upload(self, recording_sid: str, recording_url: str) -> str:
        # chunk_resp: requests.Response = None
        response = requests.get(url=recording_url, stream=True)
        # filename = f"{recording_sid}.wav"
        content_type = u"audio/wav"
        # #metadata name key is the blob_name to upload to
        metadata = {u'name': recording_sid}

        self.connect(destination="storage")
        #chunk must be divisible by 256.0
        upload = ResumableUpload(self.upload_url, 1024 * 256)
        #the response.raw is the raw bytes from http response. it is only useable if you provide stream=True in the request
        gc_resp = upload.initiate(self.transport, response.raw, metadata, content_type, stream_final=False)

        if gc_resp.status_code == 200:
            while not upload.finished:
                _ = upload.transmit_next_chunk(self.transport)
        else:
            logger.info(f"Google Cloud Response: {gc_resp.status_code}")

        return 'gs://{bucket_name}/{blob_name}'.format(self.bucket_name, recording_sid)

    def transcribe_audio(self, gcs_uri: str) -> str:
        self.connect(destination="speech")
        audio = speech.RecognitionAudio(uri=gcs_uri)
        config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,sample_rate_hertz=8000,language_code="en-US")

        operation = self.speech_client.long_running_recognize(request={"config":config,"audio":audio})

        logger.info("Waiting for operation to complete")
        response = operation.result(timeout=90)

        for result in response.results:
            transcript = u'Transcript: {}'.format(result.alternatives[0].transcript)
            print(u'Confidence: {}'.format(result.alternatives[0].confidence))
        
        return transcript

    def download_audio_and_transcribe(self, recording_url: str) -> str:
        transcription: str = ""
        self.connect(destination="speech")
        response = requests.get(url=recording_url, stream=True)

        reqs = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in response.iter_content())
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=8000,
            language_code="en-US",
        )
        streaming_config = speech.StreamingRecognitionConfig(config=config)

        responses = self.speech_client.streaming_recognize(config=streaming_config, requests=reqs,)

        for response in responses:
            # Once the transcription has settled, the first result will contain the
            # is_final result. The other results will be for subsequent portions of
            # the audio.
            for result in response.results:
                # print("Finished: {}".format(result.is_final))
                # print("Stability: {}".format(result.stability))
                alternatives = result.alternatives
                # The alternatives are ordered from most likely to least.
                for alternative in alternatives:
                    # print("Confidence: {}".format(alternative.confidence))
                    transcription = u"{}".format(alternative.transcript)

        return transcription