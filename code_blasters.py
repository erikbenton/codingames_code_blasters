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

dist_state = 0; # 0 is Far, 1 is Med, 2 is Close
opponent_state = 0; # 0 is Far, 1 is Close

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

angle_state = 0; # 0 is Head On, 1 is Close, 2 is Off Target, 3 is Beyond


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
    
    # Determine what state the ship is in
    # Distance State
    if next_checkpoint_dist < 300:
        dist_state = 2; # Close
    elif next_checkpoint_dist < 1000:
        dist_state = 1; # Almost there
    else
        dist_state = 0; # Far away

    # Angle State
    if outside_range(next_checkpoint_angle, -90, 90):
        angle_state = 3; # Beyond
    elif outside_range(next_checkpoint_angle, -75, 75):
        angle_state = 2;
    elif outside_range(next_checkpoint_angle, -45, 45):
        angle_state = 1;
    else:
        angle_state = 0;

    # Opponent state
    if opponent_dist < 400:
        opponent_state = 2; # Hit
    elif opponent_dist < 600;
        opponent_state = 1; # Close by
    else:
        opponent_state = 0; # Not a real problem
        
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
    prev_v_angle = v_angle;
    prev_checkpoint_angle = next_checkpoint_angle;
    prev_opponent_v_angle = opponent_v_angle;
    
    # No longer the first run
    first_run = False;

def outside_range(val, lower, upper):
    return val > upper or val < lower;

def inside_range(val, lower, upper):
    return val < upper and val > lower;