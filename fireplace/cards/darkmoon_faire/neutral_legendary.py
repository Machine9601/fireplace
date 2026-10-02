from ..utils import *

##
# Minions


class DMF_074:
    """Silas Darkmoon"""

    # <b>Battlecry:</b> Choose a direction to rotate all minions.
    play = Choice(CONTROLLER, ["DMF_074a", "DMF_074b"]).then(
        Battlecry(Choice.CARD, None)
    )


def _silas_rotate(source, friendly_side, enemy_side):
    """
    Silas Darkmoon (WP-195): the outermost minions change sides at once, so a
    full board never destroys one (Steal would, one move at a time). A dormant
    minion is passed over (the wiki). The minion changes control as when taken:
    it cannot attack this turn without Rush or Charge.
    friendly_side, enemy_side: "left" or "right", the end each one leaves.
    """
    player = source.controller
    opponent = player.opponent

    def outermost(field, side):
        minions = [m for m in field if not m.dormant]
        if not minions:
            return None
        return minions[0] if side == "left" else minions[-1]

    mine = outermost(player.field, friendly_side)
    theirs = outermost(opponent.field, enemy_side)
    moving = [m for m in (mine, theirs) if m is not None]
    for minion in moving:
        minion.zone = Zone.SETASIDE
    # Your minions move left (this way): yours goes to the far left of the
    # opponent's board, theirs to the far right of yours; and the reverse.
    for minion, controller, side in (
        (mine, opponent, friendly_side),
        (theirs, player, enemy_side),
    ):
        if minion is None:
            continue
        minion.controller = controller
        minion.turns_in_play = 0
        minion._summon_index = 0 if side == "left" else len(controller.field)
        minion.zone = Zone.PLAY
        minion._summon_index = None
        # Told to the observers as a change of control (the same as Steal).
        source.game.manager.targeted_action(
            Steal(minion, controller), source, minion, controller
        )
    return ()


class DMF_074a:
    """This Way"""

    # "This Way" rotates clockwise: your minions move left, your opponent's
    # minions move right. (Absent until WP-195: the choice did nothing.)
    def play(self):
        return _silas_rotate(self, "left", "right")


class DMF_074b:
    """That Way"""

    # "That Way" rotates counter-clockwise: your minions move right, your
    # opponent's minions move left. (WP-195: inserted at -1, the right-most
    # landed second from the end.)
    def play(self):
        return _silas_rotate(self, "right", "left")


class DMF_002:
    """N'Zoth, God of the Deep"""

    # <b>Battlecry:</b> Resurrect a friendly minion of each minion type.
    play = Summon(CONTROLLER, UniqueRace(FRIENDLY + KILLED + MINION))


class DMF_004(metaclass=ThresholdUtils):
    """Yogg-Saron, Master of Fate"""

    # [x]<b>Battlecry:</b> If you've cast 10 spells this game, spin the Wheel
    # of Yogg-Saron.@ <i>({0} left!)</i>@ <i>(Ready!)</i>
    entourage = [
        "DMF_004t1",
        "DMF_004t2",
        "DMF_004t3",
        "DMF_004t4",
        "DMF_004t5",
        "DMF_004t6",
    ]
    play = Battlecry(RandomEntourage(), None)


class DMF_004t1:
    """Mysterybox"""

    # Cast a random spell for every spell you've cast this game <i>(targets
    # chosen randomly)</i>.
    play = CastSpell(RandomSpell()) * TIMES_SPELL_PLAYED_THIS_GAME


class DMF_004t2:
    """Hand of Fate"""

    # Fill your hand with random spells. They cost (0) this turn.
    play = Give(CONTROLLER, RandomSpell()).then(Buff(Give.CARD, "DMF_004t1e")) * (
        MAX_HAND_SIZE(CONTROLLER) - Count(FRIENDLY_HAND)
    )


class DMF_004t1e:
    cost = SET(0)
    events = REMOVED_IN_PLAY


class DMF_004t3:
    """Curse of Flesh"""

    # Fill the board with random minions, then give yours <b>Rush</b>.
    # The board is both sides: the opponent's is filled too, without Rush
    # (WP-195: only the caster's was).
    play = (
        Summon(CONTROLLER, RandomMinion()).then(GiveRush(Summon.CARD))
        * MINION_SLOTS(CONTROLLER),
        Summon(OPPONENT, RandomMinion()) * MINION_SLOTS(OPPONENT),
    )


