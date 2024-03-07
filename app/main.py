from dotenv import load_dotenv
import os
from recording_bot import RecordingService
from skinwalker_bot import SkinWalker
    
if __name__ == "__main__":
    load_dotenv()
    skinwalker_token = os.environ.get("SKINWALKER_TOKEN")
    recording_service_token = os.environ.get("RECORDING_SERVICE_TOKEN")
    recording_path = os.environ.get("RECORDING_DIRECTORY_PATH")
    recording_service = RecordingService()
    skinwalker_client = SkinWalker(recording_service, recording_path)
    skinwalker_client.start(skinwalker_token)
    recording_service.start(recording_service_token)

