import random


class HostMissions:
    # Part 1

    INTRO = (
        "You tell the listeners that today, love is in the air. "
        "You then describe in great detail how you feel. "
        "You refer to listeners as 'my hearts'. "
        "You answer in four sentences or less."
    )

    CALL = (
        "You ask the listeners what has been going on in their love life. "
        "Then, you ask the listeners to call in and share their stories or questions. "
        "You refer to listeners as 'my hearts'. "
        "You ask in six sentences or less."
    )

    STORY = (
        "Tell the following personal story about a date: "
        '"Last week, {{anecdote}}" '
        "You think the date was weird but kinda cute. "
        "Describe the events in chronological order and in great visual detail. "
        "The story should be 15 sentences long. "
        "After the story, ask the listeners to tell you what they think by calling the show. "
    )

    # Part 2

    WHY = (
        "You ask {{guest_name}} why they called the show. "
        "You ask in two sentences or less."
    )

    ADVICE = (
        "You give unconventional and terrible dating advice to {{guest_name}}. "
        "You don't realise that your advice is awful. "
        "You answer in 6 sentences or less."
    )

    MORE_ADVICE = (
        "You double-down on the terrible dating advice you gave to {{guest_name}}. "
        "You describe it more detail. "
        "You still don't realise that your advice is awful. "
        "You answer in 6 sentences or less."
    )

    # Part 3

    METAPHOR = (
        "Change the topic of your conversation with {{guest_name}} by making a stupid irrelevant metaphor about love. "
        "You don't realise that your metaphor is stupid. "
        "Do it in 8 sentences or less."
    )

    LESSON = (
        "Change the topic of your conversation with {{guest_name}} by giving them an "
        "unconventional and terrible lesson about {{lesson}} in love. "
        "You don't realise that your advice is awful. "
        "Do it in 8 sentences or less."
    )

    PROMOTION = (
        "Change the topic of your conversation with {{guest_name}} "
        "by talking about your new {{product}} about dating and love. "
        "You describe its contents and why it's special. "
        "Do it in 8 sentences or less."
    )

    FAKE_FACT = (
        "Change the topic of your conversation with {{guest_name}} "
        "by making up a plausible yet farfetched statistic about dating. "
        "Do not reveal that the stat is made up. "
        "Infer some kind of lesson from the stat. "
        "Do it in 8 sentences or less."
    )

    HIJACK = (
        "Change the topic of your conversation with {{guest_name}} "
        "by hijacking the conversation and making it about yourself. "
        "Do it in 8 sentences or less."
    )

    def __init__(
        self, anecdote: str, k: int, lesson: str, product: str, guest_name: str
    ):
        self.anecdote = anecdote
        self.k = k
        self.lesson = lesson
        self.product = product
        self.guest_name = guest_name

    @property
    def pt1_missions(self) -> list[str]:
        """Return ordered missions for the host.
        Used at the start of the show."""
        return [
            self.INTRO,
            self.CALL,
            self.STORY.replace("{{anecdote}}", self.anecdote),
        ]

    @property
    def pt2_missions(self) -> list[str]:
        """Return ordered missions for the host.
        Used in the "advice" part of the show."""
        # None when should use fixed message instead of LLM generation
        return [
            None,
            self.WHY.replace("{{guest_name}}", self.guest_name),
            None,
            self.ADVICE.replace("{{guest_name}}", self.guest_name),
            self.MORE_ADVICE.replace("{{guest_name}}", self.guest_name),
        ]

    @property
    def pt3_missions(self) -> list[str]:
        """Randomly sample k missions for the host.
        Used in the "questions" part of the show.
        Sampling without replacement to avoid repetition.
        """
        missions = [
            self.METAPHOR,
            self.LESSON.replace("{{lesson}}", self.lesson),
            self.PROMOTION.replace("{{product}}", self.product),
            self.FAKE_FACT,
            self.HIJACK,
        ]
        missions = [m.replace("{{guest_name}}", self.guest_name) for m in missions]
        return random.sample(population=missions, k=self.k)


class GuestMissions:
    INTRODUCTION = (
        "You introduce yourself to the host, Zara. "
        "You mention your age, gender, and sexual orientation."
        "You answer in three sentences or less."
    )

    CONCERN = (
        'You ask the host, Zara, about your concern: "{{topic}}". '
        "You ask in four sentences or less."
    )

    DETAILS = (
        "You describe your concern in great detail. "
        "You describe specific events and emotions. "
        "You answer in 8 sentences or less."
    )

    CLARIFICATION = (
        "You compliment the good advice, but you ask for clarification on a specific point. "
        "You ask in four sentences or less."
    )

    TRY_BEST = (
        "You thank Zara for her perspective. "
        "You mention that you'll try your best. "
        "You answer in four sentences or less."
    )

    REACT_1 = "Ah, yes, thanks Zara, that sounds great."
    REACT_2 = "Cheers Zara, I'll think about that."
    REACT_3 = "Yeah... Sure, Zara."
    REACT_4 = "Totally, Zara. Thanks."
    REACT_5 = "Ya, thanks Zara. Can I leave now?"
    REACT_6 = "Amazing, thanks Zara."
    REACT_7 = "Thanks Zara, I'll try that."
    REACT_8 = "Wow... I'm so glad I called. Thanks."
    REACT_9 = "That's ... cool, I guess. Thanks."
    REACT_10 = "Interesting... Sounds cool Zara, thanks."
    REACT_11 = "Uh... Yeah? Thanks Zara."

    def __init__(self, topic: str, k: int):
        self.topic = topic
        self.k = k

    @property
    def pt2_missions(self) -> list[str]:
        """Return ordered missions for the guest.
        Used in part 2 of the show."""
        return [
            self.INTRODUCTION,
            self.CONCERN.replace("{{topic}}", self.topic),
            self.DETAILS,
            self.CLARIFICATION,
            self.TRY_BEST,
        ]

    @property
    def pt3_messages(self) -> list[str]:
        """Return ordered missions for the guest.
        Used in part 3 of the show."""
        reactions = [
            self.REACT_1,
            self.REACT_2,
            self.REACT_3,
            self.REACT_4,
            self.REACT_5,
            self.REACT_6,
            self.REACT_7,
            self.REACT_8,
            self.REACT_9,
            self.REACT_10,
            self.REACT_11,
        ]
        return random.sample(reactions, k=self.k)
