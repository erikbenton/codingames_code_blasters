import sys
import math

class Pod:

    def __init__(self):

        # X components
        # Current
        self.x = 0;
        self.vx = 0;
        self.ax = 0;

        # Desired
        self.x_d = 0;
        self.vx_d = 0;
        self.ax_d = 0;

        # Commanded
        self.x_cmd = 0;
        self.vx_cmd = 0;
        self.ax_cmd = 0;
        
        # Y components
        # Current
        self.y = 0;
        self.vy = 0;
        self.ay = 0;

        # Desired
        self.y_d = 0;
        self.vy_d = 0;
        self.ay_d = 0;

        # Commanded
        self.y_cmd = 0;
        self.vy_cmd = 0;
        self.ay_cmd = 0;

        # Force components of the Pod
        self.theta_Fp = 0;
        self.mag_Fp = 0;

        # Force components for desired Pod force
        self.theta_Fd = 0;
        self.mag_Fd = 0;

        # Force components for commanded Pod force
        self.theta_Fcmd = 0;
        self.mag_Fcmd = 0;
        
        # Components for targets
        self.targets_x = [];
        self.targets_y = [];
        self.current_target_id = 0;
        self.current_target = [0,0];

        # Angle
        self.angle = 0;
        self.theta_d = 0;

        # Overalls
        self.distance = 0;
        self.thrust = 0;
        self.power = "0";
        self.thrust_d = 0;
        self.x_out = 0;
        self.y_out = 0;
        
        # Prev Values
        self.x_prev = 0;
        self.vx_prev = 0;
        self.ax_prev = 0;

        self.x_d_prev = 0;
        self.vx_d_prev = 0;
        self.ax_d_prev = 0;
        
        self.y_prev = 0;
        self.vy_prev = 0;
        self.ay_prev = 0;

        self.y_d_prev = 0;
        self.vy_d_prev = 0;
        self.ay_d_prev = 0;

        self.theta_Fp_prev = 0;
        self.mag_Fp_prev = 0;

        self.theta_Fd_prev = 0;
        self.mag_Fd_prev = 0;

        self.theta_Fcmd_prev = 0;
        self.mag_Fcmd_prev = 0;

        self.angle_prev = 0;
        self.theta_d_prev = 0;

        self.distance_prev = 0;
        self.thrust_prev = 0;
        self.power_prev = "0";
        self.thrust_d_prev = 0;
        self.x_out_prev = 0;
        self.y_out_prev = 0;

    def calc_vector_mag(self, x, y):
        return math.sqrt(x**2 + y**2);

    def calc_vector_theta(self, x, y):
        
        # if x == 0 or y == 0:
        #     return 0;

        return math.atan2(y,x);

    def update_pod(self, input_list):
        
        # Update the prev values
        self.x_prev = self.x;
        self.vx_prev =self.vx;
        self.ax_prev =self.ax;

        self.x_d_prev = self.x_d;
        self.vx_d_prev = self.vx_d;
        self.ax_d_prev = self.ax_d;
        
        self.y_prev = self.y;
        self.vy_prev = self.vy;
        self.ay_prev = self.ay;

        self.y_d_prev = self.y_d;
        self.vy_d_prev = self.vy_d;
        self.ay_d_prev = self.ay_d;

        self.theta_Fp_prev = self.theta_Fp;
        self.mag_Fp_prev = self.mag_Fp;

        self.theta_Fd_prev = self.theta_Fd;
        self.mag_Fd_prev = self.mag_Fd;

        self.theta_Fcmd_prev = self.theta_Fcmd;
        self.mag_Fcmd_prev = self.mag_Fcmd;

        self.angle_prev = self.angle;
        self.theta_d_prev = self.theta_d;

        self.distance_prev = self.distance;
        self.thrust_prev = self.thrust;
        self.power_prev = self.power;
        self.thrust_d_prev = self.thrust_d;

        x_ind = 0;
        y_ind = 1;
        vx_ind = 2;
        vy_ind = 3;
        ang_ind = 4;
        id_ind = 5;

        self.x = input_list[x_ind];
        self.y = input_list[y_ind];
        self.vx = input_list[vx_ind];
        self.vy = input_list[vy_ind];
        self.angle = input_list[ang_ind];
        self.current_target_id = input_list[id_ind];

        # First figure out what's happening with the pod
        # Calc what wasn't given
        self.update_accelerations();
        self.update_Fp();

        # Now figure out where target is and how to get there
        # First find target
        self.update_target_positions();

        # Then orient to the target
        self.update_target_locations();

        # Determine the desired thrust
        self.calc_desired_thrust();
        self.calc_desired_accelerations();

        # Determine what new inputs would make current course the desired course
        self.calc_desired_outputs();

    def update_target_positions(self):
        self.current_target[0] = self.targets_x[self.current_target_id];
        self.current_target[1] = self.targets_y[self.current_target_id];

    def update_target_locations(self):
        self.distance = self.calc_vector_mag((self.current_target[0] - self.x), (self.current_target[1] - self.y));
        self.theta_d = self.calc_vector_theta((self.current_target[0] - self.x), (self.current_target[1] - self.y));

    def calc_desired_thrust(self):
        far_away = 4000;
        scale_factor = 200/math.pi;
        stretch_factor = 0.002;
        approach_dist = 100;
        base = 50;

        if self.distance > far_away:
            self.thrust_d = 100;
        elif self.distance > approach_dist:
            self.thrust_d = (100 * (self.distance/(far_away - approach_dist)) - base) + base;# scale_factor * math.atan(stretch_factor*(self.distance - approach_dist)) + base;
        else:
            self.thrust_d = base;

    def calc_desired_accelerations(self):
        self.ax_d = self.thrust_d * math.cos(self.theta_d);
        self.ay_d = self.thrust_d * math.sin(self.theta_d);

    def calc_desired_outputs(self):
        self.x_out = self.x + self.ax_d - self.ax;
        self.y_out = self.y + self.ay_d - self.ay;
        self.thrust = self.calc_vector_mag(self.ax_d, self.ay_d);
        if self.thrust > 100:
            self.thrust = 100;

        self.power = " " + str(int(self.thrust));

    def update_accelerations(self):
        self.ax = self.vx - self.vx_prev;
        self.ay = self.vy - self.vy_prev;

    def update_Fp(self):
        self.mag_Fp = self.calc_vector_mag(self.ax, self.ay);
        self.theta_Fp = self.calc_vector_theta(self.ax, self.ay);

    def update_Fd(self):
        self.mag_Fd = self.calc_vector_mag(self.ax_d, self.ay_d);
        self.theta_Fd = self.calc_vector_theta(self.ax_d, self.ay_d);

    def say_something(self):
        return "Listen!";


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

