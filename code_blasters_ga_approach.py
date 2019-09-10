import sys
import math
import numpy as np


class Point:
    def __init__(self, x_in, y_in):
        self.x: float = x_in
        self.y: float = y_in

    def distance(self, point):
        return math.sqrt(self.distance_squared(point))

    def distance_squared(self, point):
        return (self.x - point.x) ** 2 + (self.y - point.y) ** 2

    def closest(self, point1, point2):
        da: float = point2.y - point1.y
        db: float = point2.x - point1.x
        c1: float = da * point1.x + db * point1.y
        c2: float = -db * self.x + da * self.y
        det: float = da ** 2 + db ** 2
        if det != 0:
            cx: float = (da * c1 - db * c2) / det
            cy: float = (da * c2 + db * c1) / det
        else:
            cx: float = self.x
            cy: float = self.y
        return Point(cx, cy)


class Unit(Point):
    def __init__(self, x_in, y_in, vx_in, vy_in, id_in, radius_in, num_targets_in):
        super(Unit, self).__init__(x_in, y_in)
        self.next_target_id: int = id_in
        self.radius: float = radius_in
        self.vx: float = vx_in
        self.vy: float = vy_in
        self.num_targets: int = num_targets_in

    def collision(self, unit):
        # print("Collision", file=sys.stderr)
        distance: float = self.distance_squared(unit)
        radius_sum: float = (self.radius + unit.radius) ** 2
        if distance < radius_sum:  # Objects already touching
            return Collision(self, unit, 0.0)
        if self.vx == unit.vx and self.vy == unit.vy:  # Parallel objects
            return None
        collision_x: float = self.x - unit.x
        collision_y: float = self.y - unit.y
        collision_point: Point = Point(collision_x, collision_y)
        collision_vx: float = self.vx - unit.vx
        collision_vy: float = self.vy - unit.vy
        unit_point: Point = Point(0, 0)
        closest_point: Point = unit_point.closest(collision_point,
                                                  Point(collision_x + collision_vx, collision_y + collision_vy))
        closest_point_distance: float = unit_point.distance_squared(closest_point)
        collision_point_distance: float = collision_point.distance_squared(closest_point)
        if closest_point_distance < radius_sum:
            length: float = math.sqrt(collision_vx ** 2 + collision_vy ** 2)
            backup_distance: float = math.sqrt(radius_sum - closest_point_distance)
            closest_point.x = closest_point.x - backup_distance * (collision_vx / length)
            closest_point.y = closest_point.y - backup_distance * (collision_vy / length)
            if collision_point.distance_squared(closest_point) > collision_point_distance:
                return None
            closest_point_distance = closest_point.distance(collision_point)
            if closest_point_distance > length:
                return None
                # print(str(t), file=sys.stderr)
            t: float = closest_point_distance / length
            return Collision(self, unit, t)
        return None

    def bounce(self, unit):
        return


