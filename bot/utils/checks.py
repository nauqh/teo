import lightbulb
from lightbulb import CheckFailure


class NotLearner(CheckFailure):
    pass


@lightbulb.Check
def valid_learner(ctx: lightbulb.Context) -> bool:
    roles = [role.name for role in ctx.member.get_roles()]

    if not any(role.startswith("Learner") for role in roles):
        raise NotLearner('Member does not have Learner role')
    return True
