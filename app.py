# Author: Mahdi Karami
# email: mahfi.karami.ca@gmail.com
# cellphone: (+1) 226-344-7809

# Description: 
'''
    The following code is a Python script that provides browser automation for a web application written by the author.
    The original web application address can be found on: "https://master--adorable-gelato-b069ba.netlify.app/",
    which help the user extract data points from an uploaded plot. The plot can be titlted, with non-perpendecular axes.
    The uploaded image should be located in the same directory as the python code. 
    Python Version: 3.10 or later
'''


# Import required libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dataclasses import dataclass
from typing import List
import time
import os
import re

# ----------------------------------------
# Define the ImageAutomation class
# ----------------------------------------
class ImageAutomation:
    def __init__(self, driver_path, web_address, originalImageObj):
        """
    Initialize class attributes.

    Args:
        driver_path (str): The path to the ChromeDriver executable.
        web_address (str): The web address of the application.
        originalImageObj (dict): A dictionary containing the original image information, including
                                 the pic_name, image_width, and original_axes_points.
        
        original_axes_points itself contains xAxis_point1, xAxis_point2, yAxis_point1, and yAxis_point2.
    """
        
        self.driver_path = driver_path
        self.web_address = web_address
        
        self.pic_name = originalImageObj.pic_name
        self.original_image_width = originalImageObj.image_width
        
        # Set the axes points
        self.original_axes_points = [
            (x := point.x, y := point.y) 
            for point in [originalImageObj.xAxis_point1, originalImageObj.xAxis_point2, 
                          originalImageObj.yAxis_point1, originalImageObj.yAxis_point2]
        ]
        
        
        # Set the axes values:
        self.xAxisValue_p1 = originalImageObj.xAxisValue_p1
        self.xAxisValue_p2 = originalImageObj.xAxisValue_p2
        self.yAxisValue_p1 = originalImageObj.yAxisValue_p1
        self.yAxisValue_p2 = originalImageObj.yAxisValue_p2
        
        
        # Set the coordinates of the points to be clicked
        self.clickedPoints = [
            (x := point.x, y := point.y) 
            for point in originalImageObj.clickedPoints
        ]
        
        
        self.driver = None
        self.image_element = None
        self.image_location = None
        self.image_size = None
        self.border_size = None

    # -------------------------------------------------------------
    # Method to upload an image using the provided file input element and image path
    # -------------------------------------------------------------
    def upload_image(self, file_input_element, pic_full_path):
        """
        Upload an image to the file input element.
        
        Args:
            file_input_element (WebElement): The file input element to upload the image to.
            pic_full_path (str): The full path of the image file to upload.
        """
        file_input_element.send_keys(pic_full_path)

    # -------------------------------------------------------------
    # Method to accept the alert that appears after uploading an image
    # -------------------------------------------------------------
    def accept_alert(self):
        """
        Accept the alert that appears after uploading an image.
        """
        alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        self.driver.switch_to.alert.accept()

    # -------------------------------------------------------------
    # Method to convert the original coordinates to the current coordinates based on the image dimensions and border size
    # -------------------------------------------------------------
    def convert_original_coor_to_current(self, original_coor, original_image_width, image_location, image_size, border_size):
        """
        Convert the original coordinates to the current coordinates.
        
        Args:
            original_coor (tuple): The original coordinates (x, y).
            original_image_width (int): The width of the original image.
            image_location (dict): The location of the image element.
            image_size (dict): The size of the image element.
            border_size (int): The size of the image border.

        Returns:
            x (float): The x-coordinate of the current position.
            y (float): The y-coordinate of the current position.
        """

        aspect_ratio = (image_size['width'] - 2 * border_size) / original_image_width
        X0 = original_coor[0]
        Y0 = original_coor[1]
        x = (X0 - 1) * aspect_ratio - image_size['width'] // 2 + 1 + border_size
        y = (Y0 - 1) * aspect_ratio - image_size['height'] // 2 + 1 + border_size
        return x, y

    # -------------------------------------------------------------
    # Method to find the image element, location, size, and border size
    # -------------------------------------------------------------
    def find_image_element(self):
        """
        Find the image element, location, size, and border size.
        """
        self.image_element = self.driver.find_element(By.CLASS_NAME, "uploaded-image")
        self.image_location = self.image_element.location
        self.image_size = self.image_element.size
        border_style = self.image_element.value_of_css_property("border")
        match = re.search(r'\b(\d+)px\b', border_style)
        if match:
            self.border_size = int(match.group(1))

    # -------------------------------------------------------------
    # Method to perform the actions on the image element, including moving to coordinates, clicking, and setting axis values
    # -------------------------------------------------------------
    def perform_actions(self):
        """
        Perform actions on the image element.
        """
        actions = ActionChains(self.driver)
        
        #Clicking on the coordinate points:
        for coor in self.original_axes_points:
            x, y = self.convert_original_coor_to_current(coor, self.original_image_width, self.image_location, self.image_size, self.border_size)
            actions.move_to_element(self.image_element).move_by_offset(x, y).click().perform()
        
        # Defining the axes values:
        
        x_axis_p2 = self.driver.find_element(By.ID, "x-axis-p2")
        x_axis_p2.clear()
        x_axis_p2.send_keys(f"{self.xAxisValue_p2}")

        y_axis_p2 = self.driver.find_element(By.ID, "y-axis-p2")
        y_axis_p2.clear()
        x_axis_p2.send_keys(f"{self.yAxisValue_p2}")
        
        #Clicking on the required points:
        for coor in self.clickedPoints:
            x, y = self.convert_original_coor_to_current(coor, self.original_image_width, self.image_location, self.image_size, self.border_size)
            actions.move_to_element(self.image_element).move_by_offset(x, y).click().perform()
        

    # -------------------------------------------------------------
    # Method to run the image automation process
    # -------------------------------------------------------------
    def run(self):
        """
        Run the image automation process.
        """
        self.driver = webdriver.Chrome(self.driver_path)
        self.driver.get(self.web_address)
        self.driver.maximize_window()
        time.sleep(1)

        # Find the file input element and upload the image
        file_input = self.driver.find_element(By.ID, "file-upload")
        current_dir = os.getcwd()
        pic_path = os.path.join(current_dir, self.pic_name)
        self.upload_image(file_input, pic_path)
        self.accept_alert()

        # Find the image element and perform the actions
        self.find_image_element()
        self.perform_actions()

        # Print the image location, size, and border size
        print("Location:", self.image_location)
        print("Size:", self.image_size)
        print("borderSize:", self.border_size)

        # Wait for the user to press Enter before closing the browser
        input("Press Enter to close the browser...")
        self.driver.quit()

