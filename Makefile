.PHONY:
local-setup:
	uv run ./wet_toast_talk_radio/media_store/data/load_store.py

.PHONY:
transcode: local-setup
	uv run ./wet_toast_talk_radio/main.py transcode

.PHONY:
create-playlist: transcode
	uv run ./wet_toast_talk_radio/main.py create-playlist

.PHONY:
stream: create-playlist
	uv run ./wet_toast_talk_radio/main.py stream