class DMF_004t4:
    """Mindflayer Goggles"""

    # Take control of three random enemy minions.
    play = Steal(RANDOM_ENEMY_MINION * 3)


class DMF_004t5:
    """Devouring Hunger"""

    # Destroy all other minions. Gain their Attack and Health.
    play = (
        Buff(
            SELF,
            "DMF_004t5e",
            atk=ATK(ALL_MINIONS - SELF),
            max_health=CURRENT_HEALTH(ALL_MINIONS - SELF),
        ),
        Destroy(ALL_MINIONS - SELF),
    )


class DMF_004t6:
    """Rod of Roasting"""

    # Cast 'Pyroblast' randomly until a hero dies.
    def play(self):
        hero1 = self.controller.hero
        hero2 = self.controller.opponent.hero
        while not hero1.dead and not hero2.dead:
            yield CastSpell("EX1_279")


class DMF_188:
    """Y'Shaarj, the Defiler"""

    # [x]<b>Battlecry:</b> Add a copy of each <b>Corrupted</b> card you've
    # played this game to your hand. They cost (0) this turn.
    play = Give(
        CONTROLLER, SHUFFLE(FRIENDLY + CARDS_PLAYED_THIS_GAME + CORRUPTED_CARD)
    ).then(Buff(Give.CARD, "DMF_188e"))


class DMF_188e:
    # "They cost (0) this turn" (WP-195: the data has no one-turn tag, and
    # the copies stayed at 0).
    tags = {GameTag.TAG_ONE_TURN_EFFECT: True}
    cost = SET(0)
    events = REMOVED_IN_PLAY


class DMF_254:
    """C'Thun, the Shattered"""

    # [x]<b>Start of Game:</b> Break into pieces. <b>Battlecry:</b> Deal 30
    # damage randomly split among all enemies.
    class Deck:
        events = GameStart().on(
            Remove(SELF),
            Shuffle(CONTROLLER, ["DMF_254t3", "DMF_254t4", "DMF_254t5", "DMF_254t7"]),
        )

    progress_total = 4
    reward = Shuffle(CONTROLLER, SELF)
    play = Hit(RANDOM_ENEMY_CHARACTER, 1) * 30

    def clear_progress(self):
        self.cthun_pieces = set()

    def progress(self):
        if not hasattr(self, "cthun_pieces"):
            self.cthun_pieces = set()
        return len(self.cthun_pieces)

    def add_progress(self, card):
        if not hasattr(self, "cthun_pieces"):
            self.cthun_pieces = set()
        self.cthun_pieces.add(card)


class DMF_254t3:
    """Eye of C'Thun"""

    # [x]<b>Piece_of_C'Thun_(@/4)</b> Deal $7 damage randomly split among all
    # enemies.
    play = (
        Hit(RANDOM_ENEMY_CHARACTER, 1) * 7,
        AddProgress(CREATOR, SELF),
    )


class DMF_254t4:
    """Heart of C'Thun"""

    # <b>Piece of C'Thun (@/4)</b> Deal $3 damage to all minions.
    play = (
        Hit(ALL_MINIONS, 3),
        AddProgress(CREATOR, SELF),
    )


class DMF_254t5:
    """Body of C'Thun"""

    # [x]<b>Piece of C'Thun (@/4)</b> Summon a 6/6 C'Thun's Body with
    # <b>Taunt</b>.
    play = (
        Summon(CONTROLLER, "DMF_254t5t"),
        AddProgress(CREATOR, SELF),
    )


class DMF_254t7:
    """Maw of C'Thun"""

    # <b>Piece of C'Thun (@/4)</b> Destroy a minion.
    requirements = {PlayReq.REQ_MINION_TARGET: 0, PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = (
        Destroy(TARGET),
        AddProgress(CREATOR, SELF),
    )


class YOP_035:
    """Moonfang"""

    # Can only take 1 damage at_a time.
    update = Refresh(SELF, {GameTag.HEAVILY_ARMORED: True})
