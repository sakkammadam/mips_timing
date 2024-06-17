import os
from math import floor
from dataclasses import dataclass

# Establish width to print outputs to screen - used for printing timing diagram
width = os.get_terminal_size().columns
# length of each pipeline section
dash_length = floor(width / 31)
# Regex pattern
offset_capture = "(.*)\((.*)\)"


# Define a data class around Instruction
@dataclass
class Instruction:
    # Opcode- ADD/SUB/LW/SW
    opcode: str
    # Destination Register (ADD/SUB) only
    rd: str = None
    # Source Register (LW/SW) - Register #1 (ADD/SUB)
    rs: str = None
    # Target Register (LW/SW) - Register #2 (ADD/SUB)
    rt: str = None
    # offset
    offset: str = None
    # memory address
    address: str = None
    # raw original instruction
    raw: str = None


stall_stage = {
    "long": "Stall",
    "short": "S",
    "description": "Stall instruction"
}


def gen_pipeline_stages(item: Instruction) -> list:
    pipeline_stages = [
        {  # 0
            "long": "Fetch",
            "short": "F",
            "description": "Fetch instruction - {}".format(item.raw)
        },
        {  # 1
            "long": "Decode",
            "short": "D",
            "description": "Decode instruction - {} and register contents - {}".format(
                item.opcode, present_values(step='M', item=item))
        },
        {  # 2
            "long": "Execute",
            "short": "X",
            "description": "Execute instruction - {}".format(item.opcode)
        },
        {  # 3
            "long": "Memory",
            "short": "M",
            "description": "Memory operations - {}".format(present_values(step='M', item=item))
        },
        {  # 4
            "long": "Write Back",
            "short": "W",
            "description": "Write back operations - {}".format(present_values(step='W', item=item))
        },
    ]
    return pipeline_stages


def val_checker(input_value):
    """
    If none, return an empty string
    :param input_value:
    :return:
    """
    if input_value is None:
        return ''
    else:
        return str(input_value)


def present_values(step: str, item: Instruction) -> str:
    """
    Helper function used to present values for instruction_pipeline function
    :param step: Pipeline Step
    :param item: Instruction
    :return: str
    """
    if step == "D":
        if item.opcode in ["LW", "SW"]:
            return val_checker(item.rs) + ',' + val_checker(item.rt)
        elif item.opcode in ["ADD", "SUB"]:
            return val_checker(item.rs) + ',' + val_checker(item.rt) + ',' + val_checker(item.rd)
        else:
            return ''
    elif step == "M":
        if item.opcode in ["LW"]:
            return "Value of effective address - {} and offset {} is read".format(item.rs, item.offset)
        elif item.opcode in ["SW"]:
            return "Value of Register {} is written to effective address- {} and offset {}".format(
                item.rs, item.rt, item.offset)
        else:
            return ''
    elif step == "W":
        if item.opcode in ["LW"]:
            return "Value of effective address - {} and offset {} is written to {}".format(
                item.rs, item.offset, item.rt)
        elif item.opcode in ["SW"]:
            return "Nothing to write back!"
        else:
            return ''
    else:
        return ''


def timing_step(stage: str) -> str:
    """
    This function will be used to print the timing step for a given stage
    :param stage:
    :return:
    """
    step = (('-' * dash_length)[0:3] + stage + ('-' * dash_length)[4:7])
    return step


def timing_sequence(step: str) -> None:
    """
    Timing Sequence
    :param step:
    :return:
    """
    pattern = '|' + ((('-' * dash_length)[0:7] + step + ('-' * dash_length)[8:15]) + '|') * 11
    print(pattern)


