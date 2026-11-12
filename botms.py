"""
بوت تلغرام لخدمة الطلاب المستجدين - كلية الصيدلة، الجامعة الوطنية الخاصة
المكتبة: aiogram 3.x  |  وضع التشغيل: Long Polling (مناسب لـ Railway كخدمة Worker)
"""

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import (
    KeyboardButton,
    LinkPreviewOptions,
    Message,
    ReplyKeyboardMarkup,
)
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1) الإعدادات: قراءة التوكن من متغيرات البيئة (.env محلياً / Variables في Railway)
# ---------------------------------------------------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("pharmacy_bot")

# ---------------------------------------------------------------------------
# 2) نصوص الأزرار (أسماء الأزرار)
# ---------------------------------------------------------------------------
BTN_GUIDE = "🏛️ دليلك في الكلية"
BTN_COURSES = "📚 المواد والدكاترة"
BTN_FAQ = "❓ الأسئلة الشائعة"
BTN_LINKS = "🔗 الروابط الهامة"
BTN_ABOUT = "👑 من أنا؟"

# ---------------------------------------------------------------------------
# 3) النصوص المعتمدة للردود (حرفياً كما وردت)
# ---------------------------------------------------------------------------
WELCOME_TEXT = (
    "أهلاً بك زميلنا المستجد في كلية الصيدلة 💊\n"
    "اختر من القائمة أدناه ما تريد الاطلاع عليه 👇"
)

GUIDE_TEXT = """أهلاً بك زميلنا المستجد في كلية الصيدلة بالجامعة الوطنية الخاصة! 💊
لتبدأ طريقك صح، هذه رسالة دليلك الأساسي:
⏱️ نظام الساعات المعتمدة:
دراستنا بتعتمد على نظام الساعات، والخطة الدرسية مصممة لتتخرج خلال 5 سنوات. المادة التي وزنها (1 أو 2 ساعة) هي نظرية فقط، والمادة (3 ساعات فأكثر) تحوي قسم عملي.
📊 كيف تتوزع علاماتك؟ (المجموع 100)
1️⃣ المواد التي تحوي قسم عملي:
العملي (30 علامة): (4 حضور، 4 كويز، 7 مذاكرة، 15 فاينل عملي).
النظري (70 علامة): (20 مذاكرة نصفية، 50 فاينل).
2️⃣ المواد النظرية فقط: 40 علامة للمذاكرة، 60 للفاينل.
📈 المعدل التراكمي GPA:
تحت الـ 50 (F) رسوب. من 50 وفوق يعتبر نجاح وتتدرج الأحرف (D, C, B, A).
🏢 خريطة بناء الكلية (4 طوابق رئيسية):
⬇️ البهو (القبو): مصلى للذكور والإناث.
0️⃣ الطابق الأرضي: قاعات المحاضرات النظرية والمدرج 101 للفعاليات.
1️⃣ الطابق الأول: مكتب العميد، السكرتارية، شؤون الطلبة، الامتحانات، ومخابر الصيدلانيات والعقاقير.
2️⃣ الطابق الثاني: كافيتيريا الكلية، المكتبة، ومخابر الكيمياء.
ملاحظة: الحمامات متوفرة بكل الطوابق باستثناء الطابق الأول (مخصص للإداريين). المخابر مزودة بأحدث الأجهزة والقاعات مكيفة ومجهزة للعرض."""

COURSES_TEXT = """📖 مواد السنة الأولى - الفصل الأول:
اللغة العربية: بإشراف د. موفق السراج.
بيولوجيا نباتية: بإشراف د. سيلفا زيادة.
تشريح: بإشراف د. مروان خطاب.
كيمياء عامة ولاعضوية: بإشراف د. حنين حمود.
فيزيولوجيا: بإشراف د. مروان خطاب.
بيو حيوان (بيولوجيا حيوانية): بإشراف د. محمد فاضل.
مهارات حاسوب: بإشراف د. فرح الحكيم.
💡 نصيحة من أخ لأخواته (من رئيس الهيئة الطلابية):
تابع دراستك بشكل فوري، لا تراكم موادك. بمجرد بدء كويزات العملي، ستدخل في دوامة ضغط دراسي (كويزات ثم مذاكرات عملي ثم مذاكرات نظري ثم فاينل عملي ثم فاينل نظري). هذا الضغط طبيعي جداً! نظم وقتك، ادرس أولاً بأول، ولا تخجل أبداً من سؤال الدكتور ليعيد لك أي معلومة لم تفهمها."""

FAQ_TEXT = """1️⃣ كيف بسجل المقررات؟
التوجه لمبنى الشؤون المركزية لتثبيت القبول والدفع.
التوجه لمبنى رئاسة الجامعة (قسم IT) لتفعيل موقعك الرسمي (أوتوماتا).
التوجه لكلية الصيدلة (الطابق الأول - شؤون الطلبة) لتقديم طلب تنزيل المواد (18 ساعة).
انتظار تثبيت جدول محاضراتك على موقعك.
2️⃣ في مواصلات للجامعة؟
طبعاً! النقل الرسمي متوفر لـ (حمص، حماة، السلمية). باقي المدن عبر شركات خارجية (سومر لحلب وإدلب، وألو مشوار لريف حماة الشمالي).
3️⃣ من وين بشتري المقررات والقرطاسية؟
مقابل كلية الصيدلة يوجد مبنى المكتبة الرسمية.
4️⃣ وين بتابع إعلانات الكلية؟
من خلال الغروبات الرسمية بإشراف الهيئة الطلابية (روابطها في قسم الروابط الهامة)."""

