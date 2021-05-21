import aiosqlite
from fuzzywuzzy import process
from discord.ext import commands, tasks


class WrongKeyError(commands.CommandError):
    def __init__(self, key):
        self.key = key
        super().__init__(f"Il n'y a pas de conseil sous la clé {key}")


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._create_tables.start()

    @commands.group(invoke_without_command=True)
    async def conseil(self, ctx, *, mots: str):
        '''donne un conseil sur ce que vous demandez si disponible'''

        row = await self._get_conseil(mots)
        if row is None:
            raise WrongKeyError(mots)

        else:
            await ctx.send(row['conseil'])

    @conseil.error
    async def conseil_error(self, ctx, error):
        """Error handler for the conseil command."""

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Il faut préciser le conseil à montrer.")

        elif isinstance(error, WrongKeyError):
            possible_keys = "\n".join(await self.fuzzy_key_search(error.key))
            prefix = "Il n'y a pas de conseil sous cette clé."

            if possible_keys:  # length not 0
                content = (
                    f"{prefix}\n"
                    f"Vouliez-vous dire:\n```\n{possible_keys}\n```"
                )
            else:
                content = prefix

            await ctx.send(content)

        else:
            raise error

    @conseil.command(name='create')
    async def conseil_create(self, ctx, motclé: str, *, conseil: str):
        """Subcommande pour créer un nouveau conseil."""

        await self._save_conseil(ctx, motclé, conseil)

        await ctx.send(
            f"OK! J'ai enregistré le conseil sous la clé `{motclé}`.")

    @conseil_create.error
    async def conseil_create_error(self, ctx, _error):
        """Error handler for the conseil_create command."""

        error = getattr(_error, 'original', _error)

        if isinstance(error, aiosqlite.IntegrityError):
            await ctx.send("Il y a déjà un conseil avec cette clé.")

        else:
            # if we don't know what the error is,
            # raise it so it is not suppressed
            raise _error

    # TODO: conseil_delete, conseil_update commands

    async def fuzzy_key_search(self, key):
        """Search for keys that are similar to the one requested."""

        min_score = 75
        keys = [row["key"] for row in await self._get_conseil_keys()]
        extracted = process.extract(key, keys, limit=3)

        matched_keys = [_key for _key, score in extracted if score >= min_score]

        return matched_keys


    @tasks.loop(count=1)
    async def _create_tables(self):
        """Crée les tables nécessaires, si elles n'existent pas déjà."""

        await self.bot.db.execute(
            """
            CREATE TABLE IF NOT EXISTS information_conseil(
                conseil    TEXT      NOT NULL,
                created_at TIMESTAMP NOT NULL,
                key        TEXT      NOT NULL UNIQUE,
                user_id    INTEGER   NOT NULL
            )
            """
        )

        await self.bot.db.commit()

    async def _get_conseil(self, key):
        """Cherche le conseil avec la clé 'key' dans la base de données.
        Peut retourner None si la clé n'existe pas.
        """
        async with self.bot.db.execute(
                """
                SELECT *
                  FROM information_conseil
                 WHERE key = :key
                """,
                {'key': key}
        ) as c:
            row = await c.fetchone()

        return row

    async def _get_conseil_keys(self):
        """Retourne les keys attachées à tous les conseils."""

        async with self.bot.db.execute(
                """
                SELECT key
                  FROM information_conseil
                """
        ) as c:
            rows = await c.fetchall()

        return rows

    async def _save_conseil(self, ctx, key, conseil):
        """Enregistre le conseil dans la base de données."""

        await self.bot.db.execute(
            """
            INSERT INTO information_conseil
            VALUES (:conseil,
                    :created_at,
                    :key,
                    :user_id)
            """,
            {
                'conseil': conseil,
                'created_at': ctx.message.created_at,
                'key': key,
                'user_id': ctx.author.id,
            }
        )

        await self.bot.db.commit()
