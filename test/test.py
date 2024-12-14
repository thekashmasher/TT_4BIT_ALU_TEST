import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
import random

@cocotb.test()
async def test_tt_um_Richard28277(dut):
    # Clock generation
    cocotb.start_soon(Clock(dut.clk, 10, units='ns').start())

    # Initialize Inputs
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.ena.value = 1
    dut.rst_n.value = 0

    # Wait for global reset
    await Timer(50, units='ns')
    dut.rst_n.value = 1

    # Helper function to display results
    def display_result(op_name):
        print(f"{op_name}: result = {dut.uo_out.value}, uio_out = {dut.uio_out.value}")

    # Randomized test function
    async def random_test(opcode, operation_name):
        a = random.randint(0, 15)
        b = random.randint(0, 15)
        dut.ui_in.value = (a << 4) | b  # Combine a and b into ui_in
        dut.uio_in.value = opcode
        await Timer(50, units='ns')
        display_result(f"Random {operation_name}")
        return a, b

    # Test ADD operation
    for _ in range(300):
        a, b = await random_test(0b0000, "ADD")
        assert dut.uo_out.value == (a + b) & 0xF  # Expect result mod 16

    # Test SUB operation
    for _ in range(300):
        a, b = await random_test(0b0001, "SUB")
        assert dut.uo_out.value == (a - b) & 0xF  # Expect result mod 16

    # Test MUL operation
    for _ in range(5):
        a, b = await random_test(0b0010, "MUL")
        assert dut.uo_out.value == (a * b) & 0xFF  # Expect 8-bit result for multiplication

    # Test DIV operation
    for _ in range(300):
        a, b = await random_test(0b0011, "DIV")
        expected_result = ((a % b) << 4) | (a // b) if b != 0 else 0  # Result: remainder + quotient
        assert dut.uo_out.value == expected_result

    # Test AND operation
    for _ in range(300):
        a, b = await random_test(0b0100, "AND")
        assert dut.uo_out.value == (a & b) & 0xF  # Expect 4-bit AND result

    # Test OR operation
    for _ in range(300):
        a, b = await random_test(0b0101, "OR")
        assert dut.uo_out.value == (a | b) & 0xF  # Expect 4-bit OR result

    # Test XOR operation
    for _ in range(300):
        a, b = await random_test(0b0110, "XOR")
        assert dut.uo_out.value == (a ^ b) & 0xF  # Expect 4-bit XOR result

    # Test NOT operation
    for _ in range(300):
        a, _ = await random_test(0b0111, "NOT")  # Only a is used, b is ignored
        assert dut.uo_out.value == (~a & 0xF)  # Expect 4-bit NOT result

    # Test ENC (Encryption) operation
    for _ in range(300):
        a, b = await random_test(0b1000, "ENC")
        expected_result = ((a << 4) | b) ^ 0xAB  # XOR with encryption key
        assert dut.uo_out.value == expected_result

    # Test SLT (Set Less Than) operation
    for _ in range(300):
        a, b = await random_test(0b1001, "SLT")
        expected_result = 1 if a < b else 0
        assert dut.uo_out.value == expected_result

    # Test SEQ (Set Equal) operation
    for _ in range(5):
        a, b = await random_test(0b1010, "SEQ")
        expected_result = 1 if a == b else 0
        assert dut.uo_out.value == expected_result

    # Exhaustive test for SLT (boundary cases)
    dut.ui_in.value = 0b0010_1100  # a = 2, b = 12
    dut.uio_in.value = 0b1001      # opcode = SLT
    await Timer(50, units='ns')
    display_result("SLT (a < b)")
    assert dut.uo_out.value == 0b00000001  # Expect 1 (a is less than b)

    dut.ui_in.value = 0b1010_0011  # a = 10, b = 3
    dut.uio_in.value = 0b1001      # opcode = SLT
    await Timer(50, units='ns')
    display_result("SLT (a > b)")
    assert dut.uo_out.value == 0b00000000  # Expect 0 (a is greater than b)

    # Exhaustive test for SEQ
    dut.ui_in.value = 0b0101_0101  # a = 5, b = 5
    dut.uio_in.value = 0b1010      # opcode = SEQ
    await Timer(50, units='ns')
    display_result("SEQ (a == b)")
    assert dut.uo_out.value == 0b00000001  # Expect 1 (a is equal to b)

    dut.ui_in.value = 0b0010_0101  # a = 2, b = 5
    dut.uio_in.value = 0b1010      # opcode = SEQ
    await Timer(50, units='ns')
    display_result("SEQ (a != b)")
    assert dut.uo_out.value == 0b00000000  # Expect 0 (a is not equal to b)
