from Bot import Bot

if __name__ == "__main__":
    print('Hello. I am your contact-assistant. What should I do with your contacts?')
    bot = Bot()
    bot.book.load("auto_save")
    commands = ['Add', 'Search', 'Edit', 'Load', 'Remove', 'Save', 'Congratulate', 'View', 'Exit']
    while True:
        action = input('Type help for list of commands or enter your command\n').strip().lower()
        if action == 'help':
            print(" ".join(f"{command:^20}" for command in commands))
            action = input().strip().lower()
        bot.handle(action)
        if action in ['add', 'remove', 'edit']:
            bot.book.save("auto_save")
        if action == 'exit':
            break