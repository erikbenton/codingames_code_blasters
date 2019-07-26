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
    # next_checkpoint_dist: distance to the next check point
    # next_checkpoint_angle: angle of pod and next check point
    x, y, next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = [int(i) for i in input().split()]
    opponent_x, opponent_y = [int(i) for i in input().split()]

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)
    thrust = 100;
    bad_angle = False;
    opponent_dist = math.sqrt( (x - opponent_x)**2 + (y - opponent_y)**2 );
    
    # if next_checkpoint_angle < 45 and next_checkpoint_angle > -45:
    #     thrust = 100;
    # elif next_checkpoint_angle > 90 or next_checkpoint_angle < -90:
    #     bad_angle = True;
    #     thrust = 0;
    # else:
    #     thrust = (90 - math.sqrt(next_checkpoint_angle**2))/45;
    #     thrust = int(thrust * 50) + 50;
    
    
    # First see if we are at a bad angle
    # This is 'beyond' the checkpoint, should stop going forward...
    if next_checkpoint_angle > 90 or next_checkpoint_angle < -90:
        bad_angle = True;
        thrust = 0;
    elif next_checkpoint_angle > 75 or next_checkpoint_angle < -75:
        thrust = 90;
    else:
        thrust = 100;
        
    # Then check to see if we are close to the checkpoint
    # and slow down to reduce overshooting
    if next_checkpoint_dist < 300 and not bad_angle:
        thrust = 30;    
    elif next_checkpoint_dist < 1000 and not bad_angle:
        thrust = 75;
        
    if opponent_dist < 400 and thrust > 50:
        thrust = 50;
    
    if next_checkpoint_angle < 10 and next_checkpoint_angle > -10 and next_checkpoint_dist > 4000:
        power = " BOOST";
    else:
        power = " " + str(thrust);
    

    # Edit this line to output the target position
    # and thrust (0 <= thrust <= 100)
    # i.e.: "x y thrust"
    print(str(next_checkpoint_x) + " " + str(next_checkpoint_y) + power)

