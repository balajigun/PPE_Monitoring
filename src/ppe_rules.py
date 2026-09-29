"""
ppe_rules.py

This module evaluates PPE compliance for detected workers.
"""

from detection import Detection


class PPERules:
    """
    Evaluates PPE compliance for tracked workers.
    """

    def __init__(self):
        print("PPE Rule Engine initialized.")

    def is_inside(self, person_bbox, object_bbox):
        """
        Checks whether the center of an object lies inside
        a person's bounding box.

        Parameters
        ----------
        person_bbox : tuple
            (x1, y1, x2, y2)

        object_bbox : tuple
            (x1, y1, x2, y2)

        Returns
        -------
        bool
        """

        # Person coordinates
        px1, py1, px2, py2 = person_bbox

        # Object coordinates
        ox1, oy1, ox2, oy2 = object_bbox

        # Object center
        center_x = (ox1 + ox2) // 2
        center_y = (oy1 + oy2) // 2

        return (
            px1 <= center_x <= px2 and
            py1 <= center_y <= py2
        )

    def get_object_center(self, bbox):
        """
        Returns the center point of a bounding box.

        Parameters
        ----------
        bbox : tuple
            (x1, y1, x2, y2)

         Returns
        -------
        tuple
            (center_x, center_y)
        """

        x1, y1, x2, y2 = bbox

        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        return center_x, center_y


    def is_point_inside_region(
        self,
        person_bbox,
        object_bbox,
        region_start,
        region_end
    ):
        """
        Checks whether the center of an object lies
        inside a vertical region of a person's bounding box.

        region_start and region_end are expressed as
        percentages of the person's height.
        """

        px1, py1, px2, py2 = person_bbox

        center_x, center_y = self.get_object_center(object_bbox)

        person_height = py2 - py1

        region_y1 = py1 + int(person_height * region_start)
        region_y2 = py1 + int(person_height * region_end)

        return (
            px1 <= center_x <= px2
            and
            region_y1 <= center_y <= region_y2
        )

    def is_in_head_region(self, person_bbox, object_bbox):
        """
        Checks whether an object lies in the person's head region.
        """

        return self.is_point_inside_region(
            person_bbox,
            object_bbox,
            0.00,
            0.25
        )

    def find_helmet(self, person, hardhats):
        """
        Returns True if a helmet belongs to the person.
        """

        for helmet in hardhats:

            if self.is_in_head_region(
                person.bbox,
                helmet.bbox
            ):
                return True

        return False
    
    def find_no_helmet(self, person, no_hardhats):
        """
        Returns True if a NO-Hardhat detection belongs
        to the person.
        """

        for no_helmet in no_hardhats:

            if self.is_in_head_region(
                person.bbox,
                no_helmet.bbox
            ):
                return True

        return False

    def is_in_face_region(self, person_bbox, object_bbox):
            """
            Checks whether the center of an object lies
            inside the face region of a person's bounding box.
            """
    
            px1, py1, px2, py2 = person_bbox
            ox1, oy1, ox2, oy2 = object_bbox
    
            object_center_x = (ox1 + ox2) // 2
            object_center_y = (oy1 + oy2) // 2
    
            person_height = py2 - py1
    
            face_y1 = py1
            face_y2 = py1 + int(person_height * 0.35)
    
            return (
                px1 <= object_center_x <= px2
                and
                face_y1 <= object_center_y <= face_y2
            )
    
    def find_mask(self, person, masks):
        """
        Returns True if a face mask belongs to the person.
        """

        for mask in masks:

            if self.is_in_face_region(
            person.bbox,
            mask.bbox
            ):
                return True

        return False
    
    def find_no_mask(self, person, no_masks):
        """
        Returns True if a NO-Mask detection belongs to the person.
        """

        for no_mask in no_masks:

            if self.is_in_face_region(
            person.bbox,
            no_mask.bbox
        ):
                return True

        return False 
    
    def is_in_torso_region(self, person_bbox, object_bbox):
        """
        Checks whether an object lies in the person's torso region.
        """

        return self.is_point_inside_region(
            person_bbox,
            object_bbox,
            0.25,
            0.70
        )

    def find_vest(self, person, safety_vests):
            """
            Returns True if a safety vest belongs to the person.
            """
    
            for vest in safety_vests:
    
                if self.is_in_torso_region(
                    person.bbox,
                    vest.bbox
                ):
                    return True
    
            return False

    def find_no_vest(self, person, no_safety_vests):
        """
        Returns True if a NO-Safety Vest detection belongs
        to the person.
        """

        for no_vest in no_safety_vests:

            if self.is_in_torso_region(
                person.bbox,
                no_vest.bbox
            ):
                return True

        return False
    
    def evaluate_worker_status(self, worker):

        violations = []

        if worker["no_helmet"]:
            violations.append("NO HARDHAT")

        if worker["no_vest"]:
            violations.append("NO SAFETY VEST")

        if worker["no_mask"]:
            violations.append("NO MASK")

        if len(violations) == 0:
            return "MONITORING"

        return " | ".join(violations)

    def evaluate(self, detections):
        """
        Evaluate PPE compliance for the current frame.

        Parameters
        ----------
        detections : list[Detection]
            List of all detections in the current frame.

        Returns
        -------
        list
            PPE status for each detected person.
        """

        # -----------------------------
        # Separate detections by class
        # -----------------------------

        persons = []
        hardhats = []
        safety_vests = []
        masks = []

        no_hardhats = []
        no_safety_vests = []
        no_masks = []

        for detection in detections:

            if detection.class_name == "Person":
                persons.append(detection)

            elif detection.class_name == "Hardhat":
                hardhats.append(detection)

            elif detection.class_name == "Safety Vest":
                safety_vests.append(detection)

            elif detection.class_name == "Mask":
                masks.append(detection)

            elif detection.class_name == "NO-Hardhat":
                no_hardhats.append(detection)

            elif detection.class_name == "NO-Safety Vest":
                no_safety_vests.append(detection)

            elif detection.class_name == "NO-Mask":
                no_masks.append(detection)

        print("\n========== PPE SUMMARY ==========")
        print(f"Persons           : {len(persons)}")
        print(f"Hardhats          : {len(hardhats)}")
        print(f"Safety Vests      : {len(safety_vests)}")
        print(f"Masks             : {len(masks)}")
        print(f"NO-Hardhat        : {len(no_hardhats)}")
        print(f"NO-Safety Vest    : {len(no_safety_vests)}")
        print(f"NO-Mask           : {len(no_masks)}")
        print("=================================\n")

        # -----------------------------
        # Build worker information
        # -----------------------------

        worker_status = []

        for person in persons:

            worker = {
                "track_id": person.track_id,
                "person": person,
                "helmet": self.find_helmet(person, hardhats),
                "no_helmet": self.find_no_helmet(person,no_hardhats),
                "mask": self.find_mask(person, masks),
                "no_mask": self.find_no_mask(person,no_masks),
                "vest": self.find_vest(person, safety_vests),
                "no_vest": self.find_no_vest(person,no_safety_vests),
                "status": "UNKNOWN"
            }

            worker["status"] = self.evaluate_worker_status(worker)

            print(
                f"Worker {worker['track_id']} | "
                f"Mask: {worker['mask']} | "
                f"NO-Mask: {worker['no_mask']} | "
                f"Status: {worker['status']}"
            )

            worker_status.append(worker)

        print("\n========== Worker PPE Status ==========")

        for worker in worker_status:

            print(
                f"Worker {worker['track_id']}\n "
                f"Helmet: {worker['helmet']}\n"
                f"Vest: {worker['vest']}\n"
                f"Mask: {worker['mask']}\n"
                f"Status: {worker['status']}\n"
            )

        print("=======================================\n")

        return worker_status