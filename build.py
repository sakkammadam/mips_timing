import sys
import argparse
import re
from typing import List
from helpers import Instruction
from helpers import offset_capture
from helpers import timing_step
from helpers import gen_pipeline_stages
from helpers import detect_hazards_no_fwd
from helpers import pipeline_modifier


def parse_args(argv=None):
    """
    This function is used to parse runtime arguments
    :param argv:
    :return: argparse object
    """
    parser = argparse.ArgumentParser(description="MIPS Pipeline Hazard Detection and Timing Sequence Generator")
    parser.add_argument(
        "--commands",
        required=True,
        help="Pipe separated list of MIPS commands"
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=["detect", "timing", "both"],
        help="Desired operation - 'detect' would find all hazards; 'timing' would generate a timing diagram\
        'both' would show the hazards and generate a timing diagram"
    )
    parser.add_argument(
        "--forwarding_unit",
        required=True,
        choices=["on", "off"],
        help="Forwarding unit flag. Usage will alter the timing diagram based on presence/absence of forwarding unit."
    )
    return parser.parse_args()


# noinspection DuplicatedCode
def parse_mips_commands(raw_commands: str) -> list:
    """
    This function will be used parse MIPS commands supplied by the user
    :param raw_commands: newline separated commands
    :return: list of parsed commands
    """
    # initialize an empty list
    all_instructions = []
    # initialize a tmp list by splitting the raw commands by '\n'
    tmp = raw_commands.split('|')
    # close out if there was nothing returned!
    if len(tmp) == 0:
        return []
    for item in tmp:
        # tokenize input
        tokens = item.split()
        # capture opcode
        opcode = tokens[0].strip().upper()
        # based on opcode
        if opcode in ["ADD", "SUB"]:
            # Destination Register
            rd = tokens[1].replace(',', '').strip().upper()
            # Source Register - used as Register1 for ADD,SUB
            rs = tokens[2].replace(',', '').strip().upper()
            # Target Register - used as Register1 for ADD,SUB
            rt = tokens[3].replace(',', '').strip().upper()
            # Append to instructions
            all_instructions.append(
                Instruction(opcode=opcode, rd=rd, rs=rs, rt=rt, raw=item)
            )
        elif opcode in ["LW"]:
            # target register
            rt = tokens[1].replace(',', '').strip().upper()
            # source register
            match = re.search(offset_capture, tokens[2].replace(',', '').strip().upper())
            rs = match.group(2)
            offset = match.group(1)
            # Append to instructions
            all_instructions.append(
                Instruction(opcode=opcode, rs=rs, rt=rt, offset=offset, raw=item)
            )
        elif opcode in ["SW"]:
            # source register
            rs = tokens[1].replace(',', '').strip().upper()
            # target register
            match = re.search(offset_capture, tokens[2].replace(',', '').strip().upper())
            rt = match.group(2)
            offset = match.group(1)
            # Append to instructions
            all_instructions.append(
                Instruction(opcode=opcode, rs=rs, rt=rt, offset=offset, raw=item)
            )
        else:
            raise Exception("Opcode {} not supported! Please resubmit")
    return all_instructions


def orchestrate_detection_no_fwd(num: int, item: Instruction, all_instructions: List[Instruction]):
    # initialize message with input command
    msg = item.raw
    tmp1 = ''
    tmp2 = ''
    if num == 0:
        pass
    else:
        prev_instruction_1 = all_instructions[num - 1]
        # potential RAW, WAR or WAW data hazards between {ADD, SUB} and {SUB, ADD}
        tmp1 = detect_hazards_no_fwd(current=item, previous=prev_instruction_1, prev_no=num-1)
        if (num-2) >= 0:
            prev_instruction_2 = all_instructions[num - 2]
            tmp2 = detect_hazards_no_fwd(current=item, previous=prev_instruction_2, prev_no=num-2)
    # create final message
    if tmp1 == '' and tmp2 == '':
        final_msg = msg
    elif tmp1 != '' and tmp2 == '':
        final_msg = msg + ' ------ ' + tmp1
    elif tmp1 == '' and tmp2 != '':
        final_msg = msg + ' ------ ' + tmp2
    else:
        final_msg = msg + ' ------ ' + tmp1 + '\n' + ' '.ljust(15) + '------ ' + tmp2
    # print
    print(final_msg)


