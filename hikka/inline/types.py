# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# 🌐 https://github.com/hikariatama/Hikka
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🔑 https://www.gnu.org/licenses/agpl-3.0.html

from __future__ import annotations  # Я В РОТ ЕБАЛ ЭТУ ХУЙНЮ

import logging
from typing import Any, Optional, Union

from aiogram import Bot
from aiogram.types import CallbackQuery, InlineQueryResultsButton, InlineQueryResultVoice, InlineQueryResultVideo, \
    InlineQueryResultVenue, InlineQueryResultPhoto, InlineQueryResultMpeg4Gif, InlineQueryResultLocation, \
    InlineQueryResultGif, InlineQueryResultDocument, InlineQueryResultContact, InlineQueryResultAudio, \
    InlineQueryResultGame, InlineQueryResultCachedVoice, InlineQueryResultCachedAudio, InlineQueryResultCachedDocument, \
    InlineQueryResultCachedGif, InlineQueryResultCachedMpeg4Gif, InlineQueryResultCachedPhoto, \
    InlineQueryResultCachedSticker, InlineQueryResultCachedVideo
from aiogram.types import InlineQuery as AiogramInlineQuery
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import Message as AiogramMessage
from aiogram.methods import AnswerInlineQuery
from pydantic import ConfigDict, Field
from pydantic._internal import _model_construction

from .. import utils

logger = logging.getLogger(__name__)


class InlineMessage:
    """Aiogram message, sent via inline bot"""
    form: Optional[Any] = Field(None)

    def __init__(
        self,
        inline_manager: "InlineManager",  # type: ignore  # noqa: F821
        unit_id: str,
        inline_message_id: str,
    ):
        self.inline_message_id = inline_message_id
        self.unit_id = unit_id
        self.inline_manager = inline_manager
        self._units = inline_manager._units
        self.form = (
            {"id": unit_id, **self._units[unit_id]} if unit_id in self._units else {}
        )

    async def edit(self, *args, **kwargs) -> "InlineMessage":
        if "unit_id" in kwargs:
            kwargs.pop("unit_id")

        if "inline_message_id" in kwargs:
            kwargs.pop("inline_message_id")

        return await self.inline_manager._edit_unit(
            *args,
            unit_id=self.unit_id,
            inline_message_id=self.inline_message_id,
            **kwargs,
        )

    async def delete(self) -> bool:
        return await self.inline_manager._delete_unit_message(
            self,
            unit_id=self.unit_id,
        )

    async def unload(self) -> bool:
        return await self.inline_manager._unload_unit(unit_id=self.unit_id)


class BotInlineMessage:
    """Aiogram message, sent through inline bot itself"""

    def __init__(
        self,
        inline_manager: "InlineManager",  # type: ignore  # noqa: F821
        unit_id: str,
        chat_id: int,
        message_id: int,
    ):
        self.chat_id = chat_id
        self.unit_id = unit_id
        self.inline_manager = inline_manager
        self.message_id = message_id
        self._units = inline_manager._units
        self.form = (
            {"id": unit_id, **self._units[unit_id]} if unit_id in self._units else {}
        )

    async def edit(self, *args, **kwargs) -> "BotMessage":
        if "unit_id" in kwargs:
            kwargs.pop("unit_id")

        if "message_id" in kwargs:
            kwargs.pop("message_id")

        if "chat_id" in kwargs:
            kwargs.pop("chat_id")

        return await self.inline_manager._edit_unit(
            *args,
            unit_id=self.unit_id,
            chat_id=self.chat_id,
            message_id=self.message_id,
            **kwargs,
        )

    async def delete(self) -> bool:
        return await self.inline_manager._delete_unit_message(
            self,
            unit_id=self.unit_id,
            chat_id=self.chat_id,
            message_id=self.message_id,
        )

    async def unload(self, *args, **kwargs) -> bool:
        if "unit_id" in kwargs:
            kwargs.pop("unit_id")

        return await self.inline_manager._unload_unit(
            *args,
            unit_id=self.unit_id,
            **kwargs,
        )


