H! welcome to our EyeTracking project. To run this on your local machine, please clone it: <code> git clone https://github.com/xginevra/GazeTrackingApp.git </code>

------

To run it, you'll need a virtual environment running Python 3.10:
use <code> py -3.10 -m venv .venv </code> to create the .venv folder
and then run .\.venv\Scripts\Activate.ps1 to activate the virtual environment.
The indicator (.venv) in your terminal tells you it worked! :) Then, confirm the python version 3.10 with <code> python --version </code> (it should show the version 3.10.11)
After that, install the dependencies: <code> pip install -r requirements.txt </code>


-----

Run then <code> python tracking_examplecopy.py </code>

Congrats!

------

First, the app will calibrate using your gaze. Follow the dot with your eyes. 
After reaching 25 points, it will stop calibrating and the stimulus is shown.
Look naturally where you would look at while seeing a person. 

-----

The app is supposed to record your gaze and save the gaze times for each region (eyes, nose, mouth, forehead, chin). 
It can give you a hint for autism diagnosis - but we are no doctors and this is just a student project. 

People with autism tend to not look directly into the eyes - rather everywhere around the face. This is what we are trying to record and show here.

-----


The Picture is potentially changeable. So is the time the picture is shown.
