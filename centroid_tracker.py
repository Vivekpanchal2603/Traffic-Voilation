# centroid_tracker.py
import numpy as np
from scipy.spatial import distance as dist
from collections import OrderedDict

class CentroidTracker:
    def __init__(self, max_disappeared=30, max_distance=50):
        self.nextObjectID = 0
        self.objects = OrderedDict()      # objectID -> centroid
        self.bboxes = OrderedDict()       # objectID -> bounding box (x1,y1,x2,y2)
        self.disappeared = OrderedDict()  # objectID -> disappeared frames count
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid, bbox):
        self.objects[self.nextObjectID] = centroid
        self.bboxes[self.nextObjectID] = bbox
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):
        del self.objects[objectID]
        del self.bboxes[objectID]
        del self.disappeared[objectID]

    def update(self, rects):
        """
        rects: list of bounding boxes in format (x1,y1,x2,y2)
        returns: dict objectID -> bbox
        """
        if len(rects) == 0:
            to_deregister = []
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.max_disappeared:
                    to_deregister.append(objectID)
            for oid in to_deregister:
                self.deregister(oid)
            return self.bboxes

        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for (i, (x1, y1, x2, y2)) in enumerate(rects):
            cX = int((x1 + x2) / 2.0)
            cY = int((y1 + y2) / 2.0)
            input_centroids[i] = (cX, cY)

        if len(self.objects) == 0:
            for i in range(len(input_centroids)):
                self.register(input_centroids[i], rects[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())
            D = dist.cdist(np.array(objectCentroids), input_centroids)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            assignedRows, assignedCols = set(), set()
            for (row, col) in zip(rows, cols):
                if row in assignedRows or col in assignedCols:
                    continue
                if D[row, col] > self.max_distance:
                    continue
                objectID = objectIDs[row]
                self.objects[objectID] = input_centroids[col]
                self.bboxes[objectID] = rects[col]
                self.disappeared[objectID] = 0
                assignedRows.add(row)
                assignedCols.add(col)

            unassignedRows = set(range(D.shape[0])).difference(assignedRows)
            for row in unassignedRows:
                objectID = objectIDs[row]
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.max_disappeared:
                    self.deregister(objectID)

            unassignedCols = set(range(D.shape[1])).difference(assignedCols)
            for col in unassignedCols:
                self.register(input_centroids[col], rects[col])

        return self.bboxes
