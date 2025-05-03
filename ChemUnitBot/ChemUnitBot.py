import math
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import re

# Dictionary of supported units with their conversion factors
# Each unit includes: base unit type, conversion factor, dimension
UNITS = {
    # Force units
    "newton": {"type": "force", "factor": 1, "symbol": "N"},
    "n": {"type": "force", "factor": 1, "symbol": "N"},
    "dyne": {"type": "force", "factor": 1e-5, "symbol": "dyn"},
    "dyn": {"type": "force", "factor": 1e-5, "symbol": "dyn"},

    # Pressure units
    "pa": {"type": "pressure", "factor": 1, "symbol": "Pa"},
    "pascal": {"type": "pressure", "factor": 1, "symbol": "Pa"},
    "kpa": {"type": "pressure", "factor": 1000, "symbol": "kPa"},
    "bar": {"type": "pressure", "factor": 100000, "symbol": "bar"},
    "atm": {"type": "pressure", "factor": 101325, "symbol": "atm"},
    "mmhg": {"type": "pressure", "factor": 133.322, "symbol": "mmHg"},
    "torr": {"type": "pressure", "factor": 133.322, "symbol": "torr"},
    "psi": {"type": "pressure", "factor": 6894.76, "symbol": "psi"},

    # Surface tension units
    "dyne/cm": {"type": "surface_tension", "factor": 0.001, "symbol": "dyn/cm"},
    "n/m": {"type": "surface_tension", "factor": 1, "symbol": "N/m"},

    # Energy units
    "j": {"type": "energy", "factor": 1, "symbol": "J"},
    "joule": {"type": "energy", "factor": 1, "symbol": "J"},
    "erg": {"type": "energy", "factor": 0.0000001, "symbol": "erg"},
    "dynecm": {"type": "energy", "factor": 0.0000001, "symbol": "dynecm"},
    "cal": {"type": "energy", "factor": 4.184, "symbol": "cal"},
    "calorie": {"type": "energy", "factor": 4.184, "symbol": "cal"},

    # Volume units
    "m^3": {"type": "volume", "factor": 1, "symbol": "m³"},
    "cm^3": {"type": "volume", "factor": 1e-6, "symbol": "cm³"},
    "l": {"type": "volume", "factor": 0.001, "symbol": "L"},
    "liter": {"type": "volume", "factor": 0.001, "symbol": "L"},
    "ml": {"type": "volume", "factor": 1e-6, "symbol": "mL"},

    # Length units
    "m": {"type": "length", "factor": 1, "symbol": "m"},
    "cm": {"type": "length", "factor": 0.01, "symbol": "cm"},
    "mm": {"type": "length", "factor": 0.001, "symbol": "mm"},
    "angstrom": {"type": "length", "factor": 1e-10, "symbol": "Å"},
    "nm": {"type": "length", "factor": 1e-9, "symbol": "nm"},
    "inch": {"type": "length", "factor": 0.0254, "symbol": "in"},
}

# Unit conversion function


def convert_units(value, from_unit, to_unit):
    from_unit = from_unit.lower().replace(" ", "")
    to_unit = to_unit.lower().replace(" ", "")

    # Handle cubic units (m³, cm³, etc.)

    if from_unit.endswith("³"):
        from_unit = from_unit.replace("³", "^3")
    if to_unit.endswith("³"):
        to_unit = to_unit.replace("³", "^3")

    # Try to get unit information
    from_unit_info = UNITS.get(from_unit)
    to_unit_info = UNITS.get(to_unit)

    if not from_unit_info:
        return f"❌ Error: '{from_unit}' is not a supported unit."

    if not to_unit_info:
        return f"❌ Error: '{to_unit}' is not a supported unit."

    if from_unit_info["type"] != to_unit_info["type"]:
        return f"❌ Error: Cannot convert between different unit types: {from_unit_info['type']} and {to_unit_info['type']}."

    # Calculate the conversion
    result = value * from_unit_info["factor"] / to_unit_info["factor"]
    from_symbol = from_unit_info["symbol"]
    to_symbol = to_unit_info["symbol"]

    # Format the result
    superscripts = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")

    if result != 0 and math.log10(abs(result)).is_integer():
        exponent = int(math.log10(abs(result)))
        formatted_result = f"10{str(exponent).translate(superscripts)}"
    else:
        formatted_result = f"{result:.6f}".rstrip('0').rstrip('.')

    return f"✅ {value} {from_symbol} = {formatted_result} {to_symbol}"


# Parse the user input


def parse_conversion_request(text):
    # Try standard format "X unit to unit"
    match = re.match(
        r"^\s*(\d+\.?\d*)\s*([a-zA-Z/^³3]+)\s+to\s+([a-zA-Z/^³3]+)\s*$", text, re.IGNORECASE)
    if match:
        value = float(match.group(1))
        from_unit = match.group(2)
        to_unit = match.group(3)
        return value, from_unit, to_unit

    return None, None, None

# Telegram command handlers


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to ChemUnitBot!\n\n"
        "I can convert between these specific units:\n\n"
        "• Force: newton (N), dyne (dyn)\n"
        "• Pressure: pascal (Pa), kPa, bar, atm, mmHg, torr, psi\n"
        "• Surface tension: dyne/cm, N/m\n"
        "• Energy: joule (J), calorie (cal)\n"
        "• Volume: m³, cm³, liter (L), mL\n"
        "• Length: m, cm, mm, angstrom (Å), nm, inch\n\n"
        "Simply use the format:\n"
        "25 atm to Pa\n"
        "10 dyne to N\n"
        "5 J to cal\n\n"
        "Try it now!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    units_list = "\n".join([
        "• Force: newton (N), dyne (dyn)",
        "• Pressure: pascal (Pa), kPa, bar, atm, mmHg, torr, psi",
        "• Surface tension: dyne/cm, N/m",
        "• Energy: joule (J), calorie (cal)",
        "• Volume: m³, cm³, liter (L), mL",
        "• Length: m, cm, mm, angstrom (Å), nm, inch"
    ])

    await update.message.reply_text(
        "📚 ChemUnitBot Help\n\n"
        f"Supported units:\n{units_list}\n\n"
        "Usage examples:\n"
        "• 25 atm to Pa\n"
        "• 10 dyne to N\n"
        "• 5 J to cal\n"
        "• 100 cm^3 to mL\n"
        "• 72 dyne/cm to N/m\n\n"
        "If you encounter any issues, make sure your format is correct: '25 unit to unit'"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    value, from_unit, to_unit = parse_conversion_request(text)

    if value is None:
        await update.message.reply_text("⚠️ Format not recognized. Please use: 25 atm to Pa")
        return

    result = convert_units(value, from_unit, to_unit)
    await update.message.reply_text(result)

# Main function


async def main():
    # Replace with your actual token
    import os
    token = os.getenv("BOT_TOKEN")

    app = ApplicationBuilder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 ChemUnitBot is running... Press Ctrl+C to stop.")

    # Start the bot
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Keep the bot running until Ctrl+C is pressed
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    asyncio.run(main())
