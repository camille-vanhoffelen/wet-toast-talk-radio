from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)


def generate_guest_generation_template(polarity: str):
    system_template = "You are an edgy, satirical writer who writes character profiles."
    human_template = f"Think of the most stereotypical person who would argue {polarity} of the use of {{topic}}. Describe them in three sentences."
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    return ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

def generate_script_generation_template():
    system_template = "You are an edgy, satirical writer. You write dialogues in the following format:\nX: Did you eat the Doritos?\nY: No X, I didn't.\nX: I bet you did.\n"
    human_template = "Here are the descriptions of two characters: {in_favor_guest} and {against_guest}. Imagine that these two characters are discussing the pros and cons of {topic}. They are stubborn, emotional, and stuck in disagreement. The conversation is chaotic and they cut eachother off often. Now generate a dialogue for this conversation of roughly 2000 words."
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    return ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

IN_FAVOR_GUEST = generate_guest_generation_template(polarity="in favor")
AGAINST_GUEST = generate_guest_generation_template(polarity="against")

SCRIPT = generate_script_generation_template()
