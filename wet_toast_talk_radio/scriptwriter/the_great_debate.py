# ruff: noqa: E501
import asyncio
import random

import structlog
from guidance import Program
from guidance.llms import LLM

from wet_toast_talk_radio.common.log_ctx import show_id_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.names import (
    GENDERS,
    PLACEHOLDER_NAMES,
    random_name,
)
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow
from wet_toast_talk_radio.scriptwriter.topics import load_topics
from wet_toast_talk_radio.scriptwriter.traits import load_traits

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


class TheGreatDebate(RadioShow):
    def __init__(self, llm: LLM, media_store: MediaStore):
        self._llm = llm
        self._media_store = media_store
        self.topic = random.choice(TOPICS).lower()
        self.trait_in_favor = random.choice(TRAITS).lower()
        self.trait_against = random.choice(TRAITS).lower()
        self.gender_in_favor = random.choice(GENDERS)
        self.gender_against = random.choice(GENDERS)
        self.name_in_favor = random_name(self.gender_in_favor)
        self.name_against = random_name(self.gender_against)
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
            trait_in_favor=self.trait_in_favor,
            trait_against=self.trait_against,
            gender_in_favor=self.gender_in_favor,
            gender_against=self.gender_against,
            name_in_favor=self.name_in_favor,
            name_against=self.name_against,
        )

        logger.info("Writing guest profiles")
        guest = Program(text=GUEST_TEMPLATE, llm=self._llm, async_mode=True)
        task_in_favor = asyncio.create_task(
            aexec(
                guest,
                topic=self.topic,
                polarity="in favor of",
                name=PLACEHOLDER_NAMES["in_favor"][self.gender_in_favor],
                gender=self.gender_in_favor,
                trait=self.trait_in_favor,
            )
        )
        task_against = asyncio.create_task(
            aexec(
                guest,
                topic=self.topic,
                polarity="against",
                name=PLACEHOLDER_NAMES["against"][self.gender_against],
                gender=self.gender_against,
                trait=self.trait_against,
            )
        )
        results = await asyncio.gather(task_in_favor, task_against)
        guest_in_favor = results[0]
        guest_against = results[1]
        logger.debug("Guest in favor", guest=guest_in_favor)
        logger.debug("Guest against", guest=guest_against)

        logger.info("Writing debate script")
        debate = Program(text=DEBATE_TEMPLATE, llm=self._llm, async_mode=True)
        written_debate = await debate(
            topic=self.topic,
            in_favor=self.guest_to_dict(guest_in_favor),
            against=self.guest_to_dict(guest_against),
        )
        logger.debug("Written debate", debate=written_debate)
        content = self._post_processing(written_debate["script"])

        logger.info("Finished writing The Great Debate")
        logger.debug("Final script", content=content)
        self._media_store.put_script_show(show_id=show_id, content=content)
        return True

    def _post_processing(self, script: str) -> str:
        logger.info("Post processing The Great Debate")
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
        assert (
            bad_lines_ratio < self.max_bad_lines_ratio
        ), f"Too many bad lines, {bad_lines_ratio}%"
        clean_script = "\n".join(clean_lines)
        clean_script = self.replace_guest_names(clean_script)
        return clean_script

    @staticmethod
    def is_good_line(line: str) -> bool:
        return ":" in line

    @staticmethod
    def guest_to_dict(guest: Program) -> dict[str, str]:
        return {
            "name": guest["name"],
            "description": guest["description"],
            "trait": guest["trait"],
            "arguments": guest["bullet_points"],
            "backstory": guest["backstory"],
        }

    def replace_guest_names(self, script: str) -> str:
        logger.debug(
            "Replacing placeholder guest names",
            name_in_favor=self.name_in_favor,
            name_against=self.name_against,
        )
        script = script.replace(
            PLACEHOLDER_NAMES["in_favor"][self.gender_in_favor], self.name_in_favor
        )
        script = script.replace(
            PLACEHOLDER_NAMES["against"][self.gender_against], self.name_against
        )
        return script


async def aexec(program: Program, **kwargs) -> Program:
    """For some reason the program await is messed up so we have to wrap in this async function"""
    return await program(**kwargs)
