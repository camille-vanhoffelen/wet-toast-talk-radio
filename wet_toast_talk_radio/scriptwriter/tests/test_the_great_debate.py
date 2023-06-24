import pytest
from langchain.llms.fake import FakeListLLM

from wet_toast_talk_radio.media_store import VirtualMediaStore
from wet_toast_talk_radio.scriptwriter.prompts import generate_guest_generation_template
from wet_toast_talk_radio.scriptwriter.the_great_debate import (
    TheGreatDebateChain,
    TheGreatDebateShow,
)


def test_guest_generation_prompt_template():
    prompt_template = generate_guest_generation_template(polarity="in_favor")
    prompt = prompt_template.format(topic="toilet paper")
    assert isinstance(prompt, str)
    messages = prompt_template.format_prompt(topic="toilet paper").to_messages()
    expected_messages = 2
    assert len(messages) == expected_messages


def test_the_great_debate_chain(fake_llm, topic):
    chain = TheGreatDebateChain.from_llm(llm=fake_llm)
    outputs = chain(inputs={"topic": topic})
    script = outputs["script"]
    assert script.startswith("Alice:")


def test_broken_the_great_debate_chain(broken_fake_llm, topic):
    chain = TheGreatDebateChain.from_llm(llm=broken_fake_llm)
    with pytest.raises(AssertionError):
        chain(inputs={"topic": topic})


def test_topic_cycling(fake_llm):
    show1 = TheGreatDebateShow.create(fake_llm, VirtualMediaStore())
    show2 = TheGreatDebateShow.create(fake_llm, VirtualMediaStore())
    assert show1.topic != show2.topic


@pytest.fixture()
def topic() -> str:
    return "toilet paper"


@pytest.fixture()
def script(topic: str) -> str:
    return f"Alice: I love {topic}.\n\nBob: I hate {topic}.\n\nAlice: Let's agree to disagree."


@pytest.fixture()
def bad_script() -> str:
    return "This isn't a script at all!"


@pytest.fixture()
def fake_llm(topic: str, script: str) -> FakeListLLM:
    in_favor_guest = f"Meet Alice. Alice loves {topic}."
    against_guest = f"Meet Bob. Bob hates {topic}."
    return FakeListLLM(responses=[in_favor_guest, against_guest, script])


@pytest.fixture()
def broken_fake_llm(topic: str, bad_script: str) -> FakeListLLM:
    in_favor_guest = f"Meet Alice. Alice loves {topic}."
    against_guest = f"Meet Bob. Bob hates {topic}."
    return FakeListLLM(responses=[in_favor_guest, against_guest, bad_script])
