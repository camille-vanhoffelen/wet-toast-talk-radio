# ruff: noqa: E501
import asyncio
import random
from dataclasses import dataclass
from enum import Enum

import structlog
from guidance import Program
from guidance.llms import LLM

from wet_toast_talk_radio.common.dialogue import Line, Speaker
from wet_toast_talk_radio.common.log_ctx import show_id_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.names import (
    GENDERS,
    random_name,
)
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow
from wet_toast_talk_radio.scriptwriter.the_great_debate.topics import load_topics
from wet_toast_talk_radio.scriptwriter.the_great_debate.traits import load_traits

logger = structlog.get_logger()

TOPICS = load_topics()
TRAITS = load_traits()

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

DEBATE_TEMPLATE = """{{#system~}}
You are an edgy, satirical writer.
{{~/system}}
{{#user~}}
Chris is a radio show host who hosts "The Great Debate", a radio show where guests call in to discuss the pros and cons of particular topics.
{{in_favor.name}} and {{against.name}} are today's guests, and have never met before.
{{in_favor.name}} and {{against.name}} are stubborn, emotional, and stuck in disagreement. The conversation is chaotic and eccentric.
The characters grow gradually frustrated, cut each other off often, still disagree at the end, and remain bitter.
Chris sometimes interjects to try to calm the guests down, and redirect the conversation, but is mostly ignored.
Your task is to write this radio show conversation.

Here are the descriptions of the two guests:

{{in_favor.name}}
Character trait: {{in_favor.trait}}
Description: {{in_favor.description}}
Arguments:
{{in_favor.arguments}}
Backstory: {{in_favor.backstory}}

{{against.name}}
Character trait: {{against.trait}}
Description: {{against.description}}
Arguments:
{{against.arguments}}
Backstory: {{against.backstory}}

Each line should start with the name of the speaker, followed by a colon and a space.
Capitalize words for emphasis. The following non-verbal sounds can be used:

Non-verbal sounds:
[laughs]
[sighs]
[gasps]
[clears throat]

Here's an example conversation:
Chris: Welcome to THE GREAT DEBATE! Today's topic is {{topic}}. We have two guests on the line, {{in_favor.name}} and {{against.name}}, ready to battle it out. {{in_favor.name}}, what do you think about {{topic}}?
{{in_favor.name}}: I think {{topic}} is GREAT!
Chris: What about you, {{against.name}}?
{{against.name}}: That I sure don't... I can't stand it!
Chris: Then let the debate begin!
{{in_favor.name}}: [sighs] Why don't you like it, {{against.name}}?

Now generate this long conversation in 2000 words. Please include the guests' arguments and style their speech according to their character traits.
{{~/user}}
{{#assistant~}}
{{gen 'script' temperature=0.9 max_tokens=3000}}
{{~/assistant}}"""


class Polarity(Enum):
    IN_FAVOR = "in favor of"
    AGAINST = "against"


# Neutral names to prevent biasing character profiles
PLACEHOLDER_NAMES = {
    Polarity.IN_FAVOR: {"female": "Emily", "male": "Kevin"},
    Polarity.AGAINST: {"female": "Sarah", "male": "Brian"},
}


@dataclass
class Guest:
    name: str
    gender: str
    trait: str
    polarity: Polarity
    placeholder_name: str

    @classmethod
    def random(cls, polarity: Polarity):
        gender = random.choice(GENDERS)
        name = random_name(gender)
        trait = random.choice(TRAITS).lower()
        placeholder_name = PLACEHOLDER_NAMES[polarity][gender]
        return cls(
            name=name,
            gender=gender,
            trait=trait,
            polarity=polarity,
            placeholder_name=placeholder_name,
        )