@dataclass
class Point:
    x: float
    y: float

@dataclass
class UploadedImage:
    pic_name: str
    image_width: int
    xAxis_point1: Point
    xAxis_point2: Point
    yAxis_point1: Point
    yAxis_point2: Point
    
    xAxisValue_p1: float
    xAxisValue_p2: float
    yAxisValue_p1: float
    yAxisValue_p2: float
    
    clickedPoints : List[Point]
    
def initializeImageObj():
    pic_name = "1.jpg"
    image_width = 784
    xAxis_point1 = Point(127, 581)
    xAxis_point2 = Point(735, 400)
    yAxis_point1 = Point(262, 621)
    yAxis_point2 = Point(192, 241)
    
    xAxisValue_p1=0
    xAxisValue_p2=10
    yAxisValue_p1=0
    yAxisValue_p2=100
    
    clickedPoints = [
    Point(113,505),
    Point(99,429),
    Point(85,354),
    Point(234,469),
    Point(220,393),
    Point(206,318),
    Point(356,433),
    Point(342,357),
    Point(328,281)]
    
    originalImageObj = UploadedImage(pic_name=pic_name,
                        image_width = image_width,
                        xAxis_point1 = xAxis_point1,
                        xAxis_point2 = xAxis_point2,
                        yAxis_point1 = yAxis_point1,
                        yAxis_point2 = yAxis_point2,
                        xAxisValue_p1 = xAxisValue_p1,
                        xAxisValue_p2 = xAxisValue_p2,
                        yAxisValue_p1 = yAxisValue_p1,
                        yAxisValue_p2 = yAxisValue_p2,
                        clickedPoints = clickedPoints)
    
    return originalImageObj

# -------------------------------------------------------------
# Main function to create an instance of the ImageAutomation class and run the automation process
# -------------------------------------------------------------
if __name__ == "__main__":
    # Set the path to the ChromeDriver executable, web address, image name, original image width, and original axes points
    chrome_driver_path = "D:\z_softwareSource\browserDrivers\chrome\chromedriver.exe"
    
    web_address = "https://master--adorable-gelato-b069ba.netlify.app/"
    
    # Define uploaded Image
    originalImageObj = initializeImageObj()

    # Create an instance of the ImageAutomation class and run the automation process
    #image_automation = ImageAutomation(chrome_driver_path, web_address, pic_name, original_image_width, original_axes_points)
    image_automation = ImageAutomation(chrome_driver_path, web_address, originalImageObj)
    image_automation.run()

# -------------------------------------------------------------
# End of the script
# -------------------------------------------------------------





