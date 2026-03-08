
########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory


MENU_COMMANDS = {
    "1": "add",
    "2": "subtract",
    "3": "multiply",
    "4": "divide",
    "5": "power",
    "6": "root",
    "7": "modulus",
    "8": "ind_divide",
    "9": "percent",
    "10": "abs_diff",
    "11": "history",
    "12": "clear",
    "13": "undo",
    "14": "redo",
    "15": "save",
    "16": "load",
    "0": "exit",
}


def show_menu():
    print("\n===== Calculator Menu =====")
    print("--- Operations ---")
    print("  1.  Add")
    print("  2.  Subtract")
    print("  3.  Multiply")
    print("  4.  Divide")
    print("  5.  Power")
    print("  6.  Root")
    print("  7.  Modulus")
    print("  8.  Integer Divide")
    print("  9.  Percentage")
    print("  10. Absolute Difference")
    print("--- History ---")
    print("  11. Show History")
    print("  12. Clear History")
    print("  13. Undo")
    print("  14. Redo")
    print("  15. Save History")
    print("  16. Load History")
    print("--- Other ---")
    print("  0.  Exit")
    print("===========================")


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

        print("Calculator started.")

        while True:
            try:
                # Display the menu and prompt the user for a choice
                show_menu()
                choice = input("Select an option: ").strip()
                command = MENU_COMMANDS.get(choice)

                if command is None:
                    print(f"Invalid option: '{choice}'. Please select a number from the menu.")
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print("History saved successfully.")
                    except Exception as e:
                        print(f"Warning: Could not save history: {e}")
                    print("Goodbye!")
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print("No calculations in history")
                    else:
                        print("\nCalculation History:")
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print("History cleared")
                    continue

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print("Operation undone")
                    else:
                        print("Nothing to undo")
                    continue

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print("Operation redone")
                    else:
                        print("Nothing to redo")
                    continue

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print("History saved successfully")
                    except Exception as e:
                        print(f"Error saving history: {e}")
                    continue

                if command == 'load':
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print("History loaded successfully")
                    except Exception as e:
                        print(f"Error loading history: {e}")
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'power', 'root',
                               'modulus', 'ind_divide', 'percent', 'abs_diff']:
                    # Perform the specified arithmetic operation
                    try:
                        print("\nEnter numbers (or 'cancel' to abort):")
                        a = input("First number: ")
                        if a.lower() == 'cancel':
                            print("Operation cancelled")
                            continue
                        b = input("Second number: ")
                        if b.lower() == 'cancel':
                            print("Operation cancelled")
                            continue

                        # Create the appropriate operation instance using the Factory pattern
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(f"\nResult: {result}")
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(f"Error: {e}")
                    except Exception as e:
                        # Handle any unexpected exceptions
                        print(f"Unexpected error: {e}")
                    continue

            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print("\nOperation cancelled")
                continue
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print("\nInput terminated. Exiting...")
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"Error: {e}")
                continue

    except Exception as e:
        # Handle fatal errors during initialization
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise