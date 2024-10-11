import lightbulb
from lightbulb import CheckFailure


class NotLearner(CheckFailure):
    pass


class NotTA(CheckFailure):
    pass


@lightbulb.Check
def valid_learner(ctx: lightbulb.Context) -> bool:
    roles = [role.name for role in ctx.member.get_roles()]

    if not any(role.startswith("Learner") for role in roles):
        raise NotLearner('Member does not have Learner role')
    return True


@lightbulb.Check
def is_TA(ctx: lightbulb.Context) -> bool:
    roles = [role.name for role in ctx.member.get_roles()]

    if not any(role.startswith("TA") for role in roles):
        raise NotTA('Member does not have TA role')
    return True
