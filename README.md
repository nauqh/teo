---
hide:
  - navigation
title: Home
---
# T.e.o - The Excellent Organizer 

![Version](https://img.shields.io/badge/Latest%20Version-1.0.0.dev-%2300b4d8.svg?&style=for-the-badge&logo=git&logoColor=white)
![Python](https://img.shields.io/badge/Python-%230096c7.svg?&style=for-the-badge&logo=python&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

![](./assets/poros.jpg)

## About the project
T.e.o, formerly known as [**P.o.r.o**]("Productive Organizer and Resource Orchestrator"), is a multifunctional bot designed to enhance forum management. With its advanced moderation and logging capabilities, it meticulously monitors forum activity, promoting moderator accountability and easing the workload for staff members by automating query filtering. 

Moreover, T.e.o excels in proactive engagement by sending timely reminders to TAs staff regarding unresolved queries as well as generating comprehensive monthly reports on forum interactions. Its user-friendly interface ensures efficient and swift operation, making it an indispensable tool for forum management.

## Interoperability
T.e.o is probably a useful bot for your server if:

- [x] Your server is active and needs automatic moderation
- [x] You want to give more power to your moderators
- [x] You need a long-term punishment management system

T.e.o is probably NOT the right bot for your server if:

❌ You don't already know how to use forum thread

❌ You aren't able and willing to read this wiki to solve most problems

If any of the above apply, then T.e.o will probably not be the best bot for your server, and you should consider searching on [discord.bots.gg](https://discord.bots.gg) for a different moderation bot.

## Techstack

The repository structure follows the conceptual architecture of Teobot, which consists of three loosely-coupled sub-systems.

To briefly explain these three sub-systems:

- **[Notificator](https://www.hikari-py.dev/)** utilizes `Asyncio` for interval checking of unresolved threads, ensuring timely notifications to moderators for thread resolution.
- **[Storage][storage]** relies on `PostgreSQL` as a robust and feature-rich database system for persistent storage of forum queries and session log, while leveraging `SQLAlchemy` as the ORM tool for simplified interaction with the database.
- **[Logger][logger]** utilizes built-in `Logging` to record and manage thread events, errors, and messages within the server. It employs different log levels to categorize messages, providing a comprehensive overview of system activities.


## Documentation

Since Teobot is built on the basis of Hikari library, it is essential to look for the library documentation for further implementation. 

- Hikari: [hikari-py.dev](https://www.hikari-py.dev/)
- Lightbulb: [lightbulb.readthedocs.io](https://hikari-lightbulb.readthedocs.io/en/latest/)


[storage]: https://docs.python.org/3/library/sqlite3.html
[logger]: https://docs.python.org/3/library/logging.html

