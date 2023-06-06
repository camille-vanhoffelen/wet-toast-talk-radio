from wet_toast_talk_radio.scriptwriter.prompts import generate_guest_generation_template

def test_guest_generation_prompt_template():
    prompt_template = generate_guest_generation_template()
    prompt = prompt_template.format(topic="toilet paper")
    assert isinstance(prompt, str)
    messages = prompt_template.format_prompt(topic="toilet paper").to_messages()
    assert len(messages) == 2