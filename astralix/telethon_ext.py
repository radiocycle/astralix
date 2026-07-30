"""Custom Telethon extensions.

These methods are absent in upstream Telethon but used by the userbot.
They are patched onto telethon's classes at import time.
"""

import typing

from telethon import TelegramClient, types, utils, functions
from telethon.extensions import html


async def translate(
    self,
    peer,
    message,
    to_lang: str,
    raw_text: typing.Optional[str] = None,
    entities: typing.Optional[typing.List[types.TypeMessageEntity]] = None,
) -> str:
    """Translate a message using Telegram's built-in translation API."""
    msg_id = utils.get_message_id(message) or 0
    if not msg_id:
        return None

    if not isinstance(message, types.Message):
        message = (await self.get_messages(peer, ids=[msg_id]))[0]

    result = await self(
        functions.messages.TranslateTextRequest(
            peer=peer,
            id=[msg_id],
            text=[
                types.TextWithEntities(
                    raw_text or message.raw_text,
                    entities or message.entities or [],
                )
            ],
            to_lang=to_lang,
        )
    )

    return (
        html.unparse(
            result.result[0].text,
            result.result[0].entities,
        )
        if result and result.result
        else ""
    )


def _patch_message_methods():
    """Patch send_message and edit_message to accept and forward invert_media.

    Upstream Telethon doesn't accept ``invert_media``, but the underlying
    TL requests (SendMessageRequest / EditMessageRequest) do. We wrap the
    original methods to pop ``invert_media`` from kwargs, call the original,
    then set the flag on the constructed request before it's sent.
    """
    from telethon.client.messages import MessageMethods as TLMessageMethods

    if getattr(TLMessageMethods, "_invert_patched", False):
        return

    # --- wrap edit_message ---
    _orig_edit_message = TLMessageMethods.edit_message

    async def edit_message(self, *args, **kwargs):
        invert_media = kwargs.pop("invert_media", False)
        if not invert_media:
            return await _orig_edit_message(self, *args, **kwargs)

        # Replicate telethon's edit_message but with invert_media in the request.
        # We intercept at the __call__ level: temporarily wrap _call to inject
        # invert_media into EditMessageRequest.
        old_call = self._call

        async def patched_call(sender, request, *a, **kw):
            if isinstance(request, functions.messages.EditMessageRequest):
                request.invert_media = True
            elif isinstance(
                request, functions.messages.EditInlineBotMessageRequest
            ):
                request.invert_media = True
            return await old_call(sender, request, *a, **kw)

        self._call = patched_call
        try:
            return await _orig_edit_message(self, *args, **kwargs)
        finally:
            self._call = old_call

    # --- wrap send_message ---
    _orig_send_message = TLMessageMethods.send_message

    async def send_message(self, *args, **kwargs):
        invert_media = kwargs.pop("invert_media", False)
        if not invert_media:
            return await _orig_send_message(self, *args, **kwargs)

        old_call = self._call

        async def patched_call(sender, request, *a, **kw):
            if isinstance(request, functions.messages.SendMessageRequest):
                request.invert_media = True
            return await old_call(sender, request, *a, **kw)

        self._call = patched_call
        try:
            return await _orig_send_message(self, *args, **kwargs)
        finally:
            self._call = old_call

    edit_message.__wrapped__ = _orig_edit_message
    send_message.__wrapped__ = _orig_send_message
    TLMessageMethods.edit_message = edit_message
    TLMessageMethods.send_message = send_message
    TLMessageMethods._invert_patched = True


def patch_telethon_client():
    """Monkey-patch custom methods onto telethon.TelegramClient."""
    if not hasattr(TelegramClient, "translate"):
        TelegramClient.translate = translate

    _patch_message_methods()


# Auto-patch on import
patch_telethon_client()
