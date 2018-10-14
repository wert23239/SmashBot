#!/usr/bin/python3
import melee
import config
import util
import logger
import menuhelper
import objgraph
import argparse
import signal
import sys
import experience_replay

#This example program demonstrates how to use the Melee API to run dolphin programatically,
#   setup controllers, and send button presses over to dolphin

def check_port(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
         raise argparse.ArgumentTypeError("%s is an invalid controller port. \
         Must be 1, 2, 3, or 4." % value)
    return ivalue

chain = None

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--port', '-p', type=check_port,
                    help='The controller port your AI will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=check_port,
                    help='The controller port the opponent will play on',
                    default=1)
parser.add_argument('--live', '-l',
                    help='The opponent is playing live with a GCN Adapter',
                    default=True)
parser.add_argument('--debug', '-d',default=True, action='store_true',
                    help='Debug mode. Creates a CSV of all game state')
parser.add_argument('--framerecord', '-r', default=False, action='store_true',
                    help='(DEVELOPMENT ONLY) Records frame data from the match, stores into framedata.csv.')

args = parser.parse_args()

log = None
if args.debug:
    log = logger.Logger()

framedata = melee.framedata.FrameData(args.framerecord)

#Options here are:
#   "Standard" input is what dolphin calls the type of input that we use
#       for named pipe (bot) input
#   GCN_ADAPTER will use your WiiU adapter for live human-controlled play
#   UNPLUGGED is pretty obvious what it means
opponent_type = melee.enums.ControllerType.STANDARD

#Create our Dolphin object. This will be the primary object that we will interface with
dolphin = melee.dolphin.Dolphin(ai_port=args.port,
                                opponent_port=args.opponent,
                                opponent_type=opponent_type,
                                logger=log)
#Create our GameState object for the dolphin instance
gamestate = melee.gamestate.GameState(dolphin)
#Create our Controller object that we can press buttons on
controller1 = melee.controller.Controller(port=args.port, dolphin=dolphin)
controller2 = melee.controller.Controller(port=args.opponent, dolphin=dolphin)

def signal_handler(signal, frame):
    dolphin.terminate()
    if args.debug:
        log.write_log()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    if args.framerecord:
        framedata.saverecording()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#Run dolphin and render the output
ISO_PATH="/home/fuckme/Desktop/Melee/Smash.iso"
dolphin.run(render=True,iso_path=ISO_PATH)

#Plug our controller in
#   Due to how named pipes work, this has to come AFTER running dolphin
#   NOTE: If you're loading a movie file, don't connect the controller,
#   dolphin will hang waiting for input and never receive it
controller1.connect()
controller2.connect()

supportedcharacters = [melee.enums.Character.PEACH, melee.enums.Character.CPTFALCON, melee.enums.Character.FALCO, \
    melee.enums.Character.FOX, melee.enums.Character.SAMUS, melee.enums.Character.ZELDA, melee.enums.Character.SHEIK, \
    melee.enums.Character.PIKACHU, melee.enums.Character.JIGGLYPUFF, melee.enums.Character.MARTH]


cpu_state=menuhelper.CpuState.UNSET
cpu_char_state=menuhelper.CpuState.UNSET
is_ai=True
is_ai_2=False

if is_ai:
    util1=util.Util(dolphin.logger,
                    controller1,
                    config.Config('current_model',config.ModelType.BINARY))

if is_ai_2:                    
    util2=util.Util(dolphin.logger,
                    controller2,
                    config.Config('model3',config.ModelType.BINARY))

if is_ai==True and is_ai_2==True:
    score1,score2=0,0


data_frame=0
total_data_frames=0
episode_size=1000
buffer=experience_replay.ExperienceReplay(episode_size*10)
#Main loop
while True:
    #"step" to the next frame
    gamestate.step()
    if(gamestate.processingtime * 1000 > 12):
        pass
        #print("WARNING: Last frame took " + str(gamestate.processingtime*1000) + "ms to process.")

    if gamestate.menu_state in [melee.enums.Menu.IN_GAME, melee.enums.Menu.SUDDEN_DEATH]:
        if is_ai:
            util1.do_attack(gamestate,gamestate.ai_state,gamestate.opponent_state) 
        if is_ai_2:    
            util2.do_attack(gamestate,gamestate.opponent_state,gamestate.ai_state)    
            
    #If we're at the character select screen, choose our character
    elif gamestate.menu_state == melee.enums.Menu.CHARACTER_SELECT:
        if is_ai:
            menuhelper.set_ai_character(
                            controller=controller1,
                            character=melee.enums.Character.MARTH,
                            gamestate=gamestate,
                            port=args.port,
                            opponent_port=args.opponent)        
        else:
            cpu_state=menuhelper.set_cpu_character(
                            controller=controller1,
                            character=melee.enums.Character.MARTH,
                            gamestate=gamestate,
                            port=args.port,
                            opponent_port=args.opponent,
                            level=9,
                            cpu_state=cpu_state) 
        if is_ai_2:
            menuhelper.set_ai_character(
                                        controller=controller2,
                                        character=melee.enums.Character.MARTH,
                                        gamestate=gamestate,
                                        port=args.opponent,
                                        opponent_port=args.port)  
        else:                                  
            cpu_char_state=menuhelper.set_cpu_character(
                            controller=controller2,
                            character=melee.enums.Character.MARTH,
                            gamestate=gamestate,
                            port=args.opponent,
                            opponent_port=args.port,
                            level=9,
                            cpu_state=cpu_char_state)                                      
    #If we're at the postgame scores screen, spam START
    elif gamestate.menu_state == melee.enums.Menu.POSTGAME_SCORES:
        melee.menuhelper.skippostgame(controller=controller1)
        melee.menuhelper.skippostgame(controller=controller2)
    #If we're at the stage select screen, choose a stage
    elif gamestate.menu_state == melee.enums.Menu.STAGE_SELECT:
        melee.menuhelper.choosestage(stage=melee.enums.Stage.POKEMON_STADIUM,
                                    gamestate=gamestate,
                                    controller=controller1)
    #Flush any button presses queued up
    controller1.flush()
    controller2.flush()
    if (log and 
        gamestate.menu_state in [melee.enums.Menu.IN_GAME, melee.enums.Menu.SUDDEN_DEATH]):
        log.log_frame(gamestate)
        log.write_frame()
        data_frame+=1
        if data_frame>=episode_size:
            objgraph.show_growth(limit=3)
            log.write_log()
            loss,epsilon,action_size=util1.train(log.rows+buffer.sample(episode_size))
            buffer.extend(log.rows)
            log.rows.clear()
            total_data_frames+=data_frame
            print("Total Frames collected so far:",total_data_frames,"Current Loss",str(loss))
            print("Current Random Rate:", epsilon,"Action Size:", action_size)
            print()
            data_frame=0

            