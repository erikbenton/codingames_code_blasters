import sys
import math
import numpy as np


class Pod:

    def __init__(self, attitude):

        # X components
        # Current
        self.x = 0
        self.vx = 0
        self.ax = 0

        # Desired
        self.x_d = 0
        self.vx_d = 0
        self.ax_d = 0
        self.desired_x = 0

        # Commanded
        self.x_cmd = 0
        self.vx_cmd = 0
        self.ax_cmd = 0

        # Y components
        # Current
        self.y = 0
        self.vy = 0
        self.ay = 0

        # Desired
        self.y_d = 0
        self.vy_d = 0
        self.ay_d = 0
        self.desired_y = 0

        # Commanded
        self.y_cmd = 0
        self.vy_cmd = 0
        self.ay_cmd = 0

        # Force components of the Pod
        self.theta_Fp = 0
        self.mag_Fp = 0

        # Force components for desired Pod force
        self.theta_Fd = 0
        self.mag_Fd = 0

        # Force components for commanded Pod force
        self.theta_Fcmd = 0
        self.mag_Fcmd = 0

        # Components for targets
        self.targets_x = []
        self.targets_y = []
        self.current_target_id = 0
        self.next_target_id = 0
        self.current_target = [0, 0]
        self.next_target = [0, 0]
        self.number_laps = 0

        # Angle
        self.angle = 0
        self.theta_d = 0
        self.theta_d_next = 0
        self.theta_v = 0

        # Overalls
        self.distance = 0
        self.thrust = 0
        self.power = "0"
        self.thrust_d = 0
        self.x_out = 0
        self.y_out = 0
        self.num_turns = 0
        self.personality = attitude
        self.v_mag = 0;
        self.boost_used = False
        self.turns_for_boost = 0

        # For pre-emptive turning
        self.turning_theta = 0
        self.facing_theta = 0;
        self.turns_next_target = 0
        self.turns_hit_target = 0
        self.rotation_limit = math.radians(18);

        # Prev Values
        self.x_prev = 0
        self.vx_prev = 0
        self.ax_prev = 0

        self.x_d_prev = 0
        self.vx_d_prev = 0
        self.ax_d_prev = 0

        self.y_prev = 0
        self.vy_prev = 0
        self.ay_prev = 0

        self.y_d_prev = 0
        self.vy_d_prev = 0
        self.ay_d_prev = 0

        self.theta_Fp_prev = 0
        self.mag_Fp_prev = 0

        self.theta_Fd_prev = 0
        self.mag_Fd_prev = 0

        self.theta_Fcmd_prev = 0
        self.mag_Fcmd_prev = 0

        self.angle_prev = 0
        self.theta_d_prev = 0
        self.thrust_d_prev = 0
        self.theta_v_prev = 0

        self.distance_prev = 0
        self.thrust_prev = 0
        self.power_prev = "0"
        self.x_out_prev = 0
        self.y_out_prev = 0
        self.v_mag_prev = 0;

    def calc_vector_mag(self, vect_x, vect_y):
        return math.sqrt(vect_x ** 2 + vect_y ** 2)

    def calc_vector_theta(self, vect_x, vect_y):

        # if x == 0 or y == 0:
        #     return 0;

        return math.atan2(vect_y, vect_x)

    def update_pod(self, pod_input_list):
        self.num_turns = self.num_turns + 1
        if self.personality == 0:
            self.update_pod_racer(pod_input_list)
        elif self.personality == 1:
            self.update_pod_defender(pod_input_list)

    def update_pod_racer(self, inputs):

        # Update the prev values
        self.update_prevs()

        # Read in new inputs
        self.new_inputs(inputs)

        # First figure out what's happening with the pod
        # Calc what wasn't given
        self.update_velocity()
        self.update_accelerations()
        self.update_Fp()

        # Now figure out where target is and how to get there
        # First find target
        self.update_target_positions()

        # Then orient to the target
        self.update_target_locations()

        # Determine the desired thrust
        self.calc_desired_thrust()
        self.calc_desired_accelerations()

        # Determine what new inputs would make current course the desired course
        self.calc_desired_outputs()

    def update_pod_defender(self, inputs):

        # Update the prev values
        self.update_prevs()

        # Read in new inputs
        self.new_inputs_defender(inputs)

        # First figure out what's happening with the pod
        # Calc what wasn't given
        self.update_accelerations()
        self.update_Fp()

        # Now figure out where target is and how to get there
        # First find target
        self.update_target_positions()

        # Then orient to the target
        self.update_target_locations()

        # Determine the desired thrust
        self.calc_desired_thrust_defender()
        self.calc_desired_accelerations()

        # Determine what new inputs would make current course the desired course
        self.calc_desired_outputs()

    def update_prevs(self):
        self.x_prev = self.x
        self.vx_prev = self.vx
        self.ax_prev = self.ax

        self.x_d_prev = self.x_d
        self.vx_d_prev = self.vx_d
        self.ax_d_prev = self.ax_d

        self.y_prev = self.y
        self.vy_prev = self.vy
        self.ay_prev = self.ay

        self.y_d_prev = self.y_d
        self.vy_d_prev = self.vy_d
        self.ay_d_prev = self.ay_d

        self.theta_Fp_prev = self.theta_Fp
        self.mag_Fp_prev = self.mag_Fp

        self.theta_Fd_prev = self.theta_Fd
        self.mag_Fd_prev = self.mag_Fd

        self.theta_Fcmd_prev = self.theta_Fcmd
        self.mag_Fcmd_prev = self.mag_Fcmd

        self.angle_prev = self.angle
        self.theta_d_prev = self.theta_d

        self.distance_prev = self.distance
        self.thrust_prev = self.thrust
        self.power_prev = self.power
        self.thrust_d_prev = self.thrust_d
        self.thrust_v_prev = self.theta_v
        self.v_mag_prev = self.v_mag

    def new_inputs(self, input_list):
        x_ind = 0
        y_ind = 1
        vx_ind = 2
        vy_ind = 3
        ang_ind = 4
        id_ind = 5

        self.x = input_list[x_ind]
        self.y = input_list[y_ind]
        self.vx = input_list[vx_ind]
        self.vy = input_list[vy_ind]
        self.angle = input_list[ang_ind]
        self.current_target_id = input_list[id_ind]
        self.next_target_id = (self.current_target_id + 1) % int(len(self.targets_x))

    def new_inputs_defender(self, input_list):
        x_ind = 0
        y_ind = 1
        vx_ind = 2
        vy_ind = 3
        ang_ind = 4
        id_ind = 5

        self.x = input_list[x_ind]
        self.y = input_list[y_ind]
        self.vx = input_list[vx_ind]
        self.vy = input_list[vy_ind]
        self.angle = input_list[ang_ind]
        self.current_target_id = int(len(self.targets_x) - 1)
        self.next_target_id = int(len(self.targets_x) - 1)

        print("DFNDR: " + str(input_list[-1]) + ", " + str(self.next_target_id), file=sys.stderr)

    def update_target_positions(self):
        self.current_target[0] = self.targets_x[self.current_target_id]
        self.current_target[1] = self.targets_y[self.current_target_id]

        self.next_target[0] = self.targets_x[self.next_target_id]
        self.next_target[1] = self.targets_y[self.next_target_id]

    def update_target_locations(self):
        x_diff = self.current_target[0] - self.x
        y_diff = self.current_target[1] - self.y
        self.distance = self.calc_vector_mag(x_diff, y_diff)
        self.theta_d = self.calc_vector_theta(x_diff, y_diff)

    def calc_desired_thrust(self):
        far_away = 2000
        scale_factor = 100 / math.pi  # 200/math.pi;
        stretch_factor = 0.002
        approach_dist = 1200  # 100;
        base = 55

        if self.distance > far_away:
            self.thrust_d = 100
        elif self.distance > approach_dist:
            self.thrust_d = (100 * (self.distance / (far_away - approach_dist)) - base) + base
            # scale_factor * math.atan(stretch_factor*(self.distance - approach_dist)) + base;
            print("THRUST: " + str(self.distance) + ", " + str(self.thrust_d), file=sys.stderr)
            # self.thrust_d = scale_factor * math.atan(stretch_factor*(self.distance - approach_dist)) + base;
        else:
            self.thrust_d = base

    def calc_desired_thrust_defender(self):
        far_away = 2000
        scale_factor = 100 / math.pi  # 200/math.pi;
        stretch_factor = 0.002
        approach_dist = 300  # 100;
        base = 55

        if self.distance > far_away:
            self.thrust_d = 100
        elif self.distance > approach_dist:
            self.thrust_d = 75
        else:
            self.thrust_d = base

    def calc_desired_accelerations(self):
        self.ax_d = self.thrust_d * math.cos(self.theta_d)
        self.ay_d = self.thrust_d * math.sin(self.theta_d)

    def calc_desired_outputs(self):

        # if self.distance > 1000:
        #     # Momentum control
        #     self.x_out = self.x + self.current_target[0] - self.x - self.vx;
        #     self.y_out = self.y + self.current_target[1] - self.y - self.vy;

        #     # Force control
        #     # self.x_out = self.x + self.ax_d - self.ax;
        #     # self.y_out = self.y + self.ay_d - self.ay;
        # else:
        #     self.x_out = self.current_target[0];
        #     self.y_out = self.current_target[1];
        self.calc_next_x_y(self.current_target[0], self.current_target[1])
        self.x_out = self.x + self.desired_x - self.x - self.vx
        self.y_out = self.y + self.desired_y - self.y - self.vy
        # self.x_out = self.x + self.current_target[0] - self.x - self.vx
        # self.y_out = self.y + self.current_target[1] - self.y - self.vy
        self.thrust = self.calc_vector_mag(self.ax_d, self.ay_d)

        # Preemptive Turning for next checkpoint
        # Check to see if pod is close and on target
        # print_text = str(self.distance)
        # print_text = print_text + ", " + str(self.check_on_target())
        # print_text = print_text + ", " + str(self.v_mag)
        # print_text = print_text + ", " + str(self.turning_theta)
        # print("NEXT: " + print_text, file=sys.stderr)
        
        if self.check_on_target():
            self.calc_next_target_theta()
            self.turns_next_target = self.turning_theta/self.rotation_limit;
            if self.v_mag != 0: # Check for div by 0
                self.turns_hit_target = self.distance/self.v_mag
            else:
                self.turns_hit_target = 500

            if (self.turns_hit_target - self.turns_next_target) < 3:
                self.calc_next_x_y(self.next_target[0], self.next_target[1])
                self.x_out = self.desired_x
                self.y_out = self.desired_y
                # self.x_out = int(self.next_target[0])
                # self.y_out = int(self.next_target[1])
                # if self.boost_used == False:
                #     self.boost_used = True
                # else:
                #     if self.turns_for_boost > 0:
                #         self
                self.thrust_d = self.thrust_d * 0.25
                print("YAY!", file=sys.stderr)

        # if self.distance < 2000 and self.check_on_target() and self.calc_vector_mag(self.vx, self.vy) > 100:
        #     self.x_out = int(self.targets_x[self.next_target_id])
        #     self.y_out = int(self.targets_y[self.next_target_id])
        #     self.thrust_d = 0
        #     print("YAY!", file=sys.stderr)

        # Check to see if pod is close and on target
        # print_text = str(self.distance)
        # print_text = print_text + ", " + str(self.check_on_target())
        # print_text = print_text + ", " + str(self.v_mag)
        # print_text = print_text + ", " + str(math.degrees(self.turning_theta - self.rotation_limit))
        # print("NEXT: " + print_text, file=sys.stderr)

        if self.thrust_d > 100:
            self.thrust_d = 100

        # If we aren't able to move towards the target
        if (self.turning_theta - self.rotation_limit) > math.radians(90):
            # Figure out angle displacement from the next target
            self.calc_facing_theta()

            # If we are far away
            if self.distance > 2000:
                # And we aren't facing in the right direction
                if self.facing_theta > self.rotation_limit:
                    # Slow down
                    self.thrust_d = self.thrust_d #* 0.50;
            else:
                if self.thrust_d > 5:
                    self.thrust_d = self.thrust_d
            # print("w00+!", file=sys.stderr)

        self.calc_facing_theta()
        self.which_way_turn()

        self.power = " " + str(int(self.thrust_d))

    def calc_desired_outputs_defender(self):

        # Force control
        self.x_out = self.x + self.ax_d - self.ax
        self.y_out = self.y + self.ay_d - self.ay

        if self.thrust > 100:
            self.thrust = 100

        self.power = " " + str(int(self.thrust))

    def update_velocity(self):
        self.v_mag = self.calc_vector_mag(self.vx, self.vy)

    def update_accelerations(self):
        self.ax = self.vx - self.vx_prev
        self.ay = self.vy - self.vy_prev

    def update_Fp(self):
        self.mag_Fp = self.calc_vector_mag(self.ax, self.ay)
        self.theta_Fp = self.calc_vector_theta(self.ax, self.ay)

    def update_Fd(self):
        self.mag_Fd = self.calc_vector_mag(self.ax_d, self.ay_d)
        self.theta_Fd = self.calc_vector_theta(self.ax_d, self.ay_d)

    def check_on_target(self):
        # Calc the angle for the next checkpoint versus current velocity
        self.theta_v = self.calc_vector_theta(self.vx, self.vy)

        # Calc the next checkpoint angle
        self.theta_d_next = self.calc_vector_theta(self.targets_x[self.next_target_id],
                                                   self.targets_y[self.next_target_id])

        # Absolute diff between the two angles
        theta_diff = math.sqrt((self.theta_v - self.theta_d) ** 2)

        # print("ON TARG: " + str(self.theta_v) + ", " + str(self.theta_d_next) + ", " + str(theta_diff), file=sys.stderr);

        # Get the displacements from the next target
        x_diff = self.current_target[0] - self.x
        y_diff = self.current_target[1] - self.y

        # Set up vectors for math
        a = [self.vx, self.vy]
        b = [x_diff, y_diff]

        # Angle between (pod, current target, next target)
        self.turning_theta = math.acos(np.inner(a,b)/(self.distance*self.v_mag))

        return self.turning_theta < self.rotation_limit

    def calc_next_target_theta(self):
        # Get the displacements from the next target
        x_diff_p = self.current_target[0] - self.x
        y_diff_p = self.current_target[1] - self.y

        x_diff_np = self.current_target[0] - self.next_target[0]
        y_diff_np = self.current_target[1] - self.next_target[1]

        # Get the distance between the two targets
        mag_np = self.calc_vector_mag(x_diff_np, y_diff_np)

        # Set up vectors for math
        a = [x_diff_p, y_diff_p]
        b = [x_diff_np, y_diff_np]

        # Angle between (pod, current target, next target)
        self.turning_theta = math.acos(np.inner(a,b)/(self.distance*mag_np))

    def calc_facing_theta(self):
        # Get the displacements from the next target
        x_diff = self.current_target[0] - self.x
        y_diff = self.current_target[1] - self.y

        # Set up vectors for math
        a = [math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))]
        b = [x_diff, y_diff]

        # Angle between (pod, current target, next target)
        if self.v_mag == 0 or self.distance == 0:
            self.facing_theta = 0;
        else:
            self.facing_theta = math.acos(np.inner(a,b)/(self.distance*self.v_mag))

    def which_way_turn(self):
        # Get the displacements from the next target
        x_diff_pod = self.x - self.current_target[0]
        y_diff_pod = self.y - self.current_target[1]

        x_diff_targets = self.next_target[0] - self.current_target[0]
        y_diff_targets = self.next_target[1] - self.current_target[1]

        theta_np = self.calc_vector_theta(x_diff_targets, y_diff_targets)
        dist_np = self.calc_vector_mag(x_diff_targets, y_diff_targets)

        a = [x_diff_pod, y_diff_pod]
        b = [x_diff_targets, y_diff_targets]

        turning_angle = theta_np - self.facing_theta

        turning_sign = math.degrees(math.asin(np.linalg.norm(np.cross(a,b))/(self.distance * dist_np)))

        if turning_sign > 0:
            print("Left " + str(math.degrees(turning_sign)) + " - " + str(math.degrees(self.facing_theta)) + " = " + str(math.degrees(turning_angle)), file=sys.stderr)
        else:
            print("Right " + str(math.degrees(turning_sign)) + " - " + str(math.degrees(self.facing_theta)) + " = " + str(math.degrees(turning_angle)), file=sys.stderr)

    def calc_next_x_y(self, origin_x, origin_y):
        # Set up vectors with the current target as the origin
        target_pod_x = self.x - origin_x #self.current_target[0]
        target_pod_y = self.y - origin_y # self.current_target[1]
        target_pod_vect = np.array([target_pod_x, target_pod_y])
        target_pod_vect_mag = self.calc_vector_mag(target_pod_x, target_pod_y)

        target_next_x = self.next_target[0] - origin_x #self.current_target[0]
        target_next_y = self.next_target[1] - origin_y # self.current_target[1]
        target_next_vect = np.array([target_next_x, target_next_y])
        target_next_vect_mag = self.calc_vector_mag(target_next_x, target_next_y)

        # Get the bisecting vector
        unscaled_desired_vect_x = target_pod_vect_mag * target_next_vect[0] + target_next_vect_mag * target_pod_vect[0]
        unscaled_desired_vect_y = target_pod_vect_mag * target_next_vect[1] + target_next_vect_mag * target_pod_vect[1]

        unscaled_desired_vect_theta = self.calc_vector_theta(unscaled_desired_vect_x, unscaled_desired_vect_y)

        self.desired_x = 500 * math.cos(unscaled_desired_vect_theta) + origin_x #self.current_target[0]
        self.desired_y = 500 * math.sin(unscaled_desired_vect_theta) + origin_y # self.current_target[1]


    def say_something(self):
        return "Listen!"


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

