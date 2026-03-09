import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# ── Menu command map ──────────────────────────────────────────────────────────
# Mirrors MENU_COMMANDS in calculator_repl.py
EXIT      = '0'
ADD       = '1'
SUBTRACT  = '2'
MULTIPLY  = '3'
DIVIDE    = '4'
POWER     = '5'
ROOT      = '6'
MODULUS   = '7'
INT_DIV   = '8'
PERCENT   = '9'
ABS_DIFF  = '10'
HISTORY   = '11'
CLEAR     = '12'
UNDO      = '13'
REDO      = '14'
SAVE      = '15'
LOAD      = '16'
# ─────────────────────────────────────────────────────────────────────────────


def printed_lines(mock_print):
    """Helper: extract all printed strings from a mock_print call list."""
    return [str(c.args[0]) for c in mock_print.call_args_list]


# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:

            mock_log_dir.return_value     = temp_path / "logs"
            mock_log_file.return_value    = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"

            yield Calculator(config=config)


# ── Calculator Initialization ─────────────────────────────────────────────────

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None


# ── Logging Setup ─────────────────────────────────────────────────────────────

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value  = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')

        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")


# ── Observers ─────────────────────────────────────────────────────────────────

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers


def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers


# ── Operations ────────────────────────────────────────────────────────────────

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation


def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')


def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)


def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)


# ── Undo / Redo ───────────────────────────────────────────────────────────────

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []


def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1


# ── History Management ────────────────────────────────────────────────────────

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()


@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1':  ['2'],
        'operand2':  ['3'],
        'result':    ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    try:
        calculator.load_history()
        assert len(calculator.history) == 1
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1  == Decimal("2")
        assert calculator.history[0].operand2  == Decimal("3")
        assert calculator.history[0].result    == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")


def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history    == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []


# ── REPL: Exit ────────────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[EXIT])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
    lines = printed_lines(mock_print)
    assert any("History saved successfully" in p for p in lines)
    assert any("Goodbye" in p for p in lines)


# ── REPL: Invalid menu option ─────────────────────────────────────────────────

@patch('builtins.input', side_effect=['foobar', EXIT])
@patch('builtins.print')
def test_unknown_command(mock_print, mock_input):
    calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Invalid option" in p and "foobar" in p for p in lines)


# ── REPL: Addition ────────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[ADD, '2', '3', EXIT])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Result: 5" in p for p in lines)


# ── REPL: Undo ────────────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[UNDO, EXIT])
@patch('builtins.print')
def test_undo_success(mock_print, mock_input):
    with patch('app.calculator.Calculator.undo', return_value=True):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Operation undone" in p for p in lines)


@patch('builtins.input', side_effect=[UNDO, EXIT])
@patch('builtins.print')
def test_undo_nothing(mock_print, mock_input):
    with patch('app.calculator.Calculator.undo', return_value=False):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Nothing to undo" in p for p in lines)


# ── REPL: Redo ────────────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[REDO, EXIT])
@patch('builtins.print')
def test_redo_success(mock_print, mock_input):
    with patch('app.calculator.Calculator.redo', return_value=True):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Operation redone" in p for p in lines)


@patch('builtins.input', side_effect=[REDO, EXIT])
@patch('builtins.print')
def test_redo_nothing(mock_print, mock_input):
    with patch('app.calculator.Calculator.redo', return_value=False):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Nothing to redo" in p for p in lines)


