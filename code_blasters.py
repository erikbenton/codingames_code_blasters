import sys
import math

# This code automatically collects game data in an infinite loop.
# It uses the standard input to place data into the game variables such as x and y.
# YOU DO NOT NEED TO MODIFY THE INITIALIZATION OF THE GAME VARIABLES.

first_run = True;

# Position
prev_x = 0;
prev_y = 0;

prev_opponent_x = 0;
prev_opponent_y = 0;

prev_checkpoint_x = 0;
prev_checkpoint_y = 0;

# Distances
prev_checkpoint_dist = 0;
prev_opponent_dist = 0;

# Velocities
prev_v_x = 0;
prev_v_y = 0;
prev_v_sum = 0;

prev_opponent_v_x = 0;
prev_opponent_v_y = 0;
prev_opponent_v_sum = 0;

# Angles
prev_v_angle = 0;
prev_opponent_v_angle = 0;
prev_checkpoint_angle = 0;

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

    # Calculate the velocities
    if first_run is True:
        v_x = 0;
        v_y = 0;
        v_sum = 0;
        v_angle = 0;
        opponent_v_x = 0;
        opponent_v_y = 0;
        opponent_v_sum = 0;
    else:
        v_x = x - prev_x;
        v_y = y - prev_y;
        v_sum = math.sqrt( (v_x - prev_v_x)**2 + (v_x - prev_v_x)**2 );
        v_angle = math.arctan(v_y/v_x);
        opponent_v_x = opponent_x - prev_opponent_x;
        opponent_v_y = opponent_y - prev_opponent_y;
        opponent_v_sum = math.sqrt( (opponent_v_x - prev_opponent_v_x)**2 + (v_x - prev_opponent_v_x)**2 );;
        opponent_v_angle = math.arctan(opponent_v_y/opponent_v_x);

    # Calculate opponent distance
    opponent_dist = math.sqrt( (x - opponent_x)**2 + (y - opponent_y)**2 );
    
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

    # Remember the previous state
    # Positions
    prev_x = x;
    prev_y = y;
    
    prev_opponent_x = opponent_x;
    prev_opponent_y = opponent_y;
    
    prev_checkpoint_x = next_checkpoint_x;
    prev_checkpoint_y = next_checkpoint_y;
    
    # Distances
    prev_checkpoint_dist = next_checkpoint_dist;
    prev_opponent_dist = opponent_dist;
    
    # Velocities
    prev_v_x = v_x;
    prev_v_y = v_y;
    prev_v_sum = v_sum;
    
    prev_opponent_v_x = opponent_v_x;
    prev_opponent_v_y = opponent_v_y;
    prev_opponent_v_sum = opponent_v_sum;
    
    # Angles
    prev_checkpoint_angle = next_checkpoint_angle;
    prev_v_angle = v_angle;
    prev_opponent_v_angle = opponent_v_angle;
    
    # No longer the first run
    first_run = False;

def determine