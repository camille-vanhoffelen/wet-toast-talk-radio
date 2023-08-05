import random
from dataclasses import dataclass

import structlog
from guidance import Program
from guidance.llms import LLM

from wet_toast_talk_radio.common.dialogue import Line, Speaker
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.names import (
    GENDERS,
    random_name,
)
from wet_toast_talk_radio.scriptwriter.prolove.missions import host_missions, random_host_missions, DETAILS, ADVICE
from wet_toast_talk_radio.scriptwriter.prolove.genders import Gender
from wet_toast_talk_radio.scriptwriter.prolove.sexual_orientations import random_sexual_orientation
from wet_toast_talk_radio.scriptwriter.prolove.traits import random_trait
from wet_toast_talk_radio.scriptwriter.prolove.topics import random_topic
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow

logger = structlog.get_logger()

AGENT_TEMPLATE = """
{{~#geneach 'conversation' stop=False}}
{{#system~}}
{{await 'system_message'}}
{{~/system}}{{#if first_question}}
{{#assistant~}}
{{first_question}}
{{~/assistant}}{{/if}}
{{#user~}}
{{set 'this.question' (await 'question') hidden=False}}
{{~/user}}
{{#assistant~}}
{{gen 'this.response' temperature=1.3 max_tokens=400}}
{{~/assistant}}
{{~/geneach}}"""

# This doesn't require a llm, but using template language for clarity.
SYSTEM_MESSAGE_TEMPLATE = (
    "{{identity}} {{role}} {{mission}} "
    # "You always answer in {{n_sentences}} sentences or less."
)


@dataclass
class Guest:
    name: str
    gender: Gender
    age: int
    sexual_orientation: str
    voice_gender: str
    trait: str
    topic: str
    # used to prevent biases in dialogue generation due to guest name
    placeholder_name: str




