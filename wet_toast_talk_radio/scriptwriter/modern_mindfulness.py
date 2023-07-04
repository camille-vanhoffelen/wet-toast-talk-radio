# ruff: noqa: E501

import structlog
from guidance import Program
from guidance.llms import LLM

from wet_toast_talk_radio.common.dialogue import Line
from wet_toast_talk_radio.common.log_ctx import show_id_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow
from wet_toast_talk_radio.scriptwriter.topics import load_topics
from wet_toast_talk_radio.scriptwriter.traits import load_traits

logger = structlog.get_logger()

TOPICS = load_topics()
TRAITS = load_traits()

PLAN_TEMPLATE = """{{#system~}}
You are an edgy, satirical writer.
{{~/system}}
{{#block hidden=True}}
{{#user~}}
Your task is to make lists of unlucky yet harmless events that could happen to a person in a given situation.
List the unlucky events one per line. Don't number them or print any other text, just print an unlucky event on each line.
Use a casual tone and informal style.

Here's an example:
Situation: 
Taking the metro to go to work.
Events:
Missing your stop.
Getting caught in the door.
Sitting next to a loud chewer.
Accidentally stepping on someone's foot.
Making eye contact with your ex.

Now generate a list of 4 unlucky yet harmless events.
Situation: 
{{situation}}.
{{~/user}}
{{#assistant~}}
{{gen 'events' temperature=0.9 max_tokens=500}}
{{~/assistant}}
{{/block}}
{{#user~}}
Your task is to write a story about the unlucky events and the stressful circumstances listed below.

Situation:
{{situation}}.
Unlucky events:
{{events}}
Circumstances:
Running late to go to yoga class for the third time this week.
Having to pee.

Now write this story in 2000 words and in the first person point of view. 
Include all events and circumstances, in a order that makes chronological sense. 
Describe each event in great detail, and focus on their most stressful and frustrating aspects. 
End with an anxious cliffhanger.
Use a casual tone and informal style. Make the story long, descriptive and relatable.
{{~/user}}
{{#assistant~}}
{{gen 'story' temperature=0.9 max_tokens=2000}}
{{~/assistant}}
{{#system~}}
You are now an enlightened spiritual guru.
{{~/system}}
{{#user~}}
Your task is to turn the above story into a guided meditation.
This is a mindfulness exercise combined with exposure therapy. 
Its purpose is for listeners to face and engage with their fears and anxieties in a safe environment.
You should include all the stressful and frustrating descriptions of the story, and narrate them in extreme detail.
You should encourage the listener to remain calm despite the challenges they encounter along the way.
Regularly remind the listener to breathe and relax. Lead them through breathing exercises with "[breathes]".
Make the meditation long, descriptive, and slow.
End your meditation with your mantra: "Life sucks, but I breathe [breathes]."
{{~/user}}
{{#assistant~}}
{{gen 'meditation' temperature=0.9 max_tokens=3000}}
{{~/assistant}}
"""


class ModernMindfulness(RadioShow):
    """Guided meditation radio show combining exposure therapy and mindfulness."""

    def __init__(
        self,
        llm: LLM,
        media_store: MediaStore,
    ):
        self._llm = llm
        self._media_store = media_store

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "ModernMindfulness":
        return cls(llm=llm, media_store=media_store)

    @show_id_log_ctx()
    async def awrite(self, show_id: ShowId) -> bool:
        logger.info(
            "Async writing modern mindfulness",
        )

        plan = Program(text=PLAN_TEMPLATE, llm=self._llm, async_mode=True)
        # situation = "taking the metro to go to work"
        # TODO generate situations
        # situation = "going to the hairdresser"
        # situation = "cooking a meal for your children"
        situation = "picking up a package from the post office"
        # situation = "going to the supermarket to buy toilet paper"
        written_plan = await plan(situation=situation)
        logger.debug("Written plan", debate=written_plan)
        logger.info("Finished writing Modern Mindfulness")
        # logger.debug("Final script", content=lines)
        # self._media_store.put_script_show(show_id=show_id, lines=lines)
        return True

    def _post_processing(self, script: str) -> list[Line]:
        logger.info("Post processing Modern Mindfulness")
        # TODO
        return script
