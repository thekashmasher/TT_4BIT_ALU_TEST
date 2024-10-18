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

    # Helper function to perform operations
    def alu_model(a, b, opcode):
        try:
            if opcode == 0:  # ADD
                return (a + b) & 0xF, 0
            elif opcode == 1:  # SUB
                return (a - b) & 0xF, 0
            elif opcode == 2:  # MUL
                return (a * b) & 0xF, 0
            elif opcode == 3:  # DIV
                return (a // b) if b != 0 else 0, 0
            elif opcode == 4:  # AND
                return a & b, 0
            elif opcode == 5:  # OR
                return a | b, 0
            elif opcode == 6:  # XOR
                return a ^ b, 0
            elif opcode == 7:  # NOT
                return ~a & 0xF, 0
            elif opcode == 8:  # ENC (Encryption mock with key 0xAB)
                return (a ^ 0xAB) & 0xF, 0
            else:
                raise ValueError(f"Invalid opcode: {opcode}")
        except Exception as e:
            print(f"Error in alu_model: {e}")
            return 0, 0

    # Run 1000 random test cases
    for test_num in range(1000):
        # Generate random inputs and operation
        a = random.randint(0, 15)  # 4-bit random number
        b = random.randint(0, 15)  # 4-bit random number
        opcode = random.randint(0, 8)  # Random operation

        # Pack inputs into ui_in and set opcode
        dut.ui_in.value = (a << 4) | b  # Pack a and b into ui_in
        dut.uio_in.value = opcode  # Set the opcode

        # Wait for the operation to complete
        await Timer(50, units='ns')

        # Get expected result from the model
        expected_result, _ = alu_model(a, b, opcode)

        try:
            # Assert that the result matches the expected result
            assert dut.uo_out.value == expected_result, (
                f"Test {test_num} failed: a={a}, b={b}, opcode={opcode}. "
                f"Expected={expected_result}, Got={dut.uo_out.value}"
            )
        except AssertionError as error:
            # Print out any assertion errors during the test
            print(error)
            raise

    # Final success message
    print("1000 random ALU test cases passed successfully!")
