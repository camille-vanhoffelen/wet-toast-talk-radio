.PHONY:
local-setup:
	pdm run local-setup

.PHONY:
transcode: local-setup
	pdm run disc-jockey transcode

.PHONY:
create-playlist: transcode
	pdm run disc-jockey create-playlist

.PHONY:
stream: create-playlist
	pdm run disc-jockey stream