def instruction_pipeline(
        fwd_option: str,
        num: int,
        item: Instruction,
        all_instructions: List[Instruction],
        prev_pipe: str = None, adj: int = None
):
    pipeline_stages = gen_pipeline_stages(item=item)
    all_step = '|'
    tmp1 = ''
    tmp2 = ''
    # detect hazards
    if num == 0:
        prev_instruction_1 = None
        prev_instruction_2 = None
    else:
        prev_instruction_1 = all_instructions[num - 1]
        # potential RAW, WAR or WAW data hazards between {ADD, SUB} and {SUB, ADD}
        tmp1 = detect_hazards_no_fwd(current=item, previous=prev_instruction_1, prev_no=num-1)
        if (num-2) >= 0:
            prev_instruction_2 = all_instructions[num - 2]
            tmp2 = detect_hazards_no_fwd(current=item, previous=prev_instruction_2, prev_no=num-2)
        else:
            prev_instruction_2 = None
            tmp2 = ''
    pipeline_modifier(
        fwd_option=fwd_option,
        current=item,
        pipeline_stages=pipeline_stages,
        previous_1=prev_instruction_1,
        hazard_1=tmp1,
        hazard_2=tmp2,
        previous_2=prev_instruction_2
     )
    # introduce pipeline modifier
    base = 8
    for stage in pipeline_stages:
        gen_step = timing_step(stage=stage["short"])
        all_step = all_step + gen_step + '|'
    if prev_pipe is None:
        op = 0
    if adj is None:
        adj = 0
    else:
        if prev_pipe.count('---S---') > 0:
            op = base * prev_pipe.count('---S---')
        else:
            op = adj
    if num == 0:
        print(item.raw.ljust(15) + ' ---> ' + all_step)
    else:
        print(item.raw.ljust(15) + ' ---> ' + ' ' * num * base + ' ' * op + all_step)
    # send it for the next run
    return all_step, op


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    parsed_commands = parse_mips_commands(raw_commands=args.commands)
    tmp = None
    adjust = None
    if args.operation == "detect":
        print("-"*236)
        print("- Detecting data hazards: -")
        print("-"*236)
        for i, ind in enumerate(parsed_commands):
            orchestrate_detection_no_fwd(num=i, item=ind, all_instructions=parsed_commands)
        print("-" * 236)
        # safely exit
        sys.exit(0)
    elif args.operation == "timing":
        print("-"*236)
        print("- Generating Timing Diagram with forwarding unit {}: -".format(args.forwarding_unit.upper()))
        print("-"*236)
        for i, ind in enumerate(parsed_commands):
            tmp, adjust = instruction_pipeline(
                fwd_option=args.forwarding_unit,
                num=i, item=ind, all_instructions=parsed_commands,
                prev_pipe=tmp, adj=adjust)
        print("-" * 236)
        # safely exit
        sys.exit(0)
    elif args.operation == "both":
        print("-"*236)
        print("- Detecting data hazards: -")
        print("-"*236)
        for i, ind in enumerate(parsed_commands):
            orchestrate_detection_no_fwd(num=i, item=ind, all_instructions=parsed_commands)
        print("-"*236)
        print("*" * 236)
        print("-" * 236)
        print("- Generating Timing Diagram with forwarding unit {}: -".format(args.forwarding_unit.upper()))
        print("-"*236)
        for i, ind in enumerate(parsed_commands):
            tmp, adjust = instruction_pipeline(
                fwd_option=args.forwarding_unit,
                num=i, item=ind, all_instructions=parsed_commands,
                prev_pipe=tmp, adj=adjust)
        print("-" * 236)
    else:
        pass

