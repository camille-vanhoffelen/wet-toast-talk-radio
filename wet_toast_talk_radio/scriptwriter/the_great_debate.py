from typing import Any, Dict, List

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.prompts import ChatPromptTemplate
from pydantic import Extra

from wet_toast_talk_radio.scriptwriter import prompts

IN_FAVOR_GUEST_KEY = "in_favor_guest"
AGAINST_GUEST_KEY = "against_guest"


class FakeChain(Chain):
    chain_1: LLMChain
    chain_2: LLMChain

    @property
    def input_keys(self) -> List[str]:
        # Union of the input keys of the two chains.
        all_input_vars = set(self.chain_1.input_keys).union(set(self.chain_2.input_keys))
        return list(all_input_vars)

    @property
    def output_keys(self) -> List[str]:
        return ["concat_output"]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        output_1 = self.chain_1.run(inputs)
        output_2 = self.chain_2.run(inputs)
        return {"concat_output": output_1 + output_2}


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

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> list[str]:
        """Will be whatever keys the prompt expects.

        """
        return [self.input_key]

    @property
    def output_keys(self) -> list[str]:
        """Will always return text key.

        """
        return [self.in_favor_guest_output_key, self.against_guest_output_key]

    def _call(
            self,
            inputs: dict[str, Any],
            run_manager: CallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        in_favor_prompt_value = self.in_favor_prompt.format_prompt(**inputs)
        against_prompt_value = self.against_prompt.format_prompt(**inputs)

        in_favor_guest = self.llm.generate_prompt(
            [in_favor_prompt_value],
            callbacks=run_manager.get_child() if run_manager else None
        )

        against_guest = self.llm.generate_prompt(
            [against_prompt_value],
            callbacks=run_manager.get_child() if run_manager else None
        )

        # TODO remove

        return {self.in_favor_guest_output_key: in_favor_guest.generations[0][0].text,
                self.against_guest_output_key: against_guest.generations[0][0].text}

    async def _acall(
            self,
            inputs: dict[str, Any],
            run_manager: AsyncCallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        in_favor_prompt_value = self.in_favor_prompt.format_prompt(**inputs)
        against_prompt_value = self.against_prompt.format_prompt(**inputs)

        in_favor_guest = await self.llm.agenerate_prompt(
            [in_favor_prompt_value],
            callbacks=run_manager.get_child() if run_manager else None
        )

        against_guest = await self.llm.agenerate_prompt(
            [against_prompt_value],
            callbacks=run_manager.get_child() if run_manager else None
        )
        return {self.in_favor_guest_output_key: in_favor_guest.generations[0][0].text,
                self.against_guest_output_key: against_guest.generations[0][0].text}

    @property
    def _chain_type(self) -> str:
        return "guest_generation_chain"

class ScriptGenerationChain(Chain):
    llm: BaseLanguageModel
    prompt: ChatPromptTemplate = prompts.SCRIPT
    output_key: str = "script"

    @property
    def input_keys(self) -> List[str]:
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(
            self,
            inputs: dict[str, Any],
            run_manager: CallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        prompt_value = self.prompt.format_prompt(**inputs)

        script = self.llm.generate_prompt(
            [prompt_value],
            callbacks=run_manager.get_child() if run_manager else None
        )
        return {self.output_key: script.generations[0][0].text}

    async def _acall(
            self,
            inputs: dict[str, Any],
            run_manager: AsyncCallbackManagerForChainRun | None = None,
    ) -> dict[str, str]:
        prompt_value = self.prompt.format_prompt(**inputs)

        script = await self.llm.agenerate_prompt(
            [prompt_value],
            callbacks=run_manager.get_child() if run_manager else None
        )
        return {self.output_key: script.generations[0][0].text}

class TheGreatDialogueChain(Chain):
    # TODO implement SequentialChain of the above
    pass