class Pod(Unit):
    def __init__(self, x_in, y_in, vx_in, vy_in, angle_in, id_in, radius_in, num_targets_in, laps_in):
        super(Pod, self).__init__(x_in, y_in, vx_in, vy_in, id_in, radius_in, num_targets_in)
        self.angle: float = angle_in
        self.checkpoint = None
        self.checked: int = 0
        self.timeout: int = 100
        self.partner = None
        self.shield: bool = False
        self.number_laps: int = laps_in
        self.solutions = []
        self.fitness: float = 0
        return

    def add_partner(self, pod):
        self.partner = pod
        return

    def get_angle(self, point):
        distance = self.distance(point)
        dx = (point.x - self.x) / distance
        dy = (point.y - self.y) / distance
        theta: float = math.acos(dx)
        theta = math.degrees(theta)
        if dy < 0:
            theta = 360 - theta
        return theta

    def difference_angle(self, point):
        theta = self.get_angle(point)
        right = self.angle - theta if self.angle <= theta else 360.0 - self.angle + theta
        left = self.angle - theta if self.angle <= theta else self.angle + 360.0 - theta
        if right < left:
            return right
        else:
            return -left

    def rotate(self, point):
        theta = self.get_angle(point)
        if theta > 18.0:
            theta = 18
        elif theta < -18.0:
            theta = -18
        self.angle += theta
        if self.angle >= 360.0:
            self.angle = self.angle - 360.0
        elif self.angle < 0.0:
            self.angle += 360.0
        return

    def boost(self, thrust):
        if self.shield:
            return
        theta_radians = math.radians(self.angle)
        self.vx += math.cos(theta_radians) * thrust
        self.vy += math.sin(theta_radians) * thrust
        return

    def move(self, t):
        self.x += self.vx * t
        self.y += self.vy * t
        return

    def end(self, checkpoints):
        self.x = round(self.x)
        self.y = round(self.y)
        self.vx = math.trunc(self.vx * 0.85)
        self.vy = math.trunc(self.vy * 0.85)
        self.timeout -= 1
        self.fitness = self.score(checkpoints)
        return self.fitness

    def play(self, point, thrust, checkpoints):
        self.fitness = 0
        self.checked = 0
        self.rotate(point)
        self.boost(thrust)
        self.move(1.0)
        self.end(checkpoints)
        return

    def bounce(self, unit):
        if isinstance(unit, Checkpoint):
            self.bounce_with_checkpoint()
        else:
            mass1: float = 10 if self.shield else 1
            mass2: float = 10 if unit.shield else 1
            mass_coefficient: float = (mass1 + mass2) / (mass1 * mass2)
            new_x: float = self.x - unit.x
            new_y: float = self.y - unit.y
            new_xy_squared: float = new_x ** 2 + new_y ** 2
            dvx: float = self.vx - unit.vx
            dvy: float = self.vy - unit.vy
            product: float = new_x * dvx + new_y * dvy
            fx: float = (new_x * product) / (new_xy_squared * mass_coefficient)
            fy: float = (new_y * product) / (new_xy_squared * mass_coefficient)
            self.vx -= fx / mass1
            self.vy -= fy / mass1
            unit.vx += fx / mass2
            unit.vy += fy / mass2
            impulse: float = math.sqrt(fx ** 2 + fy ** 2)
            if impulse < 120:
                fx = fx * 120.0 / impulse
                fy = fy * 120.0 / impulse
            self.vx -= fx / mass1
            self.vy -= fy / mass1
            unit.vx += fx / mass2
            unit.vy += fy / mass2
        return

    def bounce_with_checkpoint(self):
        self.next_target_id += 1
        if self.next_target_id == self.num_targets:
            self.next_target_id = 0
        self.timeout = 100
        self.checked += 1
        return

    def score(self, checkpoints):
        self.fitness += self.checked * 50000 - self.distance(checkpoints[self.next_target_id])
        return self.fitness

    def output(self, move):
        theta: float = self.angle + move.angle
        if theta >= 360.0:
            theta = theta - 360.0
        elif theta < 0.0:
            theta += 360.0
        theta = math.radians(theta)
        px: float = self.x + math.cos(theta) * 10000.0
        py: float = self.y + math.sin(theta) * 10000.0
        print(str(round(px)) + " " + str(round(py)) + " " + str(move.thrust))
        return

    def autopilot_point(self, target, next_target):
        # Figure out the desired x & y
        # Set up vectors with the current target as the origin
        target_pod_x = self.x - target.x
        target_pod_y = self.y - target.y
        target_pod_vect = np.array([target_pod_x, target_pod_y])
        target_pod_vect_mag = math.sqrt(target_pod_x ** 2 + target_pod_y ** 2)
        # Set up vectors with the current target and the next target
        target_next_x = next_target.x - target.x
        target_next_y = next_target.y - target.y
        target_next_vect = np.array([target_next_x, target_next_y])
        target_next_vect_mag = math.sqrt(target_next_x ** 2 + target_next_y ** 2)
        # Get the bisecting vector
        unscaled_desired_vect_x = target_pod_vect_mag * target_next_vect[0] + target_next_vect_mag * target_pod_vect[0]
        unscaled_desired_vect_y = target_pod_vect_mag * target_next_vect[1] + target_next_vect_mag * target_pod_vect[1]
        unscaled_desired_vect_theta = math.atan2(unscaled_desired_vect_y, unscaled_desired_vect_x)
        desired_x = 300 * math.cos(unscaled_desired_vect_theta) + target.x
        desired_y = 300 * math.sin(unscaled_desired_vect_theta) + target.y
        # Create point from desired x & y
        target_point = Point(self.x + desired_x - self.x - self.vx, self.y + desired_y - self.y - self.vy)
        # print(str(desired_x) + "-" + str(self.x) + "-" +  str(self.vx) + "," + str(desired_y) + "-" + str(self.x) + "-" + str(self.vy), file=sys.stderr)
        return target_point

    def autopilot_thrust(self, point, style):
        # Calculate the thrust
        distance = self.distance(point)
        scale_factor = 100 / math.pi
        stretch_factor = 0.002
        far_away = 2000
        approach_dist = 1200
        base = 45
        if distance > far_away:
            thrust = 100
        elif distance > approach_dist:
            if style == 0:
                thrust = (100 * (distance / (far_away - approach_dist)) - base) + base
            elif style == 1:
                thrust = scale_factor * math.atan(stretch_factor * (distance - approach_dist)) + base
            elif style == 2:
                thrust = 75
            elif style == 3:
                thrust = 25
            else:
                thrust = (100 * (distance / (far_away - approach_dist)) - base) + base
        else:
            thrust = base
        if self.difference_angle(point) >= 90 and self.difference_angle(point) <= 270:
            # print(str(self.difference_angle(point)) + ", " + str(self.x) + ", " + str(self.y) + " - " + str(point.x) + ", " + str(point.y), file=sys.stderr)
            thrust = 0
        # print(str(self.get_angle(point)) + " | " + str(self.difference_angle(point)) + ", " + str(self.x) + ", " + str(self.y) + " - " + str(point.x) + ", " + str(point.y), file=sys.stderr)
        return thrust

    def autopilot(self, target, next_target, style, checkpoints):
        target_point = self.autopilot_point(target, next_target)
        theta = self.get_angle(target_point)
        thrust = self.autopilot_thrust(target_point, style)
        # Play the turn
        self.play(target_point, thrust, checkpoints)
        return Move(target_point, theta, thrust)


