import melee
from enum import Enum, unique

@unique
class CpuState(Enum):
    UNSET = 0
    IS_CPU = 1
    LEVEL_GRABBED = 2
    LEVEL_TOGGLE = 3
    LEVEL_SET = 4
    CHARACTER_FOUND = 5

def set_ai_character(controller, character, gamestate, port,
                     opponent_port):
    """Set the given controller to the STANDARD state playing as the given character.
    This is to be called repeatedly each frame while in the character selection menu.
    Returns true once it is complete."""
    if gamestate.player[port].controller_status != melee.enums.ControllerStatus.CONTROLLER_HUMAN:
        melee.menuhelper.changecontrollerstatus(
            controller=controller,
            gamestate=gamestate,
            targetport=port,
            port=port,
            status=melee.enums.ControllerStatus.CONTROLLER_HUMAN)
        return False

    if not gamestate.player[port].coin_down or gamestate.player[port].character != character:
        melee.menuhelper.choosecharacter(
            character=character,
            gamestate=gamestate,
            port=port,
            opponent_port=opponent_port,
            controller=controller,
            swag=False,
            start=False)
        return

    press_start(gamestate, controller)

def set_cpu_character(controller, character, gamestate, port,
                      opponent_port, level, cpu_state=CpuState.UNSET):
    """Set the given controller to be a CPU playing as the given character.
    This is to be called repeatedly each frame while in the character selection menu.
    Returns the current state of this command."""
    if cpu_state == CpuState.UNSET:
        if gamestate.player[port].controller_status != melee.enums.ControllerStatus.CONTROLLER_CPU:
            melee.menuhelper.changecontrollerstatus(
                controller=controller,
                gamestate=gamestate,
                targetport=port,
                port=port,
                status=melee.enums.ControllerStatus.CONTROLLER_CPU)
            return CpuState.UNSET
        controller.release_button(melee.enums.Button.BUTTON_A)
        return CpuState.IS_CPU

    if (cpu_state == CpuState.IS_CPU
        or cpu_state == CpuState.LEVEL_GRABBED
        or cpu_state == CpuState.LEVEL_TOGGLE):
        return set_cpu_level(
            controller=controller,
            port=port,
            level=level,
            character_state=gamestate.player[port],
            cpu_state=cpu_state
        )

    if cpu_state == CpuState.LEVEL_SET:
        if (gamestate.player[port].character == character) and gamestate.player[port].coin_down:
            return CpuState.CHARACTER_FOUND
        melee.menuhelper.choosecharacter(
            character=character,
            gamestate=gamestate,
            port=port,
            opponent_port=opponent_port,
            controller=controller,
            swag=False,
            start=False)
        return cpu_state

    if cpu_state == CpuState.CHARACTER_FOUND:
        if gamestate.ready_to_start and \
            not controller.prev.button[melee.enums.Button.BUTTON_START]:
            controller.press_button(melee.enums.Button.BUTTON_START)
            return CpuState.CHARACTER_FOUND
        else:
            controller.empty_input()
            return CpuState.CHARACTER_FOUND

    return cpu_state


def set_cpu_level(controller, port, level, character_state, cpu_state):
    """Set the CPU level. Requires the CPU to currently be at level 1."""
    target_x, target_y = 0, -15
    if port == 1:
        target_x = -31.5
    elif port == 2:
        target_x = -16
    elif port == 3:
        target_x = -0.5
    else:
        target_x = 15
    wiggleroom = 0.25

    new_level_x = target_x + (level - 1)*1.3

    if cpu_state == CpuState.IS_CPU:

        #Move up if we're too low
        if character_state.cursor_y < target_y - wiggleroom:
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, .5, 0.7)
            return cpu_state
        #Move down if we're too high
        if character_state.cursor_y > target_y + wiggleroom:
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, .5, 0.3)
            return cpu_state
        #Move right if we're too left
        if character_state.cursor_x < target_x - wiggleroom:
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.7, .5)
            return cpu_state
        #Move left if we're too right
        if character_state.cursor_x > target_x + wiggleroom:
            controller.tilt_analog(melee.enums.Button.BUTTON_MAIN, 0.3, .5)
            return cpu_state

        controller.press_button(melee.enums.Button.BUTTON_A)
        return CpuState.LEVEL_GRABBED

    if cpu_state == CpuState.LEVEL_TOGGLE:
        x_dir, _ = controller.current.main_stick
        #Move right if we're too left
        if (character_state.cursor_x < new_level_x - wiggleroom
            and x_dir != 0.6):
            controller.simple_press(0.7, .5, melee.enums.Button.BUTTON_A)
            return CpuState.LEVEL_GRABBED
        #Move left if we're too right
        if (character_state.cursor_x > new_level_x + wiggleroom
            and x_dir != 0.4):
            controller.simple_press(0.3, .5, melee.enums.Button.BUTTON_A)
            return CpuState.LEVEL_GRABBED
    if cpu_state == CpuState.LEVEL_GRABBED:
        controller.empty_input()
        return CpuState.LEVEL_TOGGLE

    controller.empty_input()
    return CpuState.LEVEL_SET

def press_start(gamestate, controller):
    if (gamestate.ready_to_start and
            not controller.prev.button[melee.enums.Button.BUTTON_START]):
        controller.press_button(melee.enums.Button.BUTTON_START)
    else:
        controller.empty_input()