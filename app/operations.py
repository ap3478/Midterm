########################
# Operation Classes    #
########################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from app.exceptions import ValidationError


class Operation(ABC):
    

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Execute the operation.

        """
        pass  # pragma: no cover

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands before execution.

        """
        pass

    def __str__(self) -> str:
        """
        Return operation name for display.

        """
        return self.__class__.__name__


class Addition(Operation):
    """
    Addition operation implementation.

    Performs the addition of two numbers.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Add two numbers.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Returns:
            Decimal: Sum of the two operands.
        """
        self.validate_operands(a, b)
        return a + b


class Subtraction(Operation):
    """
    Subtraction operation implementation.

    Performs the subtraction of one number from another.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Subtract one number from another.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Returns:
            Decimal: Difference between the two operands.
        """
        self.validate_operands(a, b)
        return a - b


class Multiplication(Operation):
    """
    Multiplication operation implementation.

    Performs the multiplication of two numbers.
    """

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Multiply two numbers.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Returns:
            Decimal: Product of the two operands.
        """
        self.validate_operands(a, b)
        return a * b


class Division(Operation):
    """
    Division operation implementation.

    Performs the division of one number by another.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands, checking for division by zero.

        Overrides the base class method to ensure that the divisor is not zero.

        Args:
            a (Decimal): Dividend.
            b (Decimal): Divisor.

        Raises:
            ValidationError: If the divisor is zero.
        """
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Divide one number by another.

        Args:
            a (Decimal): Dividend.
            b (Decimal): Divisor.

        Returns:
            Decimal: Quotient of the division.
        """
        self.validate_operands(a, b)
        return a / b


class Power(Operation):
    """
    Power (exponentiation) operation implementation.

    Raises one number to the power of another.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for power operation.

        Overrides the base class method to ensure that the exponent is not negative.

        Args:
            a (Decimal): Base number.
            b (Decimal): Exponent.

        Raises:
            ValidationError: If the exponent is negative.
        """
        super().validate_operands(a, b)
        if b < 0:
            raise ValidationError("Negative exponents not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate one number raised to the power of another.

        Args:
            a (Decimal): Base number.
            b (Decimal): Exponent.

        Returns:
            Decimal: Result of the exponentiation.
        """
        self.validate_operands(a, b)
        return Decimal(pow(float(a), float(b)))


class Root(Operation):
    """
    Root operation implementation.

    Calculates the nth root of a number.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for root operation.

        Overrides the base class method to ensure that the number is non-negative
        and the root degree is not zero.

        Args:
            a (Decimal): Number from which the root is taken.
            b (Decimal): Degree of the root.

        Raises:
            ValidationError: If the number is negative or the root degree is zero.
        """
        super().validate_operands(a, b)
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate the nth root of a number.

        Args:
            a (Decimal): Number from which the root is taken.
            b (Decimal): Degree of the root.

        Returns:
            Decimal: Result of the root calculation.
        """
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))

<<<<<<< HEAD
    
class Modulus(Operation):
    """
    Modulus operation implementation.
    Calculates the remainder of dividing one number by another.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for modulus operation.
        Overrides the base class method to ensure that the divisor is not zero.

        Args:
            a (Decimal): The dividend.
            b (Decimal): The divisor.

        Raises:
            ValidationError: If the divisor is zero.
        """
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Modulus by zero is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate the remainder of dividing a by b.

        Args:
            a (Decimal): The dividend.
            b (Decimal): The divisor.

        Returns:
            Decimal: The remainder of the division.
        """
        self.validate_operands(a, b)
        return a % b
    
class IntegerDivision(Operation):
    """
    Integer division operation implementation.
    Calculates the quotient of dividing one number by another, discarding the remainder.
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for integer division operation.
        Overrides the base class method to ensure that the divisor is not zero.

        Args:
            a (Decimal): The dividend.
            b (Decimal): The divisor.

        Raises:
            ValidationError: If the divisor is zero.
        """
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Integer division by zero is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate the integer quotient of dividing a by b.

        Args:
            a (Decimal): The dividend.
            b (Decimal): The divisor.

        Returns:
            Decimal: The integer result of the division, with the remainder discarded.
        """
        self.validate_operands(a, b)
        return a // b
    
class Percentage(Operation):
    """
    Percentage operation implementation.
    Calculates what percentage a is of b (a / b * 100).
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for percentage operation.
        Overrides the base class method to ensure that the base value is not zero.

        Args:
            a (Decimal): The part value.
            b (Decimal): The base value (cannot be zero).

        Raises:
            ValidationError: If the base value is zero.
        """
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Cannot calculate percentage of zero base value")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate what percentage a is of b.

        Args:
            a (Decimal): The part value.
            b (Decimal): The base value.

        Returns:
            Decimal: The percentage result (e.g., 50 for 50%).
        """
        self.validate_operands(a, b)
        return (a / b) * Decimal(100)
    
class AbsoluteDifference(Operation):
    """
    Absolute Difference operation implementation.
    Calculates the absolute difference between two numbers (|a - b|).
    """

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands for absolute difference operation.
        Relies on base class validation as there are no additional constraints.

        Args:
            a (Decimal): The first number.
            b (Decimal): The second number.
        """
        super().validate_operands(a, b)

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Calculate the absolute difference between a and b.

        Args:
            a (Decimal): The first number.
            b (Decimal): The second number.

        Returns:
            Decimal: The non-negative difference between a and b.
        """
        self.validate_operands(a, b)
        return abs(a - b)
=======
>>>>>>> Tests

class OperationFactory:
    """
    Factory class for creating operation instances.

    Implements the Factory pattern by providing a method to instantiate
    different operation classes based on a given operation type. This promotes
    scalability and decouples the creation logic from the Calculator class.
    """

    # Dictionary mapping operation identifiers to their corresponding classes
    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
<<<<<<< HEAD
        'root': Root,
        'modulus': Modulus,
        'int_divide': IntegerDivision,
        'percent': Percentage,
        'abs_diff': AbsoluteDifference
=======
        'root': Root
>>>>>>> Tests
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        """
        Register a new operation type.

        Allows dynamic addition of new operations to the factory.

        Args:
            name (str): Operation identifier (e.g., 'modulus').
            operation_class (type): The class implementing the new operation.

        Raises:
            TypeError: If the operation_class does not inherit from Operation.
        """
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """
        Create an operation instance based on the operation type.

        This method retrieves the appropriate operation class from the
        _operations dictionary and instantiates it.

        Args:
            operation_type (str): The type of operation to create (e.g., 'add').

        Returns:
            Operation: An instance of the specified operation class.

        Raises:
            ValueError: If the operation type is unknown.
        """
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()