class InlineCall(CallbackQuery, InlineMessage):
    """Modified version of classic aiogram `CallbackQuery`"""
    model_config = ConfigDict(
        use_enum_values=True,
        extra="ignore",
        validate_assignment=True,
        frozen=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        defer_build=True,
    )
    __pydantic_extra__: dict[str, Any] | None = _model_construction.NoInitField(init=False)
    __pydantic_private__: dict[str, Any] | None = _model_construction.NoInitField(init=False)
    unit_id: Optional[str] = Field(None)
    inline_manager: Optional[Any] = Field(None)

    def __init__(
        self,
        call: CallbackQuery | Any,
        inline_manager: Any,
        unit_id: str,
    ):
        try: CallbackQuery.__init__(
            self,
            id=call.id,
            from_user=call.from_user,
            chat_instance=call.chat_instance,
            message=call.message,
            inline_message_id=call.inline_message_id,
            data=call.data,
            game_short_name=call.game_short_name,
        )
        except: pass

        for attr in {
            "id",
            "from_user",
            "chat_instance",
            "message",
            "inline_message_id",
            "chat_instance",
            "data",
            "game_short_name",
        }:
            try: setattr(self, attr, getattr(call, attr, None))
            except: pass

        self.as_(inline_manager.bot)

        InlineMessage.__init__(
            self,
            inline_manager,
            unit_id,
            call.inline_message_id,
        )

class BotInlineCall(CallbackQuery, BotInlineMessage):
    """Modified version of classic aiogram `CallbackQuery`"""
    model_config = ConfigDict(
        use_enum_values=True,
        extra="ignore",
        validate_assignment=True,
        frozen=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        defer_build=True,
    )
    __pydantic_extra__: dict[str, Any] | None = _model_construction.NoInitField(init=False)
    chat_id: Optional[int] = Field(None)
    unit_id: Optional[str] = Field(None)
    inline_manager: Optional[Any] = Field(None) # type: ignore  # noqa: F821
    message_id: Optional[int] = Field(None)
    form: Optional[Any] = Field(None)

    def __init__(
        self,
        call: CallbackQuery,
        inline_manager: Any,  # type: ignore  # noqa: F821
        unit_id: str,
    ):
        self.model_rebuild(raise_errors=False)
        CallbackQuery.__init__(
            self,
            id=call.id,
            from_user=call.from_user,
            chat_instance=call.chat_instance,
            message=call.message,
            inline_message_id=call.inline_message_id,
            data=call.data,
            game_short_name=call.game_short_name,
            )

        for attr in {
            "id",
            "from_user",
            "chat_instance",
            "message",
            "inline_message_id",
            "data",
            "game_short_name",
        }:
            setattr(self, attr, getattr(call, attr, None))
        setattr(self, "chat_id", getattr(call.message.chat, "id", None))

        BotInlineMessage.__init__(
            self,
            inline_manager,
            unit_id,
            call.message.chat.id,
            call.message.message_id,
        )


class InlineUnit:
    """InlineManager extension type. For internal use only"""

    def __init__(self):
        """Made just for type specification"""


class BotMessage(AiogramMessage):
    """Modified version of original Aiogram Message"""

    def __init__(self):
        super().__init__()


