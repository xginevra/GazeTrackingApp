
H! welcome to our EyeTracking project. To run this on your local machine, please clone it: <code> git clone https://github.com/xginevra/GazeTrackingApp.git </code>

# GazeTrackingApp
A Python-based eye tracking application that analyzes gaze patterns on facial regions. This research tool can provide insights into visual attention patterns, particularly useful for studying autism-related gaze behavior differences.

# Important Disclaimer
This application is for research and educational purposes only. While it may provide insights related to autism diagnosis patterns, we are not medical professionals, and this should never be used as a diagnostic tool. Always consult qualified healthcare providers for medical advice.

## 🔍 Project Background

Atypical gaze behavior — such as avoiding eye contact — is a well-documented trait in individuals with Autism Spectrum Disorder (ASD). Our tool uses webcam-based eye tracking and facial landmark detection to measure how long a user focuses on different facial regions.

This can support:
- Early research into visual attention differences  
- Supplementing social training tools  
- Gathering visual attention data in a controlled setup 



------

To run it, you'll need a virtual environment running Python 3.10:
use <code> py -3.10 -m venv .venv </code> to create the .venv folder
and then <br> run <code> .\\.venv\Scripts\Activate.ps1 </code> to activate the virtual environment.
The indicator (.venv) in your terminal tells you it worked! :) Then, confirm the python version 3.10 with <code> python --version </code> (it should show the version 3.10.11)
After that, install the dependencies: <code> pip install -r requirements.txt </code> <br> 

Make sure everything from requirements.txt is installed - if not, please manually install via the  pip install  command.

-----

Run then <code> python tracking.py </code>

Congrats!

------

First, the app will calibrate using your gaze. Follow the dot with your eyes. 
After reaching 25 points, it will stop calibrating and the stimulus is shown.
Look naturally where you would look at while seeing a person. 

------

# Important! 

Please keep approximately an arm distance from your screen.
Keep this distance as good as you can. Don't move around, don't lean anywhere.
Otherwise we can't guarantee that the gazeTracking application will work properly.
Thank you! :)

-----

The app is supposed to record your gaze and save the gaze times for each region (eyes, nose, mouth, forehead, chin). 
It can give you a hint for autism diagnosis - but we are no doctors and this is just a student project. 

People with autism tend to not look directly into the eyes - rather everywhere around the face. This is what we are trying to record and show here.

-----


The Picture is potentially changeable. So is the time the picture is shown.
