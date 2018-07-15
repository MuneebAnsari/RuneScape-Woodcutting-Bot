import cv2
import pyautogui


class Inventory:

    def __init__(self, image):
        self.image = image
        self.logs = [log
                     for log in pyautogui.locateAllOnScreen('log1.png', confidence=0.9)
                     if 550 <= log[0] <= 740]
        self.num_logs = len(self.logs)
        self.capacity = 28

    def drop_all_logs(self):
        cv2.waitKey(4000)
        first_log_x, first_log_y = self.logs[0][0], self.logs[0][1]
        pyautogui.doubleClick(first_log_x, first_log_y)

        for log_coord in self.logs:
            x_coord, y_coord = pyautogui.center(log_coord)
            pyautogui.keyDown('shift')
            pyautogui.moveTo(x_coord, y_coord)
            pyautogui.click(x_coord, y_coord)
            pyautogui.keyUp('shift')
            self.num_logs -= 1
            print(self.num_logs)
            cv2.waitKey(500)
        self.logs = []

    def is_empty(self):
        return self.num_logs == 0

    def is_full(self):
        return self.num_logs == self.capacity

    def process_inventory(self):
        if len(self.logs) > 0:
            # log_coord = (left, top, width, height)
            first_log_x, first_log_y = self.logs[0][0], self.logs[0][1]
            for log_coord in self.logs:
                # print(log_coord)
                x, y, width, height = log_coord
                cv2.rectangle(self.image,
                              (x - first_log_x + 8, y - first_log_y + 5),
                              (x - first_log_x + width + 3, y - first_log_y + height),
                              (0, 255, 0), 2)
        return self.image

    def update(self):
        processed_inventory = self.process_inventory()
        cv2.imshow('inventory', cv2.cvtColor(processed_inventory, cv2.COLOR_BGR2RGB))