class TheGreatDebate(RadioShow):
    """Radio show where two call-in guests debate a topic, moderated by the host."""

    def __init__(  # noqa: PLR0913
        self,
        llm: LLM,
        media_store: MediaStore,
        guest_in_favor: Guest | None = None,
        guest_against: Guest | None = None,
        topic: str | None = None,
    ):
        self._llm = llm
        self._media_store = media_store
        self.topic = topic if topic else random.choice(TOPICS).lower()
        self.guest_in_favor = (
            guest_in_favor
            if guest_in_favor
            else Guest.random(polarity=Polarity.IN_FAVOR)
        )
        self.guest_against = (
            guest_against if guest_against else Guest.random(polarity=Polarity.AGAINST)
        )
        self.n_speakers = 3
        self.max_bad_lines_ratio = 0.1

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "TheGreatDebate":
        return cls(llm=llm, media_store=media_store)

    @show_id_log_ctx()
    async def awrite(self, show_id: ShowId) -> bool:
        logger.info(
            "Async writing the great debate",
            topic=self.topic,
            guest_in_favor=self.guest_in_favor,
            guest_against=self.guest_against,
        )

        logger.info("Async writing guest profiles")
        guest = Program(text=GUEST_TEMPLATE, llm=self._llm, async_mode=True)
        task_in_favor = asyncio.create_task(
            aexec(
                guest,
                topic=self.topic,
                polarity=self.guest_in_favor.polarity.value,
                name=self.guest_in_favor.placeholder_name,
                gender=self.guest_in_favor.gender,
                trait=self.guest_in_favor.trait,
            )
        )
        task_against = asyncio.create_task(
            aexec(
                guest,
                topic=self.topic,
                polarity=self.guest_against.polarity.value,
                name=self.guest_against.placeholder_name,
                gender=self.guest_against.gender,
                trait=self.guest_against.trait,
            )
        )
        results = await asyncio.gather(task_in_favor, task_against)
        results_in_favor = results[0]
        results_against = results[1]
        logger.debug("Guest in favor", guest=results_in_favor)
        logger.debug("Guest against", guest=results_against)

        logger.info("Writing debate script")
        debate = Program(text=DEBATE_TEMPLATE, llm=self._llm, async_mode=True)
        written_debate = await debate(
            topic=self.topic,
            in_favor=self.results_to_dict(results_in_favor),
            against=self.results_to_dict(results_against),
        )
        logger.debug("Written debate", debate=written_debate)
        lines = self._post_processing(written_debate["script"])

        logger.info("Finished writing The Great Debate")
        logger.debug("Final script", content=lines)
        self._media_store.put_script_show(show_id=show_id, lines=lines)
        return True

    def _post_processing(self, script: str) -> list[Line]:
        logger.info("Post processing The Great Debate")

        script = script.strip()
        script = script.replace("\n\n", "\n")
        script = self.replace_guest_names(script)
        lines = script.split("\n")

        speaker_names = set()
        dialogue_lines = []
        bad_lines_counter = 0
        for line in lines:
            if self.is_good_line(line):
                speaker_name, text = line.split(":", maxsplit=1)
                speaker_names.add(speaker_name.strip().lower())
                speaker = self.to_speaker(speaker_name.strip())
                dialogue_lines.append(Line(content=text.strip(), speaker=speaker))
            else:
                bad_lines_counter += 1
                logger.warning("Skipping bad line", line=line)
                continue
        assert (
            len(speaker_names) == self.n_speakers
        ), f"Expected {self.n_speakers} speakers, but got: {len(speaker_names)}"
        bad_lines_ratio = bad_lines_counter / len(lines)
        assert (
            bad_lines_ratio < self.max_bad_lines_ratio
        ), f"Too many bad lines, {bad_lines_ratio}%"
        return dialogue_lines

    @staticmethod
    def is_good_line(line: str) -> bool:
        return ":" in line

    @staticmethod
    def results_to_dict(guest: Program) -> dict[str, str]:
        return {
            "name": guest["name"],
            "description": guest["description"],
            "trait": guest["trait"],
            "arguments": guest["bullet_points"],
            "backstory": guest["backstory"],
        }

    def replace_guest_names(self, script: str) -> str:
        script = script.replace(
            self.guest_in_favor.placeholder_name, self.guest_in_favor.name
        )
        script = script.replace(
            self.guest_against.placeholder_name, self.guest_against.name
        )
        return script

    def to_speaker(self, speaker_name: str) -> Speaker:
        if speaker_name == self.guest_in_favor.name:
            gender = self.guest_in_favor.gender
        elif speaker_name == self.guest_against.name:
            gender = self.guest_against.gender
        elif speaker_name == "Chris":
            gender = "male"
        else:
            raise ValueError(f"Unknown speaker name: {speaker_name}")
        return Speaker(name=speaker_name, gender=gender)


async def aexec(program: Program, **kwargs) -> Program:
    """For some reason the program await is messed up so we have to wrap in this async function"""
    return await program(**kwargs)
