import requests
from pydantic import BaseModel, Field
import instructor
import hikari
import lightbulb
from openai import OpenAI
import re


plugin = lightbulb.Plugin("Q&A", "📝 Q&A Automation")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(plugin)


class QuestionReply(BaseModel):
    response: str = Field(
        description="The response to the question provided, in Vietnamese. Keep it less than 200 words."
    )


class ChatBot:
    def __init__(self):
        self.client = instructor.from_openai(OpenAI())
        self.contexts = {}
        self.response_count = {}
        self.github_token = "GITHUB_TOKEN"

    def fetch_all_code_from_repo(self, owner: str, repo: str, path: str = "") -> str:
        """
        Fetches all code files from a specified GitHub repository path.
        If path is empty, starts from the repository's root.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {
            "Accept": "application/vnd.github+json",
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        contents = response.json()
        all_code = ""

        for item in contents:
            if item['type'] == 'file' and item['name'].endswith(('.py', '.js', '.jsx', 'tsx', 'ts', '.html', '.css')):
                file_response = requests.get(item['download_url'])
                file_response.raise_for_status()
                all_code += f"\n\n# File: {item['path']}\n" + \
                    file_response.text
            elif item['type'] == 'dir':
                all_code += self.fetch_all_code_from_repo(
                    owner, repo, item['path'])

        return all_code

    def extract_github_repo_info(self, question: str):
        """Extracts GitHub repository owner and repo name from a question if present."""
        pattern = r"https?://github\.com/([^/]+)/([^/\s]+)"
        match = re.search(pattern, question)

        if match:
            owner = match.group(1)
            repo = match.group(2)
            return owner, repo
        return None, None

    def ask_with_context(self, thread_id, image_urls, question, owner=None, repo=None, path="") -> str:
        content = """
You are a teaching assistant for the Data Science course. You respond to questions in Vietnamese in a concise and friendly manner. Each response should be under 200 words.

Your primary tasks are to:
  - Provide clear, accurate answers to the learner's question.
  - Extract and analyze relevant code from GitHub if a repository link is included in the question.
  - Keep responses short, engaging, and easy to understand.

<TASKS>
  - If a question contains a GitHub link, extract the owner and repository name.
  - Fetch code from the repository to assist in answering if required.
  - Use friendly, conversational language in all responses.
  - If additional questions arise or a thread reaches four replies, suggest that the learner wait for further assistance from another TA.
</TASKS>

<CONTEXT>
  - Reply to each question thread in context, building on previous responses if necessary.
  - Manage follow-up questions within the same thread to ensure continuity.
  - If a learner's question falls outside of your tasks (e.g. Ask to unlock a new module, Ask to mark exams), politely inform the learner to ask the TA role
</CONTEXT>

<TOOLS>
  - fetch_all_code_from_repo: Pulls code files from a GitHub repository for context.
  - ask_with_context: Responds to questions, integrating code context if available.
  - response_count: Tracks the number of replies in a thread to manage response frequency.
</TOOLS>
"""
        if not owner or not repo:
            owner, repo = self.extract_github_repo_info(question)

        code_content = None
        if owner and repo:
            try:
                code_content = self.fetch_all_code_from_repo(owner, repo, path)
            except Exception as e:
                print(f"Error fetching code from GitHub: {e}")

        messages = self.contexts.setdefault(
            thread_id, [{"role": "system", "content": content}]
        )

        user_message = {"role": "user", "content": question}
        if image_urls:
            user_message["images"] = image_urls
        if code_content:
            user_message["content"] += f"\n\nCode:\n{code_content}"

        messages.append(user_message)

        reply = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_model=QuestionReply,
        )

        messages.append({"role": "assistant", "content": reply.response})

        self.contexts[thread_id] = messages
        self.response_count[thread_id] = self.response_count.get(
            thread_id, 0) + 1

        return reply.response


@plugin.listener(hikari.StartingEvent)
async def on_starting(event: hikari.StartingEvent) -> None:
    plugin.app.d.bot = ChatBot()


@plugin.listener(hikari.GuildThreadCreateEvent)
async def on_thread_create(event: hikari.GuildThreadCreateEvent) -> None:
    """Handles the creation of a new thread in the question center and responds to the first message."""
    thread: hikari.GuildThreadChannel = await event.fetch_channel()

    if thread.parent_id == 1301822138319114302:
        messages = await thread.fetch_history()
        if messages:
            message: hikari.Message = messages[0]
            attachments = [att.url for att in message.attachments]
            response = plugin.app.d.bot.ask_with_context(
                thread.id, attachments, message.content
            )
            await event.thread.send(response)
    else:
        print("Not question center")


@plugin.listener(hikari.GuildMessageCreateEvent)
async def on_message_create(event: hikari.GuildMessageCreateEvent) -> None:
    """Handles new messages in the question center thread to respond to follow-up questions."""
    message = event.message
    if message.author.is_bot:
        return

    thread: hikari.GuildThreadChannel = await message.fetch_channel()
    if thread.parent_id != 1301822138319114302:
        return
    if len(await thread.fetch_history()) <= 1:
        return
    if 1302689724431073310 in thread.applied_tag_ids:
        print("Already responded")
        return

    response_count = plugin.app.d.bot.response_count.get(thread.id, 0)
    if response_count >= 4:
        ta_role_id = 1194665960376901773
        await thread.send(f"Bạn đợi các bạn TA <@&{ta_role_id}> một xíu nha!")
        await thread.edit(
            applied_tags=[1302689724431073310]
        )
    else:
        attachments = [att.url for att in message.attachments]
        response = plugin.app.d.bot.ask_with_context(
            thread.id, attachments, message.content
        )
        await thread.send(response)