LINKS_TEXT = """📱 الغروبات الرسمية لدفعة 2026 (واتساب):
الغروب المغلق (للإعلانات): https://chat.whatsapp.com/H8TSilCYJJNBc2IrSmp5Wi?s=cl&p=a&iam=2
غروب المناقشة: https://chat.whatsapp.com/GCu7QCpYkXj468bDghw8La?s=cl&p=a&iam=2
📚 قنوات الفرق التطوعية (WBCs):
WBc|5: https://t.me/ph_WBCSpharmacy
WBc|4: https://t.me/WBCsteamph
WBc|3: https://t.me/pharmacyfilesWBCs
📝 قنوات الامتحانات والملخصات:
قناة سلالم التصحيح: https://t.me/studentsph
قناة الدورات والملخصات: https://t.me/uhhd87892
غروب بيع المقررات: https://t.me/+3P5yOULxcvtmMTU0
💊 مساحات علمية وإبداعية:
قناة دليلك الدوائي : https://t.me/mgh_math25
مساحة الشعر: https://t.me/le_Ghaith0000"""

ABOUT_TEXT = """أهلاً بكم زملاء المستقبل،
أنا أخوكم وزميلكم محمد غيث منار نبهان (غيث).
ابن بلدة قمحانة، وطالب صيدلة في السنة الثالثة (بمعدل تراكمي 3.4)، أقف اليوم معكم كداعم لكم في كل خطوة ضمن أسوار هذه الكلية.
أتشرف بخدمتكم من خلال موقعي كـ:
رئيس الهيئة الطلابية بكلية الصيدلة.
نائب رئيس مكتب شؤون وقضايا الطلبة.
بعيداً عن الأروقة الأكاديمية، أنا روائي وكاتب، صدر لي روايتا «ليفوداون» و«قيامة الروح»، وأعمل حالياً على الجزء الجديد «قيامة الروح : غرام في عتبة الصمت». إلى جانب ذلك، أنا مبرمج، وشاعر، وحاصل على شهادة ICDL.
بابي مفتوح دائماً لأي استفسار أو مساعدة. نحن هنا عائلة واحدة.
📞 للتواصل في الحالات الطارئة: 0941326811"""

FALLBACK_TEXT = "اختر أحد الأزرار من القائمة أدناه 👇"

# تعطيل معاينة الروابط حتى لا تُغرق الرسالة بمعاينات كثيرة
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


# ---------------------------------------------------------------------------
# 4) لوحة المفاتيح الرئيسية
# ---------------------------------------------------------------------------
def main_keyboard() -> ReplyKeyboardMarkup:
    """يبني لوحة المفاتيح: صفّان بزرّين + صف بزر واحد."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_GUIDE), KeyboardButton(text=BTN_COURSES)],
            [KeyboardButton(text=BTN_FAQ), KeyboardButton(text=BTN_LINKS)],
            [KeyboardButton(text=BTN_ABOUT)],
        ],
        resize_keyboard=True,  # حجم أنيق ومتناسق للأزرار
        input_field_placeholder="اختر من القائمة 👇",
    )


# ---------------------------------------------------------------------------
# 5) المعالجات (Handlers)
# ---------------------------------------------------------------------------
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """رسالة الترحيب مع لوحة المفاتيح الرئيسية."""
    await message.answer(WELCOME_TEXT, reply_markup=main_keyboard())


@dp.message(F.text == BTN_GUIDE)
async def show_guide(message: Message) -> None:
    await message.answer(GUIDE_TEXT, reply_markup=main_keyboard())


@dp.message(F.text == BTN_COURSES)
async def show_courses(message: Message) -> None:
    await message.answer(COURSES_TEXT, reply_markup=main_keyboard())


@dp.message(F.text == BTN_FAQ)
async def show_faq(message: Message) -> None:
    await message.answer(FAQ_TEXT, reply_markup=main_keyboard())


@dp.message(F.text == BTN_LINKS)
async def show_links(message: Message) -> None:
    # الروابط تظهر قابلة للضغط تلقائياً (بدون parse_mode) مع إلغاء المعاينة
    await message.answer(
        LINKS_TEXT,
        reply_markup=main_keyboard(),
        link_preview_options=NO_PREVIEW,
    )


@dp.message(F.text == BTN_ABOUT)
async def show_about(message: Message) -> None:
    await message.answer(ABOUT_TEXT, reply_markup=main_keyboard())


@dp.message()
async def fallback(message: Message) -> None:
    """أي رسالة أخرى: نذكّر المستخدم بالأزرار."""
    await message.answer(FALLBACK_TEXT, reply_markup=main_keyboard())


# ---------------------------------------------------------------------------
# 6) نقطة التشغيل
# ---------------------------------------------------------------------------
async def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN غير موجود. أضفه في ملف .env أو في Variables على Railway.")
        sys.exit(1)

    # parse_mode غير مفعّل عمداً كي تبقى النصوص حرفية (رموز مثل | و _ لا تُكسر التنسيق)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties())

    # حذف أي webhook قديم وتجاهل الرسائل المتراكمة أثناء التوقف
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("البوت يعمل الآن...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("تم إيقاف البوت.")