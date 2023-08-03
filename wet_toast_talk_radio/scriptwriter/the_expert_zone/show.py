import structlog
from guidance import Program
from guidance.llms import LLM
import time

from wet_toast_talk_radio.common.dialogue import Line, Speaker
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow
from wet_toast_talk_radio.scriptwriter.the_expert_zone.missions import (
    random_host_missions,
)
from wet_toast_talk_radio.scriptwriter.the_expert_zone.titles import random_title
from wet_toast_talk_radio.scriptwriter.the_expert_zone.topics import random_topic
from wet_toast_talk_radio.scriptwriter.the_expert_zone.traits import random_trait

logger = structlog.get_logger()

AGENT_TEMPLATE = """
{{~#geneach 'conversation' stop=False}}
{{#system~}}
{{await 'system_message'}}
{{~/system}}{{#if first_question}}{{#assistant~}}
{{first_question}}
{{~/assistant}}{{/if}}
{{#user~}}
{{set 'this.question' (await 'question') hidden=False}}
{{~/user}}
{{#assistant~}}
{{gen 'this.response' temperature=1.2 max_tokens=150}}
{{~/assistant}}
{{~/geneach}}"""

# This doesn't require a llm, but using template language for clarity.
SYSTEM_MESSAGE_TEMPLATE = (
    "You are {{identity}}. You are {{role}}. {{mission}} "
    "You always answer in four sentences or less."
)


class TheExpertZone(RadioShow):
    """A radio show where expert guests are interviewed about their specialities."""

    def __init__(
        self,
        topic: str,
        trait: str,
        title: str,
        host_missions: list[str],
        llm: LLM,
        media_store: MediaStore,
    ):
        self.topic = topic
        self.trait = trait
        self.title = title
        self.host_missions = host_missions
        self._llm = llm
        self._media_store = media_store

    async def awrite(self, show_id: ShowId) -> bool:
        logger.info("Async writing The Expert Zone")
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
        guest_identity = f"Ian, an expert researcher in {self.topic}. You are exceptionally {self.trait}"
        guest_role = "the guest on a talk show"
        guest_mission = "Do not repeat yourself throughout the conversation."
        system_message_prompt = Program(text=SYSTEM_MESSAGE_TEMPLATE, llm=self._llm)
        guest_system_message = system_message_prompt(
            identity=guest_identity, role=guest_role, mission=guest_mission
        )

        intro = (
            f"Welcome to 'The Expert Zone', the show where we ask experts the difficult questions... "
            f"This is your star host, Nick, and today we welcome Ian, {self.title} {self.topic}. Ian, how are you?"
        )
        guest = await guest(system_message=guest_system_message, question=intro)

        host_identity = "Nick, a stupid and rude radio celebrity who hates their job"
        host_role = "the host of a talk show"

        print(self.host_missions)
        # Body
        for i, host_mission in enumerate(self.host_missions):
            # first question needed for conversation context
            first_question = intro if i == 0 else None
            host_system_message = system_message_prompt(
                identity=host_identity, role=host_role, mission=host_mission
            )
            host = await host(
                first_question=first_question,
                system_message=host_system_message,
                question=guest["conversation"][-2]["response"],
            )
            guest = await guest(
                system_message=guest_system_message,
                question=host["conversation"][-2]["response"],
            )

            # TODO remove
            time.sleep(0.5)

        # Outro
        outro = (
            "Well, that's all the time we have today! "
            "Ian, thank you for sharing your knowledge with us, "
            "and I wish you all the best in your groundbreaking research. "
            "Join us next time on 'The Expert Zone', where we ask the experts the difficult questions!"
        )
        guest = await guest(system_message=guest_system_message, question=outro)

        print("HOST:")
        print(host)
        print("GUEST:")
        print(guest)

        logger.debug("Written script", conversation=guest["conversation"])
        logger.info("Finished writing The Expert Zone")

        lines = self._post_processing(guest)

        # TODO remove
        print(lines)
        n_words = sum([len(line.content.split(" ")) for line in lines])
        print(f"Number of words: {n_words}")

        self._media_store.put_script_show(show_id=show_id, lines=lines)
        return True

    def _post_processing(self, program: Program) -> list[Line]:
        logger.debug("Post processing The Expert Zone")
        # TODO randomize host and guest
        host = Speaker(name="Nick", gender="male", host=True)
        guest = Speaker(name="Ian", gender="male", host=False)

        # TODO remove new lines from questions and responses
        # TODO also for other shows
        conversation = program["conversation"]
        lines = []
        # last exchange is always empty
        for exchange in conversation[:-1]:
            lines.append(Line(speaker=host, content=exchange["question"]))
            lines.append(Line(speaker=guest, content=exchange["response"]))
        return lines

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "RadioShow":
        topic = random_topic()
        logger.info("Random topic", topic=topic)
        trait = random_trait()
        logger.info("Random trait", trait=trait)
        title = random_title()
        logger.info("Random title", title=title)
        host_missions = random_host_missions(topic=topic, k=8)
        logger.info("Random host missions", missions=host_missions)

        return cls(
            topic=topic,
            trait=trait,
            title=title,
            host_missions=host_missions,
            llm=llm,
            media_store=media_store,
        )
