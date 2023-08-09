from dataclasses import dataclass

import structlog
from guidance import Program
from guidance.llms import LLM

from wet_toast_talk_radio.common.dialogue import Line, Speaker
from wet_toast_talk_radio.common.log_ctx import show_id_log_ctx
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId, ShowMetadata, ShowName
from wet_toast_talk_radio.scriptwriter.adverts.strategies import random_strategies
from wet_toast_talk_radio.scriptwriter.radio_show import RadioShow

logger = structlog.get_logger()

# TODO how to add randomness to the writing? styles? how to make sure it don't sound the same every time?
# TODO how to get more per step? 5 sentences?
STRATEGY_TEMPLATE = """{{#system~}}
You are {{polarity}} at product marketing.
You write in a casual and informal manner.
{{~/system}}
{{#user~}}
Your task is write the text for a {{polarity}} endorsement ad. The product is as follows:

Product name: {{product.name}}
Product description: {{product.description}}
Company name: {{product.company}}

Here is the advertising strategy you must follow. 

1. Make a catchy introduction
{{#each strategies~}}
{{@index + 2}}. {{this}}
{{/each}}

Start each step with "Host: " followed by the ad text.
For each step, write 5 sentences. Be detailed and specific.
You cannot include sound effects, soundbites or music. 
{{~/user}}
{{#assistant~}}
{{gen 'advert' temperature=0.9 max_tokens=800}}
{{~/assistant}}"""

PREFIX = "And now for a word from our sponsors. "


@dataclass
class Product:
    name: str
    description: str
    company: str


class Advert(RadioShow):
    """A radio show where the host reads out an advert for an absurd product."""

    def __init__(
        self,
        polarity: str,
        product: Product,
        strategies: list[str],
        llm: LLM,
        media_store: MediaStore,
    ):
        self._llm = llm
        self._media_store = media_store
        self.product = product
        self.polarity = polarity
        self.strategies = strategies

    @classmethod
    def create(cls, llm: LLM, media_store: MediaStore) -> "Advert":
        product = Product(
            name="Better Laughing",
            description="A course that teaches you how to laugh.",
            company="Life Coaching Inc.",
        )
        strategies = random_strategies(k_part_1=4, k_part_2=3)
        logger.info("Random strategies", strategies=strategies)
        return cls(
            polarity="good",
            product=product,
            strategies=strategies,
            llm=llm,
            media_store=media_store,
        )

    @show_id_log_ctx()
    async def awrite(self, show_id: ShowId) -> bool:
        logger.info("Async writing advert")
        program = Program(text=STRATEGY_TEMPLATE, llm=self._llm, async_mode=True)
        executed_program = await program(
            polarity=self.polarity, product=self.product, strategies=self.strategies
        )
        self._post_processing(program=executed_program, show_id=show_id)
        return True

    def _post_processing(self, program: Program, show_id: ShowId):
        logger.info(program)
        product_description = program["product_description"]
        product_description = " ".join(product_description.split())
        content = PREFIX + product_description
        line = Line(
            speaker=Speaker(name="Ian", gender="male", host=True), content=content
        )
        self._media_store.put_script_show(show_id=show_id, lines=[line])
        self._media_store.put_script_show_metadata(
            show_id=show_id, metadata=ShowMetadata(ShowName.ADVERTS)
        )
