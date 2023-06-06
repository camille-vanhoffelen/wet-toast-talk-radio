from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import BaseOutputParser


def generate_guest_generation_template(polarity: str):
    system_template = "You are an edgy, satirical writer who writes character profiles."
    human_template = (
        f"Think of the most stereotypical person who would argue {polarity} of the use of {{topic}}. "
        "Describe them in three sentences."
    )
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    return ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )


def generate_script_generation_template():
    system_template = "You are an edgy, satirical writer. {format_instructions}"
    human_template = (
        "Here are the descriptions of two characters: {in_favor_guest} and {against_guest}. "
        "Imagine that these two characters are discussing the pros and cons of {topic}. "
        "They are stubborn, emotional, and stuck in disagreement. The conversation is chaotic. "
        "They cut eachother off often, and still disagree at the end. "
        "Now generate a dialogue for this conversation of roughly 1000 words."
    )
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    return ChatPromptTemplate(
        messages=[system_message_prompt, human_message_prompt],
        input_variables=["in_favor_guest", "against_guest"],
        partial_variables={
            "format_instructions": ScriptOutputParser().get_format_instructions()
        },
    )


class ScriptOutputParser(BaseOutputParser):
    """Class to parse the output of an LLM call to a script."""

    n_speakers = 2

    @property
    def _type(self) -> str:
        return "str"

    def get_format_instructions(self) -> str:
        return (
            "Your response should be a dialogue in the following format:\n\n"
            "X: Hi, how are you?\n\n"
            "Y: I'm good, thanks. And you?\n\n"
            "X: I'm pretty good.\n\n"
        )

    def parse(self, script: str) -> str:
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


IN_FAVOR_GUEST = generate_guest_generation_template(polarity="in favor")
AGAINST_GUEST = generate_guest_generation_template(polarity="against")
SCRIPT = generate_script_generation_template()