firstRun = True;

pod1 = Pod();
pod2 = Pod();
pods = [pod1, pod2];

laps = int(input())
checkpoint_count = int(input())
for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    pods[0].targets_x.append(checkpoint_x);
    pods[0].targets_y.append(checkpoint_y);
    pods[1].targets_x.append(checkpoint_x);
    pods[1].targets_y.append(checkpoint_y);

# game loop
while True:
    input_list = [];
    for i in range(2):
        # x: x position of your pod
        # y: y position of your pod
        # vx: x speed of your pod
        # vy: y speed of your pod
        # angle: angle of your pod
        # next_check_point_id: next check point id of your pod
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        input_data = [x, y, vx, vy, angle, next_check_point_id]
        input_data_str = [str(i) for i in input_data];
        print(" ".join(input_data_str), file=sys.stderr);
        pods[i].update_pod(input_data);

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
        print(str(int(pods[0].thrust_d)) + ", " + str(int(pods[0].theta_d)) + ", " + str(int(pods[0].angle)), file=sys.stderr);
        print(str(int(pods[1].thrust_d)) + ", " + str(int(pods[1].theta_d)) + ", " + str(int(pods[1].angle)), file=sys.stderr);
        # print(str(0) + " " + str(0) + " 0");
        print(str(int(pods[0].x_out)) + " " + str(int(pods[0].y_out)) + " BOOST");
        print(str(int(pods[1].x_out)) + " " + str(int(pods[1].y_out)) + " BOOST");
    else:
        print(str(int(pods[0].thrust_d)) + ", " + str(int(pods[0].theta_d)) + ", " + str(int(pods[0].angle)) + " " +str(math.degrees(math.atan2(-1 * pods[0].y, -1 * pods[0].x))), file=sys.stderr);
        print(str(int(pods[1].thrust_d)) + ", " + str(int(pods[1].theta_d)) + ", " + str(int(pods[1].angle)), file=sys.stderr);
        # print(str(0) + " " + str(0) + " 0");
        if pods[0].thrust_d > 100:
            text = " " + str(int(100));
        else:
            text = " " + str(int(pods[0].thrust_d));
        print(str(int(pods[0].x_out)) + " " + str(int(pods[0].y_out)) + text);
        print(str(int(pods[1].x_out)) + " " + str(int(pods[1].y_out)) + pods[1].power);

    firstRun = False;

    