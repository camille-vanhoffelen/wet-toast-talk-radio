import guidance
import structlog
from guidance.llms import LLM

from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.config import LLMConfig
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow

logger = structlog.get_logger()

TEMPLATE = """{{#system~}}
You are a satyrical product marketing expert.
You are an expert in coming up with parodies of products, and marketing them in a real professional way.
{{~/system}}
{{#user~}}
Your task is to come up with names for crazy products.
Here are some examples: [Noodle Nose, Tasty Fork, Bacon-beacon, The Ultimate Crypto Chatbot]
Now come up with a new name. Only write the name of a single product in the format PRODUCT: product name.
{{~/user}}
{{#assistant~}}
{{gen 'product_name' temperature=0.9 max_tokens=10}}
{{~/assistant}}
{{#user~}}
Now describe this product {{product_name}} in great detail.
{{~/user}}
{{#assistant~}}
{{gen 'product_description' temperature=0.9 max_tokens=500}}
{{~/assistant}}"""

PREFIX = "And now for a word from our sponsors. "


class Advert(RadioShow):
    def __init__(self, llm: LLM, media_store: MediaStore):
        # TODO check that there isn't better way of doing this
        guidance.llm = llm
        self._media_store = media_store

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "Advert":
        return cls(llm=llm, media_store=media_store)

    async def awrite(self, show_id: ShowId) -> bool:
        logger.info(f"Writing advert for {show_id}")
        program = guidance(template=TEMPLATE, async_mode=True)
        executed_program = await program()
        self._post_processing(program=executed_program, show_id=show_id)
        return True

    def write(self, show_id: ShowId) -> bool:
        logger.info(f"Writing advert for {show_id}")
        program = guidance(template=TEMPLATE)
        executed_program = program()
        self._post_processing(program=executed_program, show_id=show_id)
        return True

    def _post_processing(self, program: guidance.Program, show_id: ShowId):
        # TODO parsing / validating
        logger.info(program)
        content = PREFIX + program["product_description"]
        self._media_store.put_script_show(show_id=show_id, content=content)
