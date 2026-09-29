"""
proximity_detector.py

Unsafe proximity detection between workers and heavy machinery.
"""

import math


class ProximityDetector:
    """
    Detect unsafe proximity between workers and machinery.

    Proximity is calculated using:
        1. Stable worker ID
        2. Worker foot point
        3. Machinery bounding box
        4. Configurable safety-zone margin
        5. Consecutive-frame confirmation
        6. One event when a worker enters the safety zone
        7. Event reset when the worker leaves the zone
    """

    def __init__(
        self,
        safety_zone_margin=200,
        confirmation_frames=5,
        machinery_classes=None
    ):
        self.safety_zone_margin = safety_zone_margin
        self.confirmation_frames = confirmation_frames

        if machinery_classes is None:
            machinery_classes = {
                "machinery"
            }

        self.machinery_classes = {
            name.lower()
            for name in machinery_classes
        }

        self.worker_class = "person"

        # Number of consecutive frames a worker-machine
        # pair has remained inside the safety zone.
        self.proximity_history = {}

        # Worker-machine pairs that have already generated
        # an event during the current proximity period.
        self.active_events = set()

    @staticmethod
    def _get_foot_point(bbox):
        """
        Calculate the worker's ground/foot point.

        The foot point is the center of the bottom edge
        of the worker bounding box.
        """

        x1, y1, x2, y2 = bbox

        foot_x = (x1 + x2) // 2
        foot_y = y2

        return foot_x, foot_y

    @staticmethod
    def _point_to_box_distance(point, bbox):
        """
        Calculate the minimum distance between a point
        and a bounding box.

        Returns 0 when the point is inside the box.
        """

        point_x, point_y = point

        x1, y1, x2, y2 = bbox

        horizontal_distance = max(
            x1 - point_x,
            0,
            point_x - x2
        )

        vertical_distance = max(
            y1 - point_y,
            0,
            point_y - y2
        )

        return math.sqrt(
            horizontal_distance ** 2
            + vertical_distance ** 2
        )

    def _is_inside_safety_zone(self, foot_point, machinery_bbox):
        """
        Determine whether the worker foot point is inside
        the machinery safety zone.

        The machinery bounding box is expanded by
        safety_zone_margin pixels on all sides.
        """

        x1, y1, x2, y2 = machinery_bbox

        margin = self.safety_zone_margin

        safety_x1 = x1 - margin
        safety_y1 = y1 - margin
        safety_x2 = x2 + margin
        safety_y2 = y2 + margin

        foot_x, foot_y = foot_point

        return (
            safety_x1 <= foot_x <= safety_x2
            and
            safety_y1 <= foot_y <= safety_y2
        )

    def detect(self, workers, machinery):
        """
        Detect confirmed unsafe proximity events.

        Parameters
        ----------
        workers : list
            Output from PPEStateTracker.update().
            Each worker dictionary should contain:
                - stable_worker_id
                - person

        machinery : list
            Detection objects for machinery.

        Returns
        -------
        list
            Confirmed proximity events.
        """

        current_pairs = set()
        confirmed_events = []

        for worker in workers:

            stable_worker_id = worker.get("stable_worker_id")

            person = worker.get("person")

            # Skip invalid worker data.
            if stable_worker_id is None:
                continue

            if person is None:
                continue

            worker_bbox = person.bbox

            # Calculate worker foot point.
            foot_point = self._get_foot_point(
                worker_bbox
            )

            for machine in machinery:

                # Machinery must have a tracker ID.
                if machine.track_id is None:
                    continue

                # Check machinery class.
                if (
                    machine.class_name.lower()
                    not in self.machinery_classes
                ):
                    continue

                machinery_bbox = machine.bbox

                # Check whether worker foot point is
                # inside the expanded machinery safety zone.
                inside_safety_zone = (
                    self._is_inside_safety_zone(
                        foot_point,
                        machinery_bbox
                    )
                )

                # Pair is outside the safety zone.
                if not inside_safety_zone:
                    continue

                # Stable worker ID + machinery tracker ID.
                pair_key = (
                    stable_worker_id,
                    machine.track_id
                )

                current_pairs.add(pair_key)

                # Increase consecutive-frame count.
                self.proximity_history[pair_key] = (
                    self.proximity_history.get(
                        pair_key,
                        0
                    ) + 1
                )

                frame_count = (
                    self.proximity_history[pair_key]
                )

                # Generate only ONE event when the pair
                # first becomes confirmed.
                if (
                    frame_count >= self.confirmation_frames
                    and pair_key not in self.active_events
                ):

                    self.active_events.add(pair_key)

                    distance = self._point_to_box_distance(
                        foot_point,
                        machinery_bbox
                    )

                    confirmed_events.append(
                        {
                            "worker_id": stable_worker_id,
                            "worker_bbox": worker_bbox,
                            "worker_foot_point": foot_point,

                            "machinery_id": machine.track_id,
                            "machinery_bbox": machinery_bbox,

                            "distance_pixels": round(
                                distance,
                                2
                            ),

                            "safety_zone_margin": (
                                self.safety_zone_margin
                            ),

                            "confirmation_frames": (
                                self.confirmation_frames
                            ),

                            "event": "UNSAFE PROXIMITY"
                        }
                    )

        # --------------------------------------------------
        # RESET
        # --------------------------------------------------
        #
        # If a worker-machine pair is no longer inside
        # the safety zone, remove its history.
        #
        # This allows a NEW event when the worker later
        # enters the safety zone again.
        # --------------------------------------------------

        inactive_pairs = (
            set(self.proximity_history.keys())
            - current_pairs
        )

        for pair_key in inactive_pairs:

            self.proximity_history.pop(
                pair_key,
                None
            )

            self.active_events.discard(
                pair_key
            )

        return confirmed_events