import asyncio
import json
import random
from pathlib import Path

import structlog
from guidance import Program
from guidance.llms import LLM

logger = structlog.get_logger()

# TODO business owner
PRODUCT_TEMPLATE = """{{#system~}}
You a creative product designer.
{{~/system}}
{{#user~}}
Your task is to generate lists of commercial products.
{{product_description}}
List the products one per line. Don't number them or print any other text, just print a product on each line.

Here is an example:
{{#each examples~}}
{{this}}
{{/each}}
Now generate a list of {{n_products}} products.
{{~/user}}
{{#assistant~}}
{{gen 'list' temperature=1.3 max_tokens=1000}}
{{~/assistant}}"""

FAKE_EXAMPLES = [
    "Nanoeconomics",
    "Oval Universe Theory",
    "Metabiology",
    "Geometric Theology",
]
FAKE_DESCRIPTION = "The academic fields should sound like real academic research fields, but be completely fake."

# TODO superlatives
SUPERLATIVE_EXAMPLES = [
    "The thinnest phone on the Planet",
    "The most comfortable shoes ever",
    "The friendliest accountant in the country",
    "The most caffeinated soda in the world",
]
SUPERLATIVE_DESCRIPTION = "The products should be superlatives. This defines their unique selling point."

# TODO as a service

ABSURD_EXAMPLES = [
    "Time Travel Philosophy",
    "Plant Linguistics",
    "Cooties Virology",
    "Perpetual Motion Physics",
]
ABSURD_DESCRIPTION = (
    "The academic fields should be studies of things that are impossible and absurd."
)

MODERN_EXAMPLES = [
    "Tiktok Dance Studies",
    "Selfie Engineering",
    "Meme Anthropology",
    "Fast Fashion Economics",
]
MODERN_DESCRIPTION = (
    "The academic fields should be studies of modern phenomena that define millennial and gen-z culture. "
    "The fields should sound like real academic research fields."
)

MUNDANE_EXAMPLES = [
    "Lemonade Stand Economics",
    "Tea Infusion Chemistry",
    "History of Flatulence",
    "Dust Dynamics",
    "Yawn Physiology",
    "Handshake Mechanics",
    "Potato Aerodynamics",
]
MUNDANE_DESCRIPTION = (
    "The academic fields should be studies of common objects or mundane occurrences "
    "that people experience in their everyday lives. "
    "These should not be traditionally associated with serious research."
)


class ProductGenerator:
    def __init__(  # noqa: PLR0913
        self,
        llm: LLM,
        n_products: int,
        n_iter: int,
        examples: list[str],
        product_description: str,
    ):
        self._llm = llm
        self.n_products = n_products
        self.n_iter = n_iter
        self.examples = examples
        self.product_description = product_description
        logger.info("Initialized products", n_products=n_products, n_iter=n_iter)

    async def awrite_product(self, program: Program, **kwargs) -> Program:
        """For some reason the program await is messed up so we have to wrap in this async function"""
        return await program(**kwargs)

    async def awrite(self) -> list[str]:
        logger.info("Async writing products")

        tasks = []
        for _ in range(self.n_iter):
            product = Program(text=PRODUCT_TEMPLATE, llm=self._llm, async_mode=True)
            tasks.append(
                asyncio.create_task(
                    self.awrite_product(
                        product,
                        examples=self.examples,
                        n_products=self.n_products,
                        product_description=self.product_description,
                    )
                )
            )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        products = self.collect(results)
        products += self.examples
        unique_products = list(set(products))
        logger.info(
            f"Generated {len(unique_products)} unique products", products=unique_products
        )
        return unique_products

    def collect(self, results: list[Program]) -> list[str]:
        all_products = []
        for r in results:
            if isinstance(r, Exception):
                logger.error("Error generating products", error=r)
            else:
                logger.info(r)
                products = r["list"].split("\n")
                products = [t.strip().replace("-", " ") for t in products]
                all_products.extend(products)
        return all_products


class Products:
    def __init__(
        self,
        llm: LLM,
        n_products: int,
        n_iter: int,
        tmp_dir: Path = Path("tmp/"),
    ):
        self._llm = llm
        self.n_products = n_products
        self.n_iter = n_iter
        self._generators = self.init_generators()
        self._output_dir = tmp_dir
        logger.info("Initialized products", n_products=n_products, n_iter=n_iter)

    async def awrite(self) -> bool:
        logger.info("Async writing products")
        tasks = []
        for g in self._generators:
            tasks.append(asyncio.create_task(g.awrite()))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        products = flatten(results)
        self.save(products)
        return True

    def init_generators(self) -> list[ProductGenerator]:
        superlative = ProductGenerator(
            llm=self._llm,
            n_products=self.n_products,
            n_iter=self.n_iter,
            examples=SUPERLATIVE_EXAMPLES ,
            product_description=SUPERLATIVE_DESCRIPTION,
        )
        return [superlative]

    def save(self, products: list[str]) -> None:
        with (self._output_dir / "advert-products.json").open("w") as f:
            json.dump(products, f, indent=2)


def flatten(things: list) -> list:
    return [e for nested_things in things for e in nested_things]


PRODUCTS_PATH = Path(__file__).parent / "resources" / "advert-products.json"
PRODUCTS_CACHE = None


def load_products() -> list[str]:
    global PRODUCTS_CACHE  # noqa: PLW0603
    if PRODUCTS_CACHE is None:
        with PRODUCTS_PATH.open() as f:
            PRODUCTS_CACHE = json.load(f)
    return PRODUCTS_CACHE


def random_product() -> str:
    """Return a random product from the list of products"""
    return random.choice(load_products())
