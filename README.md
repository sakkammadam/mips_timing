
# MIPS Pipeline Hazard Detection and Timing Sequence Generator

This project provides a Python 
script 
for detecting data hazards in MIPS assembly instructions and generating timing diagrams for pipeline stages. The script supports ADD, SUB, LW (load word), and SW (store word) instructions. It can handle both scenarios with and without a forwarding unit, inserting stalls as needed to resolve hazards.

## Features

- **Data Hazard Detection**: Detects RAW (Read After Write), WAR (Write After Read), and WAW (Write After Write) hazards.
- **Timing Diagram Generation**: Generates timing diagrams showing the pipeline stages (Fetch, Decode, Execute, Memory, Write Back).
- **Forwarding Unit Support**: Supports scenarios with and without a forwarding unit, adjusting the timing diagram accordingly.

## Requirements

- Python 3.x

## Usage

### Command-Line Arguments

- `--commands`: Pipe-separated list of MIPS commands.
- `--operation`: Desired operation - `detect` to find all hazards, `timing` to generate a timing diagram, or `both` to show hazards and generate a timing diagram.
- `--forwarding_unit`: `on` to enable the forwarding unit, `off` to disable it.

### Examples

```bash
python build.py --commands "SW R4, 8(R2)|LW R4, 8(R3)" --operation both --forwarding_unit off

python build.py --commands "SW R4, 8(R2)|ADD R0, R7, R1|LW R4, 8(R3)" --operation both --forwarding_unit off
```

Example output with hazards:

```
SW R4, 8(R2)
ADD R0, R7, R1
LW R4, 8(R3) ------ [RAW HAZARD] Instruction [LW R4, 8(R3)] Register Memory Location R4 depends on Instruction#1 Instruction [SW R4, 8(R2)] Destination Register R2
```

### Detailed Example

```bash
python build.py --commands "SUB R0, R1, R2|LW R4, 8(R2)|ADD R0, R1, R4|SW R4, 24(R9)" --operation both --forwarding_unit off
```

Example output with multiple hazards:

```
SUB R0, R1, R2
LW R4, 8(R2)
ADD R0, R1, R4 ------ [RAW HAZARD] Instruction [ADD R0, R1, R4] Register Memory Location R4 depends on Instruction#2 Instruction [LW R4, 8(R2)] Destination Register R4
               ------ [WAW HAZARD] - Same target register R0 used for instructions [ADD R0, R1, R4] and [SUB R0, R1, R2]
SW R4, 24(R9) ------ [RAW HAZARD] Instruction [SW R4, 24(R9)] Register Memory Location R4 depends on Instruction#2 Instruction [LW R4, 8(R2)] Destination Register R4
```

### Usage with Forwarding Unit Enabled

```bash
python build.py --commands "ADD R0, R1, R2|LW R3 0(R1)|SUB R4, R3, R0|LW R5 8(R4)|ADD R6, R7, R8|SUB R1, R2, R3|LW R1, 24(R5)" --operation both --forwarding_unit on
```

## Files

- `build.py`: Main script to detect hazards and generate timing diagrams.
- `helpers.py`: Helper functions and classes used by `build.py`.
- `demo_use.txt`: Example usage of the script.

## Example Usage

To detect hazards and generate a timing diagram for a sequence of MIPS instructions:

```bash
python build.py --commands "ADD R0, R1, R2|LW R3 0(R1)|SUB R4, R3, R0|LW R5 8(R4)|ADD R6, R7, R8" --operation both --forwarding_unit off
```

To generate a timing diagram with a forwarding unit:

```bash
python build.py --commands "ADD R0, R1, R2|LW R3 0(R1)|SUB R4, R3, R0|LW R5 8(R4)|ADD R6, R7, R8|SUB R1, R2, R3|LW R1, 24(R5)" --operation both --forwarding_unit on
```

## Sample Outputs

    python .\build.py --commands "SW R4, 8(R2)|LW R4, 8(R3)" --operation both --forwarding_unit off

![detect_timing_no_fwding_SW_LW.png](images%2Fdetect_timing_no_fwding_SW_LW.png)

    python .\build.py --commands "SW R4, 8(R2)|ADD R0, R7, R1|LW R4, 8(R3)" --operation both --forwarding_unit off

![detect_timing_no_fwding_SW_ADD_LW.png](images%2Fdetect_timing_no_fwding_SW_ADD_LW.png)

    python .\build.py --commands "SUB R0, R1, R2|LW R4, 8(R2)|ADD R0, R1, R4|SW R4, 24(R9)" --operation both --forwarding_unit off

![detect_timing_no_fwding_SUB_LW_ADD_SW.png](images%2Fdetect_timing_no_fwding_SUB_LW_ADD_SW.png)

    python .\build.py --commands "ADD R9, R2, R7|ADD R0, R1, R4|SW R4, 24(R9)|LW R9, 0(R5)" --operation both --forwarding_unit off

![detect_timing_no_fwding_ADD_ADD_SW_LW.png](images%2Fdetect_timing_no_fwding_ADD_ADD_SW_LW.png)

    python .\build.py --commands "ADD R0, R1, R2|LW R3 0(R1)|SUB R4, R3, R0|LW R5 8(R4)|ADD R6, R7, R8" --operation both --forwarding_unit off

![detect_timing_no_fwding_ADD_LW_SUB_LW_ADD.png](images%2Fdetect_timing_no_fwding_ADD_LW_SUB_LW_ADD.png)

    python .\build.py --commands "ADD R0, R1, R2|LW R3 0(R1)|SUB R4, R3, R0|LW R5 8(R4)|ADD R6, R7, R8|SUB R1, R2, R3|LW R1, 24(R5)" --operation both --forwarding_unit off

![detect_timing_no_fwding_ADD_LW_SUB_LW_ADD_SUB_LW.png](images%2Fdetect_timing_no_fwding_ADD_LW_SUB_LW_ADD_SUB_LW.png)

    python .\build.py --commands "ADD R0, R1, R2|LW R3 0(R1)|SUB R4, R3, R0|LW R5 8(R4)|ADD R6, R7, R8|SUB R1, R2, R3|LW R1, 24(R5)" --operation both --forwarding_unit on

![detect_timing_fwding_ADD_LW_SUB_LW_ADD_SUB_LW.png](images%2Fdetect_timing_fwding_ADD_LW_SUB_LW_ADD_SUB_LW.png)

## License

This project is licensed under the MIT License. See the LICENSE file for details.