class Checkpoint(Unit):
    def __init__(self, x_in, y_in, id_in, radius_in, num_targets_in):
        super(Checkpoint, self).__init__(x_in, y_in, 0.0, 0.0, id_in, radius_in, num_targets_in)

    def bounce(self, unit):
        return


class Solution:
    def __init__(self):
        self.moves1 = []
        self.score1: float = 0.0
        self.moves2 = []
        self.score2: float = 0.0
        self.overall_fitness: float = 0.0

    def randomize(self):
        return

    def score(self):
        # for j in range(len(self.moves1)):
        #     self.score1 += self.moves1[j].fitness
        # for j in range(len(self.moves2)):
        #     self.score2 += self.moves2[j].fitness
        self.overall_fitness = (self.score1 + self.score2) / 2
        return

    def mutate(self, amplitude):
        mutated_moves1 = []
        mutated_moves2 = []
        for j in range(len(self.moves1)):
            mutated_moves1.append(self.moves1[j].mutate(amplitude))
        for j in range(len(self.moves2)):
            mutated_moves2.append(self.moves2[j].mutate(amplitude))
        return [mutated_moves1, mutated_moves2]


class Move:
    def __init__(self, point_in, angle_in, thrust_in):
        self.point: Point = point_in
        self.angle: float = angle_in
        self.thrust: int = thrust_in
        self.fitness: float = 0.0

    def mutate(self, amplitude):
        ramin: float = self.angle - 36.0 * amplitude
        ramax: float = self.angle + 36.0 * amplitude
        if ramin < -18.0:
            ramin = -18.0
        if ramax > 18.0:
            ramax = 18.0
        self.angle = (ramax - ramin) * np.random.random() + ramin
        pmin: int = self.thrust - 200 * amplitude
        pmax: int = self.thrust + 200 * amplitude
        if pmin < 0:
            pmin = 0
        if pmax > 0:
            pmax = 200
        self.thrust = (pmax - pmin) * np.random.random() + pmin
        # print(str(self.angle), file=sys.stderr)
        return self


