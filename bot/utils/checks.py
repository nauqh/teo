import lightbulb
from lightbulb import CheckFailure


class NotLearner(CheckFailure):
    pass


@lightbulb.Check
def valid_learner(ctx: lightbulb.Context) -> bool:
    roles = [role.name for role in ctx.member.get_roles()]

    if "Learner" not in roles:
        raise NotLearner('Member does not have <@&1196090085263814826> role')
    return True
