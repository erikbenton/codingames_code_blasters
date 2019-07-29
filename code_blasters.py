import sys
import math

# This code automatically collects game data in an infinite loop.
# It uses the standard input to place data into the game variables such as x and y.
# YOU DO NOT NEED TO MODIFY THE INITIALIZATION OF THE GAME VARIABLES.

def outside_range(val, lower, upper):
    return val > upper or val < lower;

def inside_range(val, lower, upper):
    return val < upper and val > lower;

# Bools for determining states
first_run = True;
boost_used = False;
shield_used = 0; # Number of turns to wait

# Keeps track of turns for shield
turn_counter = 0;

# States
dist_state = 0; # 0 is Far, 1 is Med, 2 is Close
opponent_state = 0; # 0 is Far, 1 is Close
angle_state = 0; # 0 is Head On, 1 is Close, 2 is Off Target, 3 is Beyond
power_state = 0; # 0 is calc'd thrust, 1 is BOOST, 2 is SHIELD

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
    if first_run == True:
        v_x = 0;
        v_y = 0;
        v_sum = 0;
        v_angle = 0;
        opponent_v_x = 0;
        opponent_v_y = 0;
        opponent_v_sum = 0;
        opponent_v_angle = 0;
    else:
        v_x = x - prev_x;
        v_y = y - prev_y;
        v_sum = math.sqrt( (v_x - prev_v_x)**2 + (v_x - prev_v_x)**2 );
        if v_x == 0: # Check for div by 0
            v_x = 0.0001;
        v_angle =  math.atan(v_y/v_x);
        opponent_v_x = opponent_x - prev_opponent_x;
        opponent_v_y = opponent_y - prev_opponent_y;
        opponent_v_sum = math.sqrt( (opponent_v_x - prev_opponent_v_x)**2 + (v_y - prev_opponent_v_y)**2 );
        if opponent_v_x == 0: # Check for div by 0
            opponent_v_x = 0.0001;
        opponent_v_angle = math.atan(opponent_v_y/opponent_v_x);

    # Calculate opponent distance
    opponent_dist = math.sqrt( (x - opponent_x)**2 + (y - opponent_y)**2 );
    
    # Determine what state the ship is in
    # Distance State
    if next_checkpoint_dist < 150:
        dist_state = 0; # Close
    elif next_checkpoint_dist < 500:
        dist_state = 1; # Almost there
    elif next_checkpoint_dist < 1000:
        dist_state = 2;
    elif next_checkpoint_dist < 2000:
        dist_state = 3;
    else:
        dist_state = 4; # Far away

    # Angle State
    if outside_range(next_checkpoint_angle, -90, 90):
        angle_state = 0; # Beyond
    elif outside_range(next_checkpoint_angle, -75, 75):
        angle_state = 1; # Off Target
    elif outside_range(next_checkpoint_angle, -45, 45):
        angle_state = 2; # Close
    else:
        angle_state = 3; # On Target

    # Opponent state
    if opponent_dist < 400:
        opponent_state = 0; # Hit
    elif opponent_dist < 600:
        opponent_state = 1; # Close by
    else:
        opponent_state = 2; # Not a real problem

    # Now to determine the thrust based on y = m*x + b:

    # Angle towards next checkpoint is next priority
            # Fine-tune scaling (m)
    if angle_state == 3:
        thrust = 100;
    elif angle_state == 2:
        thrust = 90;
    elif angle_state == 1:
        thrust = 70;
    elif angle_state == 0:
        thrust = 0;
    else:
        thrust = 100;

        # Distance to checkpoint is most important
            # Set it's initial offset (b)
    if dist_state == 4:
        thrust = thrust * 100;
    elif dist_state == 3:
        perc = (next_checkpoint_dist - 1000) / (2000 - 1000);
        thrust = thrust * (perc);
    elif dist_state == 2:
        perc = (next_checkpoint_dist - 500) / (1000 - 500);
        thrust = thrust * perc;
    elif dist_state == 1:
        perc = (next_checkpoint_dist - 150) / (500 - 150);
        thrust = thrust * perc;
    elif dist_state == 0:
        perc = (next_checkpoint_dist) / (150);
        thrust = thrust * perc;
    else:
        thrust = thrust;
    
    # Check to see if boost should used
    if first_run:
        power_state = 1;
        boost_used = True;
    elif opponent_state == 1 and shield_used == 0:
        power_state = 0;
        shield_used = 4;
    elif opponent_state == 0 and thrust > 50:
        power_state = 2;
        thrust = 50; 
    else:
        power_state = 2;

    # Make sure that the thrust is below the limit
    if thrust > 100:
        thrust = 100;

    # Decide the power output based on the power state
    if power_state == 2:
        power = " " + str(int(thrust));
    elif power_state == 1:
        power = " BOOST";
    elif power_state == 0:
        power = " SHIELD";
    else:
        power = " " + str(int(thrust));

    # If the shield was used, update
    if shield_used > 0:
        shield_used = shield_used - 1;

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