class Collision:
    def __init__(self, unit1, unit2, t_factor):
        self.unit_a: Unit = unit1
        self.unit_b: Unit = unit2
        self.time: float = t_factor


def auto_trajectory(pod_list, checkpoints, move_list):
    for j in range(len(pod_list)):
        pod_list[j].rotate(move_list[j].point)
        pod_list[j].boost(move_list[j].thrust)

    return play_turn(pod_list, checkpoints)


def play_turn(pod_list, checkpoints):
    # print("Start turn", file=sys.stderr)
    bug_found = False
    bug_collision = None
    fitness_results = []
    t: float = 0.0
    while t < 1.0:
        first_collision = None
        # print(str(bug_collision), file=sys.stderr)
        for j in range(len(pod_list)):
            for k in range(j + 1, len(pod_list)):
                # print("B40 Col", file=sys.stderr)
                collision = pod_list[j].collision(pod_list[k])
                if (collision is not None) and (collision.time + t < 1.0) and (
                        (first_collision is None) or (collision.time < first_collision.time)):
                    # if bug_collision is not None:
                    #     if bug_collision.unit_a != collision.unit_a and bug_collision.unit_b != bug_collision.unit_b \
                    #             and collision.time > 0:
                    first_collision = collision
                    if bug_found:
                        # print(str(bug_collision.unit_a) + " " + str(first_collision.unit_a) + " " + str(bug_collision.unit_b) + " " + str(first_collision.unit_b) + " " + str(first_collision.time), file=sys.stderr)
                        if first_collision.time <= 0:
                            first_collision = None
            # print("B41 Col", file=sys.stderr)
            collision = pod_list[j].collision(checkpoints[pod_list[j].next_target_id])
            if (collision is not None) and (collision.time + t < 1.0) and (
                    (first_collision is None) or (collision.time < first_collision.time)):
                # if bug_collision is not None:
                #     if bug_collision.unit_a != collision.unit_a and bug_collision.unit_b != bug_collision.unit_b \
                #             and collision.time > 0:
                first_collision = collision
                if bug_found:
                    if first_collision.time <= 0:
                        first_collision = None
        if first_collision is None:
            # print("1st col is none", file=sys.stderr)
            for j in range(len(pod_list)):
                pod_list[j].move(1.0 - t)
            t = 1.0
        else:
            # print("1st col is some", file=sys.stderr)
            for j in range(len(pod_list)):
                pod_list[j].move(first_collision.time)
            first_collision.unit_a.bounce(first_collision.unit_b)
            bug_collision = first_collision
            bug_found = True
            t += first_collision.time
            # print(str(t), file=sys.stderr)
    for j in range(len(pod_list)):
        fitness_results.append(pod_list[j].end(checkpoints))
    return fitness_results


first_turn: bool = True
targets = []

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

laps: int = int(input())

checkpoint_count: int = int(input())

for i in range(checkpoint_count):
    checkpoint_x, checkpoint_y = [int(j) for j in input().split()]
    # Add the checkpoints to the targets list
    targets.append(Checkpoint(checkpoint_x, checkpoint_y, i, 600, checkpoint_count))