firstRun = True

pod1 = Pod(0)
pod2 = Pod(0)
pods = [pod1, pod2]

laps = int(input())

pods[0].number_laps = laps
pods[1].number_laps = laps

checkpoint_count = int(input())

for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    pods[0].targets_x.append(checkpoint_x)
    pods[0].targets_y.append(checkpoint_y)
    pods[1].targets_x.append(checkpoint_x)
    pods[1].targets_y.append(checkpoint_y)

# game loop
while True:
    input_list = []
    for i in range(2):
        # x: x position of your pod
        # y: y position of your pod
        # vx: x speed of your pod
        # vy: y speed of your pod
        # angle: angle of your pod
        # next_check_point_id: next check point id of your pod
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        input_data = [x, y, vx, vy, angle, next_check_point_id]
        input_data_str = [str(i) for i in input_data]
        print(" ".join(input_data_str), file=sys.stderr)
        pods[i].update_pod(input_data)

    for i in range(2):
        # x_2: x position of the opponent's pod
        # y_2: y position of the opponent's pod
        # vx_2: x speed of the opponent's pod
        # vy_2: y speed of the opponent's pod
        # angle_2: angle of the opponent's pod
        # next_check_point_id_2: next check point id of the opponent's pod
        x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2 = [int(j) for j in input().split()]

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    if firstRun:
        print(str(pods[0].distance), file=sys.stderr)
        print(str(pods[1].distance), file=sys.stderr)
        # print(str(0) + " " + str(0) + " 0");
        print(str(int(pods[0].x_out)) + " " + str(int(pods[0].y_out)) + " BOOST")
        print(str(int(pods[1].x_out)) + " " + str(int(pods[1].y_out)) + " BOOST")
    else:
        print(str(pods[0].distance), file=sys.stderr)
        print(str(pods[1].distance), file=sys.stderr)
        # print(str(0) + " " + str(0) + " 0");
        if pods[0].thrust_d > 100:
            text = " " + str(int(100))
        else:
            text = " " + str(int(pods[0].thrust_d))
        print(str(int(pods[0].x_out)) + " " + str(int(pods[0].y_out)) + text)
        print(str(int(pods[1].x_out)) + " " + str(int(pods[1].y_out)) + pods[1].power)

    firstRun = False