class Prolove(RadioShow):
    """A dating advice radio show."""

    def __init__(
        self,
        guest: Guest,
        intro_host_missions: list[str],
        convo_host_missions: list[str],
        llm: LLM,
        media_store: MediaStore,
    ):
        self.guest = guest
        self.intro_host_missions = intro_host_missions
        self.convo_host_missions = convo_host_missions
        self._llm = llm
        self._media_store = media_store

    async def awrite(self, show_id: ShowId) -> bool:
        logger.info("Async writing Prolove")
        guest = Program(
            text=AGENT_TEMPLATE,
            first_question=None,
            llm=self._llm,
            async_mode=True,
            await_missing=True,
        )
        host = Program(
            text=AGENT_TEMPLATE,
            llm=self._llm,
            async_mode=True,
            await_missing=True,
        )

        # Intro
        intro = (
            "Welcome to 'Prolove', the dating advice show where we say YES to love! "
            "This is your dearest host, Zara, ready to answer all your questions about love and connection. "
        )
        host_identity = (
            "You are Zara, a kind and caring dating coach who is unconsciously self-obsessed. "
            # "You are Zara, a kind and caring dating coach who is self-obsessed. "
            "You speak calmly yet confidently."
            # TODO Keep this.
            # "You don't realise that you give terrible dating advice."
            # TODO keep this below as a particular mission where you mention solosexuality. Keep this identity section light and persona based.
            # "You are proudly solosexual, and you think relationships and sex are all about yourself. "
            # "You are proudly solosexual, and you think it fosters self-empowerment and self-love. "
            # TODO keep this below too DEFAULT should be just her character and keeping the conversation going, like Nick
            # TODO the juice comes from combos of specific missions
            # "You secretly have never had a serious relationship, and don't admit that you'd rather masturbate alone than have sex. "
        )
        host_role = "You are the host of a radio talk show."
        system_message_prompt = Program(text=SYSTEM_MESSAGE_TEMPLATE, llm=self._llm)

        for mission in self.intro_host_missions[:-1]:
            host_system_message = system_message_prompt(
                identity=host_identity,
                role=host_role,
                mission=mission,
            )
            host = await host(
                system_message=host_system_message,
                question="",
                first_question=intro,
            )

        # TODO extract conversation part 1 here
        conversation = host["conversation"][:-1]

        # Convo
        # TODO shy hesitant embarrassed confused sad scared nervous happy starstruck excited
        guest_identity = (
            f"Your name is {self.guest.placeholder_name}, and you are {self.guest.age} years old. "
            f"You are {self.guest.gender.to_noun()} and you are {self.guest.sexual_orientation}. "
            f"You are very {self.guest.trait}."
        )
        guest_role = "You are the guest on a talk show."
        guest_mission = (
                        "You introduce yourself to the host and listeners. "
                        "You mention your age, gender, and sexual orientation."
                        "You always answer in four sentences or less."
        )
        guest_system_message = system_message_prompt(
            identity=guest_identity,
            role=guest_role,
            mission=guest_mission,
        )
        new_caller = "It looks like we have a caller on the line. Hello sweetie, you're on the air."
        # TODO more personal intro, start with anecdote or how we doing everyone? I'm this and that"
        # TODO randomize anecdote topic
        guest = await guest(system_message=guest_system_message, question=new_caller)

        host_system_message = system_message_prompt(
            identity=host_identity,
            role=host_role,
            mission=self.intro_host_missions[-1],
        )
        host = await host(
            system_message=host_system_message,
            question=guest["conversation"][-2]["response"],
            first_question=new_caller,
        )

        guest_mission = (
            f"You are to ask Zara about {self.guest.topic}."
            "You always answer in four sentences or less."
        )
        guest_system_message = system_message_prompt(
            identity=guest_identity,
            role=guest_role,
            mission=guest_mission,
        )
        guest = await guest(system_message=guest_system_message, question=host["conversation"][-2]["response"])

        host_system_message = system_message_prompt(
            identity="",
            role="",
            mission=DETAILS
        )
        host = await host(
            system_message=host_system_message,
            question=guest["conversation"][-2]["response"],
            first_question=None,
        )

        guest_mission = (
            "You describe your concern in great details. "
            "Refer to specific events and your emotions. "
            "You always answer in six sentences or less."
        )
        guest_system_message = system_message_prompt(
            identity=guest_identity,
            role=guest_role,
            mission=guest_mission,
        )
        guest = await guest(system_message=guest_system_message, question=host["conversation"][-2]["response"])

        host_system_message = system_message_prompt(
            identity=host_identity,
            role=host_role,
            mission=ADVICE,
        )
        host = await host(
            system_message=host_system_message,
            question=guest["conversation"][-2]["response"],
            first_question=None,
        )

        guest_mission = (
            "You appreciate Zara's advice, and compliment her for it. "
            # TODO maybe not
            "You ask for clarification on a specific point. "
            "You always answer in four sentences or less."
        )
        guest_system_message = system_message_prompt(
            identity=guest_identity,
            role=guest_role,
            mission=guest_mission,
        )
        guest = await guest(system_message=guest_system_message, question=host["conversation"][-2]["response"])

        # more bad advice
        host_system_message = system_message_prompt(
            identity=host_identity,
            role=host_role,
            mission=ADVICE,
        )
        host = await host(
            system_message=host_system_message,
            question=guest["conversation"][-2]["response"],
            first_question=None,
        )

        guest_mission = (
            "You agree with Zara's advice, and compliment her for it. "
            "You mention that you'll try your best. "
            "You always answer in four sentences or less."
        )
        guest_system_message = system_message_prompt(
            identity=guest_identity,
            role=guest_role,
            mission=guest_mission,
        )
        guest = await guest(system_message=guest_system_message, question=host["conversation"][-2]["response"])

        for mission in self.convo_host_missions:
            host_system_message = system_message_prompt(
                identity=host_identity,
                role=host_role,
                mission=mission,
            )
            host = await host(
                system_message=host_system_message,
                question=guest["conversation"][-2]["response"],
                first_question=None,
            )

            guest_mission = (
                # TODO maybe?
                # "You keep the conversation going with Zara. "
                "Do not thank Zara. "
                "You always answer in two sentences or less."
            )
            guest_system_message = system_message_prompt(
                identity=guest_identity,
                role=guest_role,
                mission=guest_mission,
            )
            guest = await guest(system_message=guest_system_message, question=host["conversation"][-2]["response"])

        # TODO extract more conversation here


        logger.debug("Written script", conversation=conversation)
        logger.info("Finished writing The Expert Zone")

        lines = self._post_processing(conversation)

        self._media_store.put_script_show(show_id=show_id, lines=lines)
        return True

    def _post_processing(self, conversation: list) -> list[Line]:
        """Converts the guidance program into a list of Lines.
        Cleans up the content for each line."""
        logger.debug("Post processing The Expert Zone")
        host = Speaker(name="Nick", gender="male", host=True)
        guest = Speaker(name=self.guest.name, gender=self.guest.voice_gender, host=False)

        lines = []
        # last exchange is always empty
        for exchange in conversation[:-1]:
            # TODO non-binary voice selection
            lines.append(
                Line(speaker=host, content=self._clean_content(exchange["question"]))
            )
            lines.append(
                Line(speaker=guest, content=self._clean_content(exchange["response"]))
            )
        return lines

    def _clean_content(self, content: str) -> str:
        """Replace placeholder names, remove new lines and extra whitespace."""
        content = content.replace(self.guest.placeholder_name, self.guest.name)
        content = " ".join(content.strip().split())
        return content

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "RadioShow":
        # TODO careful redefine variable
        guest_gender = Gender.random()
        if guest_gender == Gender.NON_BINARY:
            guest_voice_gender = random.choice(GENDERS)
        else:
            guest_voice_gender = guest_gender.value
        guest_name = random_name(guest_voice_gender)
        guest_placeholder_name = random_name(guest_voice_gender)
        guest_sexual_orientation = random_sexual_orientation(guest_gender)
        # TODO random distribution (triangle?)
        age = random.randint(18, 85)
        topic = random_topic()
        trait = random_trait()
        guest = Guest(
            name=guest_name,
            gender=guest_gender,
            voice_gender=guest_voice_gender,
            sexual_orientation=guest_sexual_orientation,
            age=age,
            trait=trait,
            topic=topic,
            placeholder_name=guest_placeholder_name,
        )
        logger.info("Random guest", guest=guest)

        intro_host_missions = host_missions()
        convo_host_missions = random_host_missions(k=4)
        logger.info("Random host missions", missions=host_missions)

        return cls(
            guest=guest,
            intro_host_missions=intro_host_missions,
            convo_host_missions=convo_host_missions,
            llm=llm,
            media_store=media_store,
        )