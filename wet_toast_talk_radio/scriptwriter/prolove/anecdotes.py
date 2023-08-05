import asyncio
import json
import random
from pathlib import Path

import structlog
from guidance import Program
from guidance.llms import LLM

logger = structlog.get_logger()

DATING_EXAMPLES = [
    "I cancelled a date to go to the spa.",
    "I left a tinder date because they weren't impressed by my sudoku high scores.",
    "I put up outdated photos on my dating profile.",
    "I lied about my sexual history to make myself seem more experienced.",
    "I broke up with someone because they didn't like my favorite movie.",
]

TOPIC_TEMPLATE = """{{#system~}}
You are petty, insecure, self-obsessed, and emotionally immature.
{{~/system}}
{{#user~}}
Your task is to generate lists of your most unique {{anecdote_type}} experiences.
Describe the experiences in a specific and personal way.
List the fields one per line. Don't number them or print any other text, just print a field on each line.

Here is an example:
{{#each examples~}}
{{this}}
{{/each}}

Now generate a list of {{n_anecdotes}} experiences.
{{~/user}}
{{#assistant~}}
{{gen 'list' temperature=1.3 max_tokens=1000}}
{{~/assistant}}"""


class AnecdoteGenerator:
    def __init__(  # noqa: PLR0913
            self,
        llm: LLM,
        n_anecdotes: int,
        n_iter: int,
        anecdote_type: str,
        examples: list[str],
    ):
        self._llm = llm
        self.n_anecdotes = n_anecdotes
        self.n_iter = n_iter
        self.anecdote_type = anecdote_type
        self.examples = examples
        logger.info("Initialized anecdotes", n_anecdotes=n_anecdotes, n_iter=n_iter)

    async def awrite_anecdote(self, program: Program, **kwargs) -> Program:
        """For some reason the program await is messed up so we have to wrap in this async function"""
        return await program(**kwargs)

    async def awrite(self) -> list[str]:
        logger.info("Async writing anecdotes")

        tasks = []
        for _ in range(self.n_iter):
            anecdote = Program(text=TOPIC_TEMPLATE, llm=self._llm, async_mode=True)
            tasks.append(
                asyncio.create_task(
                    self.awrite_anecdote(
                        anecdote,
                        anecdote_type=self.anecdote_type,
                        examples=self.examples,
                        n_anecdotes=self.n_anecdotes,
                    )
                )
            )
        results = await asyncio.gather(*tasks, return_exceptions=True)
        anecdotes = self.collect(results)
        anecdotes += self.examples
        unique_anecdotes = list(set(anecdotes))
        logger.info(
            f"Generated {len(unique_anecdotes)} unique anecdotes",
            anecdotes=unique_anecdotes,
        )
        return unique_anecdotes

    def collect(self, results: list[Program]) -> list[str]:
        all_anecdotes = []
        for r in results:
            if isinstance(r, Exception):
                logger.error("Error generating anecdotes", error=r)
            else:
                logger.info(r)
                anecdotes = r["list"].split("\n")
                anecdotes = [t.strip().replace("-", " ") for t in anecdotes]
                all_anecdotes.extend(anecdotes)
        return all_anecdotes


class Anecdotes:
    def __init__(
        self,
        llm: LLM,
        n_anecdotes: int,
        n_iter: int,
        tmp_dir: Path = Path("tmp/"),
    ):
        self._llm = llm
        self.n_anecdotes = n_anecdotes
        self.n_iter = n_iter
        self._generators = self.init_generators()
        self._output_dir = tmp_dir
        logger.info("Initialized anecdotes", n_anecdotes=n_anecdotes, n_iter=n_iter)

    async def awrite(self) -> bool:
        logger.info("Async writing anecdotes")
        tasks = []
        for g in self._generators:
            tasks.append(asyncio.create_task(g.awrite()))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        topics = flatten(results)
        self.save(topics)
        return True

    def init_generators(self) -> list[AnecdoteGenerator]:
        dating = AnecdoteGenerator(
            llm=self._llm,
            n_anecdotes=self.n_anecdotes,
            n_iter=self.n_iter,
            anecdote_type="dating",
            examples=DATING_EXAMPLES,
        )
        return [dating]

    def save(self, anecdotes: list[str]) -> None:
        with (self._output_dir / "prolove-anecdotes.json").open("w") as f:
            json.dump(anecdotes, f, indent=2)


def flatten(things: list) -> list:
    return [e for nested_things in things for e in nested_things]


TOPICS_PATH = Path(__file__).parent / "resources" / "prolove-anecdotes.json"
TOPICS_CACHE = None


def load_anecdotes() -> list[str]:
    global TOPICS_CACHE  # noqa: PLW0603
    if TOPICS_CACHE is None:
        with TOPICS_PATH.open() as f:
            TOPICS_CACHE = json.load(f)
    return TOPICS_CACHE


def random_anecdote() -> str:
    """Return a random anecdote from the list of anecdotes"""
    return random.choice(load_anecdotes())
