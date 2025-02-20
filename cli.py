from tkinter.ttk import Style

from vocab_llm_bot.app import UserDialogCtx


def main():
    try:
        app = UserDialogCtx()
        app.main_loop()
    except KeyboardInterrupt:
        print(Style.RESET_ALL)
        pass


if __name__ == '__main__':
    main()
