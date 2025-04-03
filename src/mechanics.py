# mechanics.py

import src.config as c

def coyote_ground_frames_for(game, which_type: str) -> int:
    if which_type == 'charged':
        return game.coyote_frames_charged
    return game.coyote_frames_instant

def set_coyote_ground_frames(game, which_type: str, value: int) -> None:
    if which_type == 'charged':
        game.coyote_frames_charged = value
    else:
        game.coyote_frames_instant = value

def dec_coyote_ground_frames(game, which_type: str) -> None:
    if which_type == 'charged':
        if game.coyote_frames_charged > 0:
            game.coyote_frames_charged -= 1
    else:
        if game.coyote_frames_instant > 0:
            game.coyote_frames_instant -= 1

def jump_buffer_frames_for(game, which_type: str) -> int:
    if which_type == 'charged':
        return game.jump_buffer_frames_charged
    return game.jump_buffer_frames_instant

def set_jump_buffer_frames(game, which_type: str, value: int) -> None:
    if which_type == 'charged':
        game.jump_buffer_frames_charged = value
    else:
        game.jump_buffer_frames_instant = value

def handle_charged_jump_press(game) -> None:
    # If we still have "coyote" ground frames left, begin charging
    if coyote_ground_frames_for(game, 'charged') > 0:
        game.player.charging = True
        game.player.jump_charge = c.MIN_JUMP_STRENGTH
        set_jump_buffer_frames(game, 'charged', 0)
    else:
        # store the jump input for a few frames
        set_jump_buffer_frames(game, 'charged', c.JUMP_BUFFER_FRAMES)

def handle_charged_jump_release(game) -> None:
    if game.player.charging:
        if game.player.on_ground:
            game.player.vel_y = -game.player.jump_charge
            game.boing_sound.play()
        game.player.charging = False
        game.player.jump_charge = 0

def handle_instant_jump(game) -> None:
    if coyote_ground_frames_for(game, 'instant') > 0:
        game.player.vel_y = -c.MIN_JUMP_STRENGTH
        game.boing_sound.play()
        set_jump_buffer_frames(game, 'instant', 0)
    else:
        # mid-air, possibly double jump
        if not game.player.on_ground and game.player.can_double_jump:
            game.player.vel_y = -c.MIN_JUMP_STRENGTH
            game.player.can_double_jump = False
            game.boing_sound.play()
        else:
            set_jump_buffer_frames(game, 'instant', c.JUMP_BUFFER_FRAMES)
