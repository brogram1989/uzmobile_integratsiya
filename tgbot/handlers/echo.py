from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

echo_router = Router()


@echo_router.message(F.text, StateFilter(None))
async def bot_echo(message: types.Message):
    text = ["exo bo'limidasiz", "sizning xabar o'zingizga qaytadi:", message.text]

    await message.answer("\n".join(text))


@echo_router.message(F.text)
async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    text = [
        f"exo bo'limidasiz {hcode(state_name)}",
        "Sizning xabaringiz o'zingizga qaytadi:",
        hcode(message.text),
    ]
    await message.answer("\n".join(text))
