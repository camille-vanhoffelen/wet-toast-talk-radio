from typing import Any

import structlog
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains import SequentialChain
from langchain.chains.base import Chain
from langchain.prompts import ChatPromptTemplate

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter import prompts
from wet_toast_talk_radio.scriptwriter.prompts import ScriptOutputParser
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow

IN_FAVOR_GUEST_KEY = "in_favor_guest"
AGAINST_GUEST_KEY = "against_guest"

logger = structlog.get_logger()


class GuestGenerationChain(Chain):
    """
    Generates two guests for "The Great Debate" show,
    based on the show's topic.
    """

    llm: BaseLanguageModel
    in_favor_prompt: ChatPromptTemplate = prompts.IN_FAVOR_GUEST
    against_prompt: ChatPromptTemplate = prompts.AGAINST_GUEST
    input_key: str = "topic"
    in_favor_guest_output_key: str = IN_FAVOR_GUEST_KEY
    against_guest_output_key: str = AGAINST_GUEST_KEY

    @property
    def input_keys(self) -> list[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> list[str]:
        return [self.in_favor_guest_output_key, self.against_guest_output_key]

    def _call(
        self,
        inputs: dict[str, Any],
        run_manager: CallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        logger.info("Starting guest generation chain")
        logger.debug("Guest generation chain inputs", inputs=inputs)

        in_favor_prompt_value = self.in_favor_prompt.format_prompt(**inputs)
        against_prompt_value = self.against_prompt.format_prompt(**inputs)

        in_favor_guest = self.llm.generate_prompt(
            prompts=[in_favor_prompt_value],
            callbacks=run_manager.get_child() if run_manager else None,
        )

        against_guest = self.llm.generate_prompt(
            prompts=[against_prompt_value],
            callbacks=run_manager.get_child() if run_manager else None,
        )

        output = {
            self.in_favor_guest_output_key: in_favor_guest.generations[0][0].text,
            self.against_guest_output_key: against_guest.generations[0][0].text,
        }

        logger.info("Finished guest generation chain")
        logger.debug("Guest generation chain output", output=output)
        return output

    async def _acall(
        self,
        inputs: dict[str, Any],
        run_manager: AsyncCallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        logger.info("Starting guest generation chain")
        logger.debug("Guest generation chain inputs", inputs=inputs)

        in_favor_prompt_value = self.in_favor_prompt.format_prompt(**inputs)
        against_prompt_value = self.against_prompt.format_prompt(**inputs)

        in_favor_guest = await self.llm.agenerate_prompt(
            [in_favor_prompt_value],
            callbacks=run_manager.get_child() if run_manager else None,
        )

        against_guest = await self.llm.agenerate_prompt(
            [against_prompt_value],
            callbacks=run_manager.get_child() if run_manager else None,
        )
        output = {
            self.in_favor_guest_output_key: in_favor_guest.generations[0][0].text,
            self.against_guest_output_key: against_guest.generations[0][0].text,
        }

        logger.info("Finished guest generation chain")
        logger.debug("Guest generation chain output", output=output)
        return output


class ScriptGenerationChain(Chain):
    """
    Generates a radio script for "The Great Debate" show,
    based on two guest descriptions and the show's topic.
    """

    llm: BaseLanguageModel
    prompt: ChatPromptTemplate = prompts.SCRIPT
    parser: ScriptOutputParser = ScriptOutputParser()
    output_key: str = "script"

    @property
    def input_keys(self) -> list[str]:
        return self.prompt.input_variables

    @property
    def output_keys(self) -> list[str]:
        return [self.output_key]

    def _call(
        self,
        inputs: dict[str, Any],
        run_manager: CallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        logger.info("Starting script generation chain")
        logger.debug("Script generation chain inputs", inputs=inputs)

        prompt_value = self.prompt.format_prompt(**inputs)

        result = self.llm.generate_prompt(
            prompts=[prompt_value],
            callbacks=run_manager.get_child() if run_manager else None,
        )
        raw_script = result.generations[0][0].text
        logger.debug("Parsing raw script", raw_script=raw_script)
        script = self.parser.parse(raw_script)

        logger.info("Finished script generation chain")
        logger.debug("Script generation chain output", script=script)
        return {self.output_key: script}

    async def _acall(
        self,
        inputs: dict[str, Any],
        run_manager: AsyncCallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        logger.info("Starting script generation chain")
        logger.debug("Script generation chain inputs", inputs=inputs)

        prompt_value = self.prompt.format_prompt(**inputs)

        result = await self.llm.agenerate_prompt(
            prompts=[prompt_value],
            callbacks=run_manager.get_child() if run_manager else None,
        )
        raw_script = result.generations[0][0].text
        logger.debug("Parsing raw script", raw_script=raw_script)
        script = self.parser.parse(raw_script)

        logger.info("Finished script generation chain")
        logger.debug("Script generation chain output", script=script)
        return {self.output_key: script}


class TheGreatDebateChain(Chain):
    """
    Generates a radio script for "The Great Debate" show for a given topic.
    Combines the guest generation and script generation chains.
    """

    chain: SequentialChain

    @property
    def input_keys(self) -> list[str]:
        return self.chain.input_keys

    @property
    def output_keys(self) -> list[str]:
        return self.chain.output_keys

    def _call(
        self,
        inputs: dict[str, Any],
        run_manager: CallbackManagerForChainRun | None = None,
    ) -> dict[str, Any]:
        return self.chain(inputs=inputs, callbacks=run_manager)

    async def _acall(
        self,
        inputs: dict[str, Any],
        run_manager: AsyncCallbackManagerForChainRun | None = None,
    ) -> dict[str, Any]:
        return await self.chain.acall(inputs=inputs, callbacks=run_manager)

    @classmethod
    def from_llm(cls, llm: BaseLanguageModel) -> "TheGreatDebateChain":
        guest_generation_chain = GuestGenerationChain(llm=llm)
        script_generation_chain = ScriptGenerationChain(llm=llm)
        chain = SequentialChain(
            chains=[guest_generation_chain, script_generation_chain],
            input_variables=guest_generation_chain.input_keys,
            output_variables=guest_generation_chain.output_keys
            + script_generation_chain.output_keys,
        )
        return cls(chain=chain)


class TheGreatDebateShow(RadioShow):
    def __init__(
        self,
        llm: BaseLanguageModel,
        media_store: MediaStore,
    ):
        self._chain = TheGreatDebateChain.from_llm(llm=llm)
        # TODO modularize topic
        self.topic = "toilet paper"
        self._media_store = media_store

    async def awrite(self, show_i: int, show_iso_utc_date: str):
        logger.info("Writing The Great Debate show...", topic=self.topic)
        outputs = await self._chain.acall(inputs={"topic": self.topic})
        script = outputs["script"]
        logger.info("Finished writing The Great Debate show", script=script)

        show_id = ShowId(show_i=show_i, date=show_iso_utc_date)
        self._media_store.put_script_show(show_id=show_id, content=script)

    @classmethod
    def create(
        cls,
        llm: BaseLanguageModel,
        media_store: MediaStore,
    ) -> "TheGreatDebateShow":
        return cls(
            llm=llm,
            media_store=media_store,
        )
