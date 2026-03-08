########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from colorama import init, Fore, Style
from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory

# Initialize colorama (auto-resets color after each print)
init(autoreset=True)

# ── Colour aliases ───────────────────────────────────────────────────────────
C_TITLE   = Fore.CYAN  + Style.BRIGHT   # Menu title
C_SECTION = Fore.YELLOW + Style.BRIGHT  # Section headers
C_OPTION  = Fore.WHITE                  # Menu options
C_PROMPT  = Fore.CYAN                   # Input prompts
C_RESULT  = Fore.GREEN  + Style.BRIGHT  # Successful results
C_ERROR   = Fore.RED    + Style.BRIGHT  # Errors
C_WARN    = Fore.YELLOW                 # Warnings
C_INFO    = Fore.BLUE   + Style.BRIGHT  # Info messages (history, undo, etc.)
C_RESET   = Style.RESET_ALL
# ─────────────────────────────────────────────────────────────────────────────

MENU_COMMANDS = {
    "1":  "add",
    "2":  "subtract",
    "3":  "multiply",
    "4":  "divide",
    "5":  "power",
    "6":  "root",
    "7":  "modulus",
    "8":  "ind_divide",
    "9":  "percent",
    "10": "abs_diff",
    "11": "history",
    "12": "clear",
    "13": "undo",
    "14": "redo",
    "15": "save",
    "16": "load",
    "0":  "exit",
}


def show_menu():
    print(f"\n{C_TITLE}{'=' * 27}")
    print(f"      Calculator Menu      ")
    print(f"{'=' * 27}{C_RESET}")

    print(f"{C_SECTION}  --- Operations ---{C_RESET}")
    print(f"{C_OPTION}  1.  Add")
    print(f"  2.  Subtract")
    print(f"  3.  Multiply")
    print(f"  4.  Divide")
    print(f"  5.  Power")
    print(f"  6.  Root")
    print(f"  7.  Modulus")
    print(f"  8.  Integer Divide")
    print(f"  9.  Percentage")
    print(f"  10. Absolute Difference{C_RESET}")

    print(f"{C_SECTION}  --- History ---{C_RESET}")
    print(f"{C_OPTION}  11. Show History")
    print(f"  12. Clear History")
    print(f"  13. Undo")
    print(f"  14. Redo")
    print(f"  15. Save History")
    print(f"  16. Load History{C_RESET}")

    print(f"{C_SECTION}  --- Other ---{C_RESET}")
    print(f"{Fore.RED}  0.  Exit{C_RESET}")

    print(f"{C_TITLE}{'=' * 27}{C_RESET}")


def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        # Initialize the Calculator instance
        calc = Calculator()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(f"{C_INFO}Calculator started.{C_RESET}")

        while True:
            try:
                # Display the menu and prompt the user for a choice
                show_menu()
                choice = input(f"{C_PROMPT}Select an option: {C_RESET}").strip()
                command = MENU_COMMANDS.get(choice)

                if command is None:
                    print(f"{C_ERROR}Invalid option: '{choice}'. Please select a number from the menu.{C_RESET}")
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(f"{C_INFO}History saved successfully.{C_RESET}")
                    except Exception as e:
                        print(f"{C_WARN}Warning: Could not save history: {e}{C_RESET}")
                    print(f"{C_TITLE}Goodbye!{C_RESET}")
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print(f"{C_WARN}No calculations in history{C_RESET}")
                    else:
                        print(f"\n{C_INFO}Calculation History:{C_RESET}")
                        for i, entry in enumerate(history, 1):
                            print(f"{C_OPTION}  {i}. {entry}{C_RESET}")
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print(f"{C_INFO}History cleared{C_RESET}")
                    continue

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print(f"{C_INFO}Operation undone{C_RESET}")
                    else:
                        print(f"{C_WARN}Nothing to undo{C_RESET}")
                    continue

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print(f"{C_INFO}Operation redone{C_RESET}")
                    else:
                        print(f"{C_WARN}Nothing to redo{C_RESET}")
                    continue

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print(f"{C_INFO}History saved successfully{C_RESET}")
                    except Exception as e:
                        print(f"{C_ERROR}Error saving history: {e}{C_RESET}")
                    continue

                if command == 'load':
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print(f"{C_INFO}History loaded successfully{C_RESET}")
                    except Exception as e:
                        print(f"{C_ERROR}Error loading history: {e}{C_RESET}")
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root',
                               'modulus', 'ind_divide', 'percent', 'abs_diff']:
                    # Perform the specified arithmetic operation
                    try:
                        print(f"\n{C_PROMPT}Enter numbers (or 'cancel' to abort):{C_RESET}")
                        a = input(f"{C_PROMPT}First number: {C_RESET}")
                        if a.lower() == 'cancel':
                            print(f"{C_WARN}Operation cancelled{C_RESET}")
                            continue
                        b = input(f"{C_PROMPT}Second number: {C_RESET}")
                        if b.lower() == 'cancel':
                            print(f"{C_WARN}Operation cancelled{C_RESET}")
                            continue

                        # Create the appropriate operation instance using the Factory pattern
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(f"\n{C_RESULT}Result: {result}{C_RESET}")
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(f"{C_ERROR}Error: {e}{C_RESET}")
                    except Exception as e:
                        # Handle any unexpected exceptions
                        print(f"{C_ERROR}Unexpected error: {e}{C_RESET}")
                    continue

            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print(f"\n{C_WARN}Operation cancelled{C_RESET}")
                continue
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print(f"\n{C_WARN}Input terminated. Exiting...{C_RESET}")
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"{C_ERROR}Error: {e}{C_RESET}")
                continue

    except Exception as e:
        # Handle fatal errors during initialization
        print(f"{C_ERROR}Fatal error: {e}{C_RESET}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise