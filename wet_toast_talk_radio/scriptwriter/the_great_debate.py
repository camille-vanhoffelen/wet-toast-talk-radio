import json
import random
from pathlib import Path

import structlog
from guidance import Program
from guidance.llms import LLM

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow
from wet_toast_talk_radio.scriptwriter.topics import load_topics
from wet_toast_talk_radio.scriptwriter.traits import load_traits

logger = structlog.get_logger()

TOPICS = load_topics()
TRAITS = load_traits()

# TODO randomize names
# TODO Add talking style? maybe only 4-5 with cycle? rude, terse, chatty, aggressive, shy, bored
# TODO CoT for the arguments?
# TODO simplify language for descriptions?
GUEST_TEMPLATE = """{{#system~}}
You are an edgy, satirical writer.
{{~/system}}
{{#user~}}
Your task is to write character profiles. {{name}} is a {{gender}} who is strongly {{polarity}} {{topic}}.
{{name}}'s main character trait is {{trait}}.
Describe {{name}} in three sentences with a casual and informal style.
{{~/user}}
{{#assistant~}}
{{gen 'description' temperature=0.9 max_tokens=200}}
{{~/assistant}}
{{#user~}}
Now list five arguments that {{name}} would make {{polarity}} {{topic}} in a debate.
The arguments do not need to follow logic or common sense, but they should fit the character's personality.
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

# TODO add backstories and arguments
DEBATE_TEMPLATE = """{{#system~}}
You are an edgy, satirical writer.
{{~/system}}
{{#user~}}
Chris is a radio show host who hosts "The Great Debate", a radio show where guests call in to discuss the pros and cons of particular topics.
Alice and Bob are today's guests, and have never met before.
Alice and Bob are stubborn, emotional, and stuck in disagreement. The conversation is chaotic and eccentric.
The characters grow gradually frustrated, cut each other off often, still disagree at the end, and remain bitter.
Chris sometimes interjects to try to calm the guests down, and redirect the conversation, but is mostly ignored.
Your task is to write this radio show conversation.

Here are the descriptions of the two guests:

Alice
Character trait: {{in_favor.trait}}
Description: {{in_favor.description}}
Arguments: 
{{in_favor.arguments}}
Backstory: {{in_favor.backstory}}

Bob
Character trait: {{against.trait}}
Description: {{against.description}}
Arguments: 
{{against.arguments}}
Backstory: {{against.backstory}}

Each line should start with the name of the speaker, followed by a colon and a space.

Here's an example conversation:
Chris: Welcome to The Great Debate! Today's topic is {{topic}}. We have two guests on the line, Alice and Bob, ready to battle it out. Alice, what do you think about {{topic}}?
Alice: I think {{topic}} is great!
Chris: What about you, Bob?
Bob: That I sure don't. I can't stand it!
Chris: Then let the debate begin!
Alice: Why don't you like it, Bob?

Now generate this long conversation in 2000 words. Please include the guests' arguments and style their speech according to their character traits.
{{~/user}}
{{#assistant~}}
{{gen 'script' temperature=0.9 max_tokens=1500}}
{{~/assistant}}"""


class TheGreatDebate(RadioShow):
    def __init__(self, llm: LLM, media_store: MediaStore):
        self._llm = llm
        self._media_store = media_store
        self.topic = random.choice(TOPICS).lower()
        self.trait1 = random.choice(TRAITS).lower()
        self.trait2 = random.choice(TRAITS).lower()
        self.n_speakers = 3
        self.max_bad_lines_ratio = 0.05

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "TheGreatDebate":
        return cls(llm=llm, media_store=media_store)

    async def awrite(self, show_id: ShowId) -> bool:
        logger.info(
            "Async writing the great debate",
            show_id=show_id,
            topic=self.topic,
            trait1=self.trait1,
            trait2=self.trait2,
        )

        guest = Program(text=GUEST_TEMPLATE, llm=self._llm, async_mode=True)
        guest_in_favor = await guest(
            topic=self.topic,
            polarity="in favor of",
            name="Alice",
            gender="woman",
            trait=self.trait1,
        )
        guest_against = await guest(
            topic=self.topic,
            polarity="against",
            name="Bob",
            gender="man",
            trait=self.trait2,
        )
        logger.info(guest_in_favor)
        logger.info(guest_against)

        debate = Program(text=DEBATE_TEMPLATE, llm=self._llm, async_mode=True)
        written_debate = await debate(
            topic=self.topic,
            in_favor=self.guest_to_dict(guest_in_favor),
            against=self.guest_to_dict(guest_against),
        )
        logger.info(written_debate)

        # TODO prepend show introduction (maybe introduce guests and backstories?)

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
        script = script.replace("\n\n", "\n")
        lines = script.split("\n")
        speakers = set()
        clean_lines = []
        bad_lines_counter = 0
        for line in lines:
            if self.is_good_line(line):
                speaker, text = line.split(":", maxsplit=1)
                speakers.add(speaker.strip().lower())
                clean_lines.append(line.strip())
            else:
                bad_lines_counter += 1
                logger.warning("Skipping bad line", line=line)
                continue
        assert (
            len(speakers) == self.n_speakers
        ), f"Expected {self.n_speakers} speakers, but got: {len(speakers)}"
        bad_lines_ratio = bad_lines_counter / len(lines)
        assert bad_lines_ratio < self.max_bad_lines_ratio, f"Too many bad lines, {bad_lines_ratio}%"
        clean_script = "\n".join(clean_lines)
        return clean_script

    @staticmethod
    def is_good_line(line: str) -> bool:
        return ":" in line

    @staticmethod
    def guest_to_dict(guest: Program) -> dict[str, str]:
        return {
            "description": guest["description"],
            "trait": guest["trait"],
            "arguments": guest["bullet_points"],
            "backstory": guest["backstory"],
        }


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
