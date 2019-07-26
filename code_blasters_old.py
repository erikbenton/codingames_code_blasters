import sys
import math

# This code automatically collects game data in an infinite loop.
# It uses the standard input to place data into the game variables such as x and y.
# YOU DO NOT NEED TO MODIFY THE INITIALIZATION OF THE GAME VARIABLES.


# game loop
while True:
    # x: x position of your pod
    # y: y position of your pod
    # next_checkpoint_x: x position of the next check point
    # next_checkpoint_y: y position of the next check point
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    thrust = 100;
    bad_angle = False;
    
    if next_checkpoint_angle > 90 or next_checkpoint_angle < -90:
        bad_angle = True;
        thrust = 0;
    else:
        bad_angle = False;
        thrust = 100;
        
    if next_checkpoint_dist < 5 and not bad_angle:
        thrust = 5;    
    # elif next_checkpoint_dist < 100 and not bad_angle:
    #     thrust = 25;
    elif next_checkpoint_dist < 250 and not bad_angle:
        thrust = 50;
    elif next_checkpoint_dist < 1000 and not bad_angle:
        thrust = 75;
        
    if next_checkpoint_angle < 10 and next_checkpoint_angle > -10 and next_checkpoint_dist > 4000:
        power = " BOOST";
    else:
        power = " " + str(thrust);
    

    # Edit this line to output the target position
    # and thrust (0 <= thrust <= 100)
    # i.e.: "x y thrust"
    print(str(next_checkpoint_x) + " " + str(next_checkpoint_y) + power)

