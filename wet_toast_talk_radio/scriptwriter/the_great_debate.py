import json
import random
from itertools import cycle
from pathlib import Path

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
You are an edgy, satirical author.
{{~/system}}
{{#block hidden=True}}
{{#user~}}
Your task is to generate single-word character traits. Here are some examples:
Megalomania
Cowardice
Greed
Now generate a single-word character trait.
{{~/user}}
{{#assistant~}}
{{gen 'trait' temperature=0.95 max_tokens=5}}
{{~/assistant}}
{{/block}}
{{#user~}}
Your task is to write character profiles. {{name}} is a {{gender}} who is passionately {{polarity}} {{topic}}.
{{name}}'s main character trait is {{trait}}.
Describe {{name}} in three sentences.
{{~/user}}
{{#assistant~}}
{{gen 'description' temperature=0.9 max_tokens=200}}
{{~/assistant}}
{{#user~}}
Now list five arguments that {{name}} would make {{polarity}} {{topic}} in a debate.
{{~/user}}
{{#assistant~}}
{{gen 'arguments' temperature=0.9 max_tokens=500}}
{{~/assistant}}
{{#user~}}
Now summarize these arguments as terse bullet points.
{{~/user}}
{{#assistant~}}
{{gen 'bullet_points' temperature=0.9 max_tokens=200}}
{{~/assistant}}
{{#user~}}
Now invent an unexpected backstory for {{name}} explaining why they are so {{polarity}} {{topic}}. Explain this backstory in one sentence.
{{~/user}}
{{#assistant~}}
{{gen 'backstory' temperature=0.9 max_tokens=100}}
{{~/assistant}}
"""

DEBATE_TEMPLATE = """{{#system~}}
You are an edgy, satirical author.
{{~/system}}
{{#user~}}
Here are the descriptions of two characters: {{guest_in_favor}} and {{guest_against}}.
Imagine that these two characters are discussing the pros and cons of {{topic}}.
They are stubborn, emotional, and stuck in disagreement. The conversation is chaotic and eccentric.
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
        guest_in_favor = await guest(
            topic=self.topic,
            polarity="in favor of",
            name="Alice",
            gender="woman",
            trait="megalomania",
        )
        guest_against = await guest(
            topic=self.topic,
            polarity="against",
            name="Bob",
            gender="man",
            trait="gluttony",
        )

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


GENDERS = ["male", "female"]


# TODO how to inject this name?
def random_name(gender: str):
    if gender not in GENDERS:
        raise ValueError(f"Gender: {gender} must be one of {GENDERS}")
    # TODO cleanup
    path = Path(__file__).with_name("resources") / "names-ascii.json"
    with path.open() as f:
        doc = json.load(f)
    region = doc[random.randrange(len(doc))]
    names = region[gender]
    name = names[random.randrange(len(names))]
    return name
