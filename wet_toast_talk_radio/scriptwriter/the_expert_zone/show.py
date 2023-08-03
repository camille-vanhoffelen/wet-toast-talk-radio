import structlog
from guidance import Program
from guidance.llms import LLM

from wet_toast_talk_radio.common.dialogue import Line, Speaker
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow
from wet_toast_talk_radio.scriptwriter.the_expert_zone.missions import (
    random_host_missions,
)

logger = structlog.get_logger()

AGENT_TEMPLATE = """
{{~#geneach 'conversation' stop=False}}
{{#system~}}
{{await 'system_message'}}
{{~/system}}
{{#user~}}
{{set 'this.question' (await 'question') hidden=False}}
{{~/user}}
{{#assistant~}}
{{gen 'this.response' temperature=0.9 max_tokens=150}}
{{~/assistant}}
{{~/geneach}}"""

# This doesn't require a llm, but using template language for clarity.
SYSTEM_MESSAGE_TEMPLATE = """You are {{identity}}.
You are {{role}}.
{{mission}}
You always answer in four sentences or less."""


# TODO remove
# You keep the show going


class TheExpertZone(RadioShow):
    """A radio show where expert guests are interviewed about their specialities."""

    def __init__(
        self,
        topic: str,
        trait: str,
        host_missions: list[str],
        llm: LLM,
        media_store: MediaStore,
    ):
        self.topic = topic
        self.trait = trait
        self.host_missions = host_missions
        self._llm = llm
        self._media_store = media_store

    async def awrite(self, show_id: ShowId) -> bool:
        logger.info("Async writing The Expert Zone")
        guest = Program(
            text=AGENT_TEMPLATE,
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
        guest_identity = f"Ian, a {self.trait} expert researcher in {self.topic}"
        guest_role = "the guest on a talk show"
        guest_mission = "You answer each question informatively and politely. Do not repeat yourself throughout the conversation."
        system_message_prompt = Program(text=SYSTEM_MESSAGE_TEMPLATE, llm=self._llm)
        guest_system_message = system_message_prompt(
            identity=guest_identity, role=guest_role, mission=guest_mission
        )

        intro = (
            f"Welcome to 'The Expert Zone', the show where we ask experts the difficult questions... "
            f"This is your star host, Nick, and today we welcome Ian, an expert researcher in {self.topic}. Ian, how are you?"
        )
        guest = await guest(system_message=guest_system_message, question=intro)

        host_identity = "Nick, a stupid and rude radio celebrity who hates their job"
        host_role = "the host of a talk show"

        for host_mission in self.host_missions:
            host_system_message = system_message_prompt(
                identity=host_identity, role=host_role, mission=host_mission
            )
            host = await host(
                system_message=host_system_message,
                question=guest["conversation"][-2]["response"],
            )
            guest = await guest(
                system_message=guest_system_message,
                question=host["conversation"][-2]["response"],
            )

        print("HOST:")
        print(host)

        logger.debug("Written script", conversation=guest["conversation"])
        logger.info("Finished writing The Expert Zone")

        lines = self._post_processing(guest)
        print(lines)
        self._media_store.put_script_show(show_id=show_id, lines=lines)
        return True

    def _post_processing(self, program: Program) -> list[Line]:
        logger.debug("Post processing The Expert Zone")
        # TODO randomize host and guest
        host = Speaker(name="Nick", gender="male", host=True)
        guest = Speaker(name="Ian", gender="male", host=False)

        conversation = program["conversation"]
        lines = []
        # last exchange is always empty
        for exchange in conversation[:-1]:
            lines.append(Line(speaker=host, content=exchange["question"]))
            lines.append(Line(speaker=guest, content=exchange["response"]))
        return lines

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "RadioShow":
        topic = "Dust Dynamics"
        # trait = "boring"
        trait = "arrogant"
        host_missions = random_host_missions(topic=topic, k=10)
        logger.info("Random topic", topic=topic)
        logger.info("Random trait", trait=trait)
        logger.info("Random host missions", missions=host_missions)
        return cls(
            topic=topic,
            trait=trait,
            host_missions=host_missions,
            llm=llm,
            media_store=media_store,
        )
