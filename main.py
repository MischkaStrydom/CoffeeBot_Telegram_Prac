import spacy
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Define the coffee shop menu with different sizes and prices
coffee_menu = {
    "cappuccino": {
        "small": 28.99,
        "medium": 34.90,
        "large": 44.90
    },
    "latte": {
        "small": 30.99,
        "medium": 39.90,
        "large": 48.90
    },
    "espresso": {
        "small": 18.99,
        "medium": 23.90,
        "large": 28.90
    },
    "mocha": {
        "small": 35.99,
        "medium": 40.90,
        "large": 48.90
    },
    "americano": {
        "small": 35.99,
        "medium": 40.90,
        "large": 48.90
    },
    "coffee": {
        "small": 20.99,
        "medium": 24.90,
        "large": 30.90
    },
    "milo": {
        "small": 30.99,
        "medium": 35.90,
        "large": 42.90
    },

    "tea": {
        "small": 19.99,
        "medium": 22.90,
        "large": 25.90
    },

}

# States
INIT, order_item_and_size, ADD_DRINK, DISPLAY_TOTAl, ENTER_ADDRESS  = range(5)
spacy_nlp = spacy.load("en_core_web_sm")

# ... (other code remains the same)

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Goodbye! Have a good day.")
    return ConversationHandler.END

def start(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text.strip().lower()

    if user_message == "/start":
        update.message.reply_text("Hello! Welcome to CoffeeBot!\n\nWould you like to see our menu? Please enter 'y' for yes or 'n' for no.", reply_markup=ForceReply(selective=True))
        return INIT
    elif user_message == "y":
        menu_text = "Here's our menu:\n\n"
        for item, sizes in coffee_menu.items():
            size_text = ", ".join([f"{size.capitalize()} (R{price:.2f})" for size, price in sizes.items()])
            menu_text += f"{item.capitalize()}:\n" + f"{size_text}\n\n"

        update.message.reply_text(menu_text)
        update.message.reply_text("Please select a drink from the menu.", reply_markup=ForceReply(selective=True))
        return order_item_and_size
    elif user_message == "n":
        update.message.reply_text("Thank you for considering CoffeeBot! Feel free to return if you decide to place an order.")
        return ConversationHandler.END
    else:
        update.message.reply_text("I'm sorry, I didn't understand your response. Please enter 'y' for yes or 'n' for no.", reply_markup=ForceReply(selective=True))
        return INIT

def order_item_and_size(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text.strip().lower()
    doc = spacy_nlp(user_message)

    ordered_item = context.user_data.get("ordered_item")
    ordered_size = context.user_data.get("ordered_size")



    if not ordered_item:
        for token in doc:
            if token.text in coffee_menu:
                ordered_item = token.text
                context.user_data["ordered_item"] = ordered_item

                break

    if ordered_item:
        if ordered_item and not ordered_size:
            sizes = coffee_menu.get(ordered_item)
            size_options = ", ".join(sizes.keys())

            if any(size in user_message for size in ["small", "medium", "large"]):
                for size in ["small", "medium", "large"]:
                    if size in user_message:
                        ordered_size = size
                        context.user_data["ordered_size"] = ordered_size
                        price = coffee_menu[ordered_item][ordered_size]
                        context.user_data.setdefault("orders", []).append({"item": ordered_item, "size": ordered_size, "price": price})
                        response = f"You've added a {ordered_size} {ordered_item} to your order."
                        response += "\n\nWould you like to add more drinks to your order? Please enter 'y' for yes or 'n' for no."
                        # Reset ordered_item and ordered_size
                        context.user_data["ordered_item"] = None
                        context.user_data["ordered_size"] = None
                        update.message.reply_text(response, reply_markup=ForceReply(selective=True))
                        return ADD_DRINK


            response = f"Great! You've selected {ordered_item.capitalize()}. What size would you like? We offer {size_options} sizes."
            update.message.reply_text(response, reply_markup=ForceReply(selective=True))
            return order_item_and_size
        else:
            update.message.reply_text(
                "I'm sorry, that's not a valid drink option. Please choose a drink from the menu.")
            return INIT
    else:
        update.message.reply_text(
            "I'm sorry, that's not a valid drink option. Please choose a drink from the menu.")
        return order_item_and_size
    return INIT



def add_drink(update: Update, context: CallbackContext) -> int:
    user_message = update.message.text.strip().lower()

    if user_message == "y":
        update.message.reply_text("Sure! What drink would you like to add to your order? Please select a drink from the menu.",reply_markup=ForceReply(selective=True))
        return order_item_and_size
    elif user_message == "n":
        return display_total(update, context)  # Go back to displaying the total
    else:
        update.message.reply_text(
            "I'm sorry, I didn't understand your response. Please enter 'y' for yes or 'n' for no.",
            reply_markup=ForceReply(selective=True))
        return add_drink


def display_total(update: Update, context: CallbackContext) -> int:
    orders = context.user_data.get("orders", [])
    total_cost = sum(order["price"] for order in orders)

    response = "Your order breakdown:\n\n"
    for idx, order in enumerate(orders, start=1):
        response += f"{idx}. {order['size']} {order['item']} (R{order['price']:.2f})\n"

    response += f"\nTotal: R{total_cost:.2f}\n"
    # response += "Thank you for placing your order!"



    response += "Thank you for placing your order!\nPlease enter your address for delivery."

    update.message.reply_text(response)

    return ENTER_ADDRESS  # Move to the next state for entering address


def enter_address(update: Update, context: CallbackContext) -> int:
    address = update.message.text.strip()

    # Save the address to user_data or handle it as needed
    context.user_data["address"] = address

    update.message.reply_text(f"Thank you! Your order will be delivered to the following address:\n{address} whithin the next hour.")
    return ConversationHandler.END  # End the conversation

# Modify the ConversationHandler to include the new states
def main():
    updater = Updater(token="5813156167:AAFgXROYVlTsEi9B2hhtdIlKmkB71XTXNbY", use_context=True)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INIT: [MessageHandler(Filters.text & ~Filters.command, start)],
            order_item_and_size: [MessageHandler(Filters.text & ~Filters.command, order_item_and_size)],
            ADD_DRINK: [MessageHandler(Filters.text & ~Filters.command, add_drink)],
            DISPLAY_TOTAl: [MessageHandler(Filters.text & ~Filters.command, display_total)],
            ENTER_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, enter_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()