# ── REPL: Save ────────────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[SAVE, EXIT])
@patch('builtins.print')
def test_save_success(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save:
        calculator_repl()
    assert mock_save.call_count >= 1
    lines = printed_lines(mock_print)
    assert any("History saved successfully" in p for p in lines)


@patch('builtins.input', side_effect=[SAVE, EXIT])
@patch('builtins.print')
def test_save_failure(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history',
               side_effect=[Exception("disk full"), None]):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Error saving history" in p for p in lines)


# ── REPL: Load ────────────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[LOAD, EXIT])
@patch('builtins.print')
def test_load_success(mock_print, mock_input):
    with patch('app.calculator.Calculator.load_history'):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("History loaded successfully" in p for p in lines)


@patch('builtins.input', side_effect=[LOAD, EXIT])
@patch('builtins.print')
def test_load_failure(mock_print, mock_input):
    with patch('app.calculator.Calculator.load_history',
               side_effect=Exception("file not found")):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Error loading history" in p for p in lines)


# ── REPL: Cancel ─────────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[ADD, 'cancel', EXIT])
@patch('builtins.print')
def test_cancel_first_number(mock_print, mock_input):
    with patch('app.calculator.Calculator.perform_operation') as mock_op:
        calculator_repl()
    mock_op.assert_not_called()
    lines = printed_lines(mock_print)
    assert any("Operation cancelled" in p for p in lines)


@patch('builtins.input', side_effect=[ADD, '5', 'cancel', EXIT])
@patch('builtins.print')
def test_cancel_second_number(mock_print, mock_input):
    with patch('app.calculator.Calculator.perform_operation') as mock_op:
        calculator_repl()
    mock_op.assert_not_called()
    lines = printed_lines(mock_print)
    assert any("Operation cancelled" in p for p in lines)


# ── REPL: Errors ──────────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[ADD, 'abc', '3', EXIT])
@patch('builtins.print')
def test_validation_error(mock_print, mock_input):
    calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Error:" in p for p in lines)


@patch('builtins.input', side_effect=[DIVIDE, '10', '0', EXIT])
@patch('builtins.print')
def test_operation_error_divide_by_zero(mock_print, mock_input):
    calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Error:" in p for p in lines)


@patch('builtins.input', side_effect=[ADD, '2', '3', EXIT])
@patch('builtins.print')
def test_unexpected_error_during_operation(mock_print, mock_input):
    with patch('app.calculator.Calculator.perform_operation',
               side_effect=RuntimeError("boom")):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Unexpected error" in p for p in lines)


# ── REPL: Decimal normalization ───────────────────────────────────────────────

@patch('builtins.input', side_effect=[ADD, '2', '3', EXIT])
@patch('builtins.print')
def test_result_decimal_normalized(mock_print, mock_input):
    with patch('app.calculator.Calculator.perform_operation',
               return_value=Decimal('5.000')):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Result: 5" in p for p in lines)


@patch('builtins.input', side_effect=[ADD, '2', '3', EXIT])
@patch('builtins.print')
def test_result_non_decimal(mock_print, mock_input):
    with patch('app.calculator.Calculator.perform_operation',
               return_value=42):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Result: 42" in p for p in lines)


# ── REPL: Interrupts ─────────────────────────────────────────────────────────

@patch('builtins.input', side_effect=[KeyboardInterrupt, EXIT])
@patch('builtins.print')
def test_keyboard_interrupt_continues(mock_print, mock_input):
    calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Operation cancelled" in p for p in lines)


@patch('builtins.input', side_effect=EOFError)
@patch('builtins.print')
def test_eof_exits_gracefully(mock_print, mock_input):
    calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Input terminated. Exiting..." in p for p in lines)


@patch('builtins.input', side_effect=[Exception("surprise"), EXIT])
@patch('builtins.print')
def test_generic_loop_exception_continues(mock_print, mock_input):
    calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Error:" in p for p in lines)


# ── REPL: Fatal init error ────────────────────────────────────────────────────

@patch('builtins.print')
def test_fatal_init_error_reraises(mock_print):
    with patch('app.calculator_repl.Calculator',
               side_effect=RuntimeError("init failed")):
        with pytest.raises(RuntimeError, match="init failed"):
            calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Fatal error" in p for p in lines)


# ── REPL: Exit save failure ───────────────────────────────────────────────────

@patch('builtins.input', side_effect=[EXIT])
@patch('builtins.print')
def test_exit_save_failure_warning(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history',
               side_effect=Exception("no space left")):
        calculator_repl()
    lines = printed_lines(mock_print)
    assert any("Warning: Could not save history" in p for p in lines)