def detect_hazards_no_fwd(current: Instruction, previous: Instruction, prev_no: int) -> str:
    """
    Used to detect hazards for add and sub operations with no forwarding unit!
    :param prev_no:
    :param current:
    :param previous:
    :return: str
    """
    if current.opcode in ["ADD", "SUB"] and previous.opcode in ["ADD", "SUB"]:
        if current.rd == previous.rs:
            tmp = ("[WAR HAZARD] Instruction [{}] Destination Register {} depends on Instruction#{} [{}] "
                   "Input Register {}").format(
                current.raw, current.rd, prev_no + 1, previous.raw, previous.rs)
        elif current.rd == previous.rt:
            tmp = ("[WAR HAZARD] Instruction [{}] Destination Register {} depends on Instruction#{} [{}] "
                   "Input Register {}").format(
                current.raw, current.rd, prev_no + 1, previous.raw, previous.rt)
        # RAW hazard
        elif current.rs == previous.rd:
            tmp = ("[RAW HAZARD] Instruction [{}] Input Register {} depends on Instruction#{} [{}] "
                   "Destination Register {}").format(
                current.raw, current.rs, prev_no + 1, previous.raw, previous.rd)
        elif current.rt == previous.rd:
            tmp = ("[RAW HAZARD] Instruction [{}] Input Register {} depends on Instruction#{} [{}] "
                   "Destination Register {}").format(
                current.raw, current.rt, prev_no + 1, previous.raw, previous.rd)
        # WAW hazard
        elif current.rd == previous.rd:
            tmp = "[WAW HAZARD] - Same target register {} used for instructions [{}] and [{}]".format(
                current.rd, current.raw, previous.raw)
        else:
            tmp = ''
        return tmp
    if current.opcode in ["SW"] and previous.opcode in ["LW"]:
        # RAW hazard
        if current.rs == previous.rt:
            tmp = ("[RAW HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rs, prev_no + 1, previous.raw, previous.rt)
        else:
            tmp = ''
        return tmp
    if current.opcode in ["LW"] and previous.opcode in ["SW"]:
        # WAR hazard
        if current.rt == previous.rt:
            tmp = ("[WAR HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rt, prev_no + 1, previous.raw, previous.rt)
        # RAW hazard
        elif current.rt == previous.rs:
            tmp = ("[RAW HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rt, prev_no + 1, previous.raw, previous.rt)
        else:
            tmp = ''
        return tmp
    if current.opcode in ["LW"] and previous.opcode in ["LW"]:
        # WAR hazard
        if current.rt == previous.rt:
            tmp = ("[WAW HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rt, prev_no + 1, previous.raw, previous.rt)
        else:
            tmp = ''
        return tmp
    if current.opcode in ["LW"] and previous.opcode in ["ADD", "SUB"]:
        # WAW hazard
        if current.rt == previous.rd:
            tmp = ("[WAW HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rt, prev_no + 1, previous.raw, previous.rd)
        elif current.rt == previous.rs:
            tmp = (
                "[WAR HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                "{}]"
                " Destination Register {}").format(
                current.raw, current.rt, prev_no + 1, previous.raw, previous.rs)
        elif current.rt == previous.rt:
            tmp = (
                "[WAR HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                "{}]"
                " Destination Register {}").format(
                current.raw, current.rt, prev_no + 1, previous.raw, previous.rt)
        else:
            tmp = ''
        return tmp
    if current.opcode in ["SW"] and previous.opcode in ["ADD", "SUB"]:
        # WAR hazard
        if current.rs == previous.rd:
            tmp = ("[RAW HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rs, prev_no + 1, previous.raw, previous.rd)
        else:
            tmp = ''
        return tmp
    if current.opcode in ["ADD", "SUB"] and previous.opcode == "LW":
        if current.rs == previous.rt:
            tmp = ("[RAW HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rs, prev_no + 1, previous.raw, previous.rt)
        elif current.rt == previous.rt:
            tmp = ("[RAW HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rt, prev_no + 1, previous.raw, previous.rt)
        elif current.rd == previous.rt:
            tmp = ("[WAW HAZARD] Instruction [{}] Register Memory Location {} depends on Instruction#{} Instruction ["
                   "{}]"
                   " Destination Register {}").format(
                current.raw, current.rd, prev_no + 1, previous.raw, previous.rt)
        else:
            tmp = ''
        return tmp
    else:
        return ''


def stall_helper_no_fwd(current: Instruction, previous: Instruction, hazard: str, pipeline_stages: list, run: int):
    if hazard.find("WAR HAZARD") > 0:
        # this is applicable only for LW and SW
        if current.opcode == "LW" and previous.opcode == "SW":
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        # this is applicable only ADD,SUB and ADD/SUB - won't be present if forwarding unit present
        if current.opcode in ["ADD", "SUB"] and previous.opcode in ["ADD", "SUB"]:
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        # this is applicable only LW and ADD/SUB
        if current.opcode in ["LW"] and previous.opcode in ["ADD", "SUB"]:
            # insert a single stage ** with forwarding only 1 stall ** if hazard_2 with forwarding no stall
            pipeline_stages.insert(1, stall_stage)
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
    elif hazard.find("RAW HAZARD") > 0:
        # this is applicable only ADD,SUB and ADD/SUB - won't be present if forwarding unit present
        if current.opcode in ["ADD", "SUB"] and previous.opcode in ["ADD", "SUB"]:
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        # this is applicable only for LW and SW
        if current.opcode == "LW" and previous.opcode == "SW" and run == 1:
            # only for just previous step
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        if current.opcode == "SW" and previous.opcode == "LW" and run == 1:
            # only for just previous step
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        if current.opcode == "SW" and previous.opcode in ["ADD", "SUB"]:
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        if current.opcode in ["ADD", "SUB"] and previous.opcode == "LW":
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
    elif hazard.find("WAW HAZARD") > 0:
        # this is applicable only ADD,SUB and ADD/SUB - won't be present if forwarding unit present
        if current.opcode in ["ADD", "SUB"] and previous.opcode in ["ADD", "SUB"]:
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        # this is applicable only for LW and SW
        if current.opcode == "LW" and previous.opcode == "LW":
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        # this is applicable only for LW and SW
        if current.opcode == "LW" and previous.opcode in ["ADD", "SUB"]:
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
        if current.opcode in ["ADD", "SUB"] and previous.opcode == "LW":
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)


def stall_helper_fwd(current: Instruction, previous: Instruction, hazard: str, pipeline_stages: list, run: int):
    if hazard.find("WAR HAZARD") > 0:
        # this is applicable only for LW and SW
        if current.opcode == "LW" and previous.opcode == "SW" and run == 1:
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
    elif hazard.find("RAW HAZARD") > 0:
        if current.opcode in ["ADD", "SUB"] and previous.opcode == "LW" and run == 1:
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)
    elif hazard.find("WAW HAZARD") > 0:
        # this is applicable only for LW and SW
        if current.opcode == "LW" and previous.opcode == "LW" and run == 1:
            # insert a single stage
            pipeline_stages.insert(1, stall_stage)


def pipeline_modifier(
        fwd_option: str,
        current: Instruction,
        pipeline_stages: list,
        previous_1: Instruction,
        hazard_1: str = None,
        hazard_2: str = None,
        previous_2: Instruction = None,
):
    if fwd_option == "off":
        if hazard_2 != '':
            stall_helper_no_fwd(current=current, previous=previous_2,
                                hazard=hazard_2, pipeline_stages=pipeline_stages, run=2)
        elif hazard_1 != '':
            stall_helper_no_fwd(current=current, previous=previous_1,
                                hazard=hazard_1, pipeline_stages=pipeline_stages, run=1)
        else:
            pass
    if fwd_option == "on":
        if hazard_2 != '':
            stall_helper_fwd(current=current, previous=previous_2,
                             hazard=hazard_2, pipeline_stages=pipeline_stages, run=2)
        elif hazard_1 != '':
            stall_helper_fwd(current=current, previous=previous_1,
                             hazard=hazard_1, pipeline_stages=pipeline_stages, run=1)
        else:
            pass
