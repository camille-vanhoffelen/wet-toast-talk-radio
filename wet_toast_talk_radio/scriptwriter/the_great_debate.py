from itertools import cycle

import structlog
from guidance import Program
from guidance.llms import LLM

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow

logger = structlog.get_logger()

TOPICS = cycle(
    [
        "toilet paper",
        "eating your boogers",
        "investing all your life savings in bitcoin",
    ]
)

# TODO randomize names
GUEST_TEMPLATE = """{{#system~}}
You are an edgy, satirical writer who writes character profiles.
{{~/system}}
{{#user~}}
Think of the most stereotypical person who would argue {{polarity}} of the use of {{topic}}.
Describe them in three sentences.
{{~/user}}
{{#assistant~}}
{{gen 'description' temperature=0.9 max_tokens=100}}
{{~/assistant}}
"""

DEBATE_TEMPLATE = """{{#user~}}
Here are the descriptions of two characters: {{guest_in_favor}} and {{guest_against}}.
Imagine that these two characters are discussing the pros and cons of {{topic}}.
They are stubborn, emotional, and stuck in disagreement. The conversation is chaotic.
They cut each other off often, still disagree at the end, and remain bitter.
Now generate a dialogue for this conversation of roughly 1000 words.
Your response should be a dialogue in the following format:
X: Hi, how are you?
Y: I'm good, thanks. And you?
X: I'm pretty good.
{{~/user}}
{{#assistant~}}
{{gen 'script' temperature=0.9 max_tokens=1500}}
{{~/assistant}}"""


class TheGreatDebate(RadioShow):
    def __init__(self, llm: LLM, media_store: MediaStore):
        self._llm = llm
        self._media_store = media_store
        self.topic = next(TOPICS)
        self.n_speakers = 2

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "TheGreatDebate":
        return cls(llm=llm, media_store=media_store)

    async def awrite(self, show_id: ShowId) -> bool:
        logger.info("Async writing the great debate", show_id=show_id, topic=self.topic)

        guest = Program(text=GUEST_TEMPLATE, llm=self._llm, async_mode=True)
        guest_in_favor = await guest(topic=self.topic, polarity="in favor")
        guest_against = await guest(topic=self.topic, polarity="against")

        debate = Program(text=DEBATE_TEMPLATE, llm=self._llm, async_mode=True)
        written_debate = await debate(
            topic=self.topic,
            guest_in_favor=guest_in_favor["description"],
            guest_against=guest_against["description"],
        )
        logger.info(written_debate)

        content = self._post_processing(written_debate["script"])
        self._media_store.put_script_show(show_id=show_id, content=content)
        return True

    def _post_processing(self, script: str) -> str:
        # TODO Remove last sentence if truncated ? or just generate a lot?
        # TODO Add host interjection at the end
        # TODO try agent generation
        # TODO if most of the lines start with SPEAKER: then remove lines without speaker
        # TODO SUFFIX host that interrupts "that's all we have time for this today"
        script = script.strip()
        lines = script.split("\n\n")
        speakers = set()
        clean_lines = []
        for line in lines:
            assert (
                ":" in line
            ), f"Expected line of format 'speaker: text', but got: {line}"
            speaker, text = line.split(":", maxsplit=1)
            speakers.add(speaker.strip().lower())
            clean_lines.append(line.strip())
        assert (
            len(speakers) == self.n_speakers
        ), f"Expected {self.n_speakers} speakers, but got: {len(speakers)}"
        clean_script = "\n".join(clean_lines)
        return clean_script