# game loop
while True:
    input_list = []
    pods = []
    pod_clones = []
    enemies = []
    enemy_clones = []
    for i in range(2):
        # x: x position of your pod
        # y: y position of your pod
        # vx: x speed of your pod
        # vy: y speed of your pod
        # angle: angle of your pod
        # next_check_point_id: next check point id of your pod
        x, y, vx, vy, angle, next_check_point_id = [int(j) for j in input().split()]
        pod = Pod(x, y, vx, vy, angle, next_check_point_id, 400, checkpoint_count, laps)
        pods.append(pod)

    for i in range(2):
        # x_2: x position of the opponent's pod
        # y_2: y position of the opponent's pod
        # vx_2: x speed of the opponent's pod
        # vy_2: y speed of the opponent's pod
        # angle_2: angle of the opponent's pod
        # next_check_point_id_2: next check point id of the opponent's pod
        x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2 = [int(j) for j in input().split()]
        pod = Pod(x_2, y_2, vx_2, vy_2, angle_2, next_check_point_id_2, 400, checkpoint_count, laps)
        pods.append(pod)
    pod_clones = pods
    # print("100 100 100")

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # Create five solutions for each pod
    num_generations: int = 5
    solutions = []
    num_turns = 5
    num_solutions: int = 10
    num_parents: int = 5
    for i in range(num_solutions):
        solution = Solution()
        pod_clones = pods
        # For six turns
        for l in range(num_turns):
            # Create list for saving the moves
            moves = []
            # For each pod
            for n in range(len(pod_clones)):
                # Get the pod's next target (without %) for 'autopilot'
                if pod_clones[n].next_target_id + 1 == pod_clones[n].num_targets:
                    next_target = 0
                else:
                    next_target = pod_clones[n].next_target_id + 1
                # Create one turn
                current_move = pod_clones[n].autopilot(targets[pod_clones[n].next_target_id], targets[next_target], 0,
                                                       targets)
                # Save the move for that pod for this turn
                moves.append(current_move)
                # Save that move for that specific pod
                if n == 0:  # First pod
                    solution.moves1.append(current_move)
                elif n == 1:  # Second pod
                    solution.moves2.append(current_move)
            # Play all the moves for all the clones and get their 'fitness'
            fitness = auto_trajectory(pod_clones, targets, moves)
            # Save that move's fitness
            solution.moves1[l].fitness = fitness[0]
            solution.moves2[l].fitness = fitness[1]
            solution.score1 = pod_clones[0].fitness
            solution.score2 = pod_clones[1].fitness
            solution.score()
        solutions.append(solution)
    for i in range(num_generations):
        # Sort the solutions to pick best three (avg of score1 + score2)
        solutions.sort(key=lambda parent: parent.overall_fitness, reverse=True)
        # Pick the best 3
        parents = solutions[:num_parents]
        children = []
        for j in range(num_parents):
            # For every parent, mutate the first move then play the rest of the turns

            # Mutate the parent's moves
            mutated_moves = parents[j].mutate(j / num_parents)
            # print(str(mutated_moves[0]), file=sys.stderr)
            # Create a child
            child = Solution()
            # Add the mutated moves to the child
            child.moves1 = mutated_moves[0]
            child.moves2 = mutated_moves[1]
            # Score the child
            child.score()
            # Add the child to the children
            children.append(child)
        solutions = parents + children
        # Loop through 10 times
        # Mutate them -> 5
        # Run mutations
        # Score them
        # Pick best 3

    # Play the best move
    solutions.sort(key=lambda parent: parent.overall_fitness, reverse=True)
    best_choices = [solutions[0].moves1[0], solutions[0].moves2[0]]
    if best_choices[0].thrust > 100:
        best_choices[0].thrust = 100
    if best_choices[1].thrust > 100:
        best_choices[1].thrust = 100
    if first_turn:
        print(str(int(best_choices[0].point.x)) + " " + str(int(best_choices[0].point.y)) + " BOOST")
        print(str(int(best_choices[1].point.x)) + " " + str(int(best_choices[1].point.y)) + " BOOST")
        first_turn = False
    else:
        print(str(int(best_choices[0].point.x)) + " " + str(int(best_choices[0].point.y)) + " " + str(
            int(best_choices[0].thrust)))
        print(str(int(best_choices[1].point.x)) + " " + str(int(best_choices[1].point.y)) + " " + str(
            int(best_choices[1].thrust)))