class CustomInlineQuery:
    def __init__(self, inline_query: AiogramInlineQuery, bot: "Bot"):
        self.inline_query = inline_query
        self._bot = bot

    def answer(
            self,
            inline_query_id: str,
            results: list[
                Union[
                    InlineQueryResultCachedAudio,
                    InlineQueryResultCachedDocument,
                    InlineQueryResultCachedGif,
                    InlineQueryResultCachedMpeg4Gif,
                    InlineQueryResultCachedPhoto,
                    InlineQueryResultCachedSticker,
                    InlineQueryResultCachedVideo,
                    InlineQueryResultCachedVoice,
                    InlineQueryResultArticle,
                    InlineQueryResultAudio,
                    InlineQueryResultContact,
                    InlineQueryResultGame,
                    InlineQueryResultDocument,
                    InlineQueryResultGif,
                    InlineQueryResultLocation,
                    InlineQueryResultMpeg4Gif,
                    InlineQueryResultPhoto,
                    InlineQueryResultVenue,
                    InlineQueryResultVideo,
                    InlineQueryResultVoice,
                ]
            ],
            cache_time: Optional[int] = None,
            is_personal: Optional[bool] = None,
            next_offset: Optional[str] = None,
            button: Optional[InlineQueryResultsButton] = None,
            switch_pm_parameter: Optional[str] = None,
            switch_pm_text: Optional[str] = None,
            **kwargs: Any,
    ) -> AnswerInlineQuery:
        from aiogram.methods import AnswerInlineQuery

        return AnswerInlineQuery(
            inline_query_id=inline_query_id,
            results=results,
            cache_time=cache_time,
            is_personal=is_personal,
            next_offset=next_offset,
            button=button,
            switch_pm_parameter=switch_pm_parameter,
            switch_pm_text=switch_pm_text,
            **kwargs,
        ).as_(self._bot)

    @staticmethod
    def _get_res(title: str, description: str, thumbnail_url: str) -> list:
        return [
            InlineQueryResultArticle(
                id=utils.rand(20),
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    message_text="😶‍🌫️ <i>There is nothing here...</i>",
                    parse_mode="HTML",
                ),
                thumbnail_url=thumbnail_url,
                thumbnail_width=128,
                thumbnail_height=128,
            )
        ]

    async def e400(self):
        await self.answer(
            self._get_res(
                "🚫 400",
                (
                    "Bad request. You need to pass right arguments, follow module's"
                    " documentation"
                ),
                "https://img.icons8.com/color/344/swearing-male--v1.png",
            ),
            cache_time=0,
        )

    async def e403(self):
        await self.answer(
            self._get_res(
                "🚫 403",
                "You have no permissions to access this result",
                "https://img.icons8.com/external-wanicon-flat-wanicon/344/external-forbidden-new-normal-wanicon-flat-wanicon.png",
            ),
            cache_time=0,
        )

    async def e404(self):
        await self.answer(
            self._get_res(
                "🚫 404",
                "No results found",
                "https://img.icons8.com/external-justicon-flat-justicon/344/external-404-error-responsive-web-design-justicon-flat-justicon.png",
            ),
            cache_time=0,
        )

    async def e426(self):
        await self.answer(
            self._get_res(
                "🚫 426",
                "You need to update Hikka before sending this request",
                "https://img.icons8.com/fluency/344/approve-and-update.png",
            ),
            cache_time=0,
        )

    async def e500(self):
        await self.answer(
            self._get_res(
                "🚫 500",
                "Internal userbot error while processing request. More info in logs",
                "https://img.icons8.com/external-vitaliy-gorbachev-flat-vitaly-gorbachev/344/external-error-internet-security-vitaliy-gorbachev-flat-vitaly-gorbachev.png",
            ),
            cache_time=0,
        )




class InlineQuery(AiogramInlineQuery):
    """Modified version of original Aiogram InlineQuery"""

    def __init__(self, inline_query: AiogramInlineQuery):
        super().__init__()

        for attr in {"id", "from_user", "query", "offset", "chat_type", "location"}:
            setattr(self, attr, getattr(inline_query, attr, None))

        self.inline_query = inline_query
        self.args = (
            self.inline_query.query.split(maxsplit=1)[1]
            if len(self.inline_query.query.split()) > 1
            else ""
        )

    @staticmethod
    def _get_res(title: str, description: str, thumbnail_url: str) -> list:
        return [
            InlineQueryResultArticle(
                id=utils.rand(20),
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    "😶‍🌫️ <i>There is nothing here...</i>",
                    parse_mode="HTML",
                ),
                thumbnail_url=thumbnail_url,
                thumbnail_width=128,
                thumbnail_height=128,
            )
        ]

    async def e400(self):
        await self.answer(
            self._get_res(
                "🚫 400",
                (
                    "Bad request. You need to pass right arguments, follow module's"
                    " documentation"
                ),
                "https://img.icons8.com/color/344/swearing-male--v1.png",
            ),
            cache_time=0,
        )

    async def e403(self):
        await self.answer(
            self._get_res(
                "🚫 403",
                "You have no permissions to access this result",
                "https://img.icons8.com/external-wanicon-flat-wanicon/344/external-forbidden-new-normal-wanicon-flat-wanicon.png",
            ),
            cache_time=0,
        )

    async def e404(self):
        await self.answer(
            self._get_res(
                "🚫 404",
                "No results found",
                "https://img.icons8.com/external-justicon-flat-justicon/344/external-404-error-responsive-web-design-justicon-flat-justicon.png",
            ),
            cache_time=0,
        )

    async def e426(self):
        await self.answer(
            self._get_res(
                "🚫 426",
                "You need to update Hikka before sending this request",
                "https://img.icons8.com/fluency/344/approve-and-update.png",
            ),
            cache_time=0,
        )

    async def e500(self):
        await self.answer(
            self._get_res(
                "🚫 500",
                "Internal userbot error while processing request. More info in logs",
                "https://img.icons8.com/external-vitaliy-gorbachev-flat-vitaly-gorbachev/344/external-error-internet-security-vitaliy-gorbachev-flat-vitaly-gorbachev.png",
            ),
            cache_time=0